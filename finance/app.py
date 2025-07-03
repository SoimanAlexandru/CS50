import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]

    # Group transactions by stock to get total shares
    stocks = db.execute("""
        SELECT symbol, SUM(shares) as total_shares
        FROM transactions
        WHERE user_id = ?
        GROUP BY symbol
        HAVING total_shares > 0
    """, user_id)

    portfolio = []
    total_value = 0

    for stock in stocks:
        quote = lookup(stock["symbol"])
        current_price = quote["price"]
        total = stock["total_shares"] * current_price
        total_value += total

        portfolio.append({
            "symbol": stock["symbol"],
            "name": quote["name"],
            "shares": stock["total_shares"],
            "price": current_price,
            "total": total
        })

    # Get user's remaining cash
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    total_value += cash

    return render_template("index.html", portfolio=portfolio, cash=cash, total=total_value)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("must provide stock symbol")
        if not shares:
            return apology("must provide number of shares")

        try:
            shares = int(shares)
            if shares <= 0:
                return apology("must be a positive integer")
        except ValueError:
            return apology("shares must be an integer")

        stock = lookup(symbol.upper())
        if stock is None:
            return apology("invalid stock symbol")

        total_cost = stock["price"] * shares
        user_id = session["user_id"]

        # Check user's available cash
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        if user_cash < total_cost:
            return apology("not enough cash")

        # Deduct from user's cash
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_cost, user_id)

        # Record transaction
        db.execute("""
            INSERT INTO transactions (user_id, symbol, shares, price)
            VALUES (?, ?, ?, ?)
        """, user_id, stock["symbol"], shares, stock["price"])

        flash("Stock purchased successfully!")
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]

    transactions = db.execute("""
        SELECT symbol, shares, price, timestamp
        FROM transactions
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, user_id)

    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")

        if not symbol:
            return apology("must provide symbol")

        stock = lookup(symbol.upper())
        if stock is None:
            return apology("invalid symbol")

        return render_template("quoted.html", stock=stock)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate input
        if not username:
            return apology("must provide username")
        if not password:
            return apology("must provide password")
        if password != confirmation:
            return apology("passwords must match")

        # Check if username already exists
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) > 0:
            return apology("username already taken")

        # Insert new user into users table
        hash_pw = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_pw)

        # Log the user in automatically after registration
        user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
        session["user_id"] = user_id

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("must provide stock symbol")

        try:
            shares = int(shares)
            if shares <= 0:
                return apology("must be a positive integer")
        except ValueError:
            return apology("shares must be a number")

        # Check total shares the user owns of the symbol
        result = db.execute("""
            SELECT SUM(shares) as total_shares FROM transactions
            WHERE user_id = ? AND symbol = ?
            GROUP BY symbol
        """, user_id, symbol.upper())

        if len(result) != 1 or result[0]["total_shares"] < shares:
            return apology("not enough shares to sell")

        # Lookup current stock price
        stock = lookup(symbol.upper())
        if stock is None:
            return apology("invalid stock symbol")

        # Calculate total sale value
        total_value = stock["price"] * shares

        # Update user cash
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total_value, user_id)

        # Insert negative transaction (to track sale)
        db.execute("""
            INSERT INTO transactions (user_id, symbol, shares, price)
            VALUES (?, ?, ?, ?)
        """, user_id, symbol.upper(), -shares, stock["price"])

        flash("Stock sold successfully!")
        return redirect("/")

    else:
        # For the dropdown: get all symbols the user currently owns with positive shares
        rows = db.execute("""
            SELECT symbol FROM transactions
            WHERE user_id = ?
            GROUP BY symbol
            HAVING SUM(shares) > 0
        """, user_id)

        symbols = [row["symbol"] for row in rows]
        return render_template("sell.html", symbols=symbols)
