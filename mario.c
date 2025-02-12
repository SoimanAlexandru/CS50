#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int height, i, j;
    do
        height = get_int("Height: \n");
    while (height < 1 || height > 8);
    for (i = 1; i <= height; i++)
    {
        for (j = 1; j <= height - i; j++)
            printf(" ");
        for (j = 0; j < i; j++)
            printf("#");
        printf("  ");
        for (j = 0; j < i; j++)
            printf("#");
        printf("\n");
    }
}
