#include <cs50.h>
#include <stdio.h>
int length(long nr)
{
    int l = 0;
    while (nr)
    {
        nr = nr / 10;
        l++;
    }
    return l;
}

int first(long nr)
{
    while (nr > 9)
    {
        nr = nr / 10;
        if (nr == 34 || nr == 37 || nr == 51 || nr == 52 || nr == 53 || nr == 54 || nr == 55)
            break;
    }
    return nr;
}

int checksum(long nr)
{
    int x1 = 0, x2 = 0, x;
    while (nr)
    {
        x2++;
        x = nr % 10;
        if (x2 % 2 == 0)
        {
            x = x * 2;
            if (x > 9)
                x = x % 10 + 1;
        }
        x1 = x1 + x;
        nr = nr / 10;
    }
    return x1;
}

int main(void)
{
    long nr;
    int l, f, x = 0;
    do
    {
        nr = get_long("Number: ");
    }
    while (nr < 0);
    if (checksum(nr) % 10 == 0)
    {
        l = length(nr);
        f = first(nr);
        if (l == 15 && (f == 34 || f == 37))
            x = 1;
        else if (l == 16 && (f == 51 || f == 52 || f == 53 || f == 54 || f == 55))
            x = 2;
        else if ((l == 13 || l == 16) && f == 4)
            x = 3;
    }
    if (x == 1)
        printf("AMEX\n");
    else if (x == 2)
        printf("MASTERCARD\n");
    else if (x == 3)
        printf("VISA\n");
    else if (x == 0)
        printf("INVALID\n");
}
