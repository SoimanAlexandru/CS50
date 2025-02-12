#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int cents, coins = 0;
    do
    {
        cents = get_int("Change owed: ");
    }
    while (cents < 0);
    while (cents >= 25)
    {
        cents = cents - 25;
        coins++;
    }
    while (cents >= 10)
    {
        cents = cents - 10;
        coins++;
    }
    while (cents >= 5)
    {
        cents = cents - 5;
        coins++;
    }
    while (cents >= 1)
    {
        cents = cents - 1;
        coins++;
    }
    printf("%d\n", coins);
}
