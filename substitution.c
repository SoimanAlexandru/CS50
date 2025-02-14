#include <cs50.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

int validkey(string key)
{
    if (strlen(key) != 26)
    {
        printf("Key must contain 26 characters.\n");
        return 1;
    }
    int index, i, letters[26] = {0};
    for (i = 0; i < 26; i++)
    {
        if (isalpha(key[i]) == 0)
        {
            printf("Key must only contain alphabetic characters.\n");
            return 1;
        }
        index = toupper(key[i]) - 'A';
        if (letters[index])
        {
            printf("Key must not contain repeated characters.\n");
            return 1;
        }
        letters[index] = 1;
    }
    return 0;
}

string substitution(string text, string key)
{
    int i;
    char *c = text;
    for (i = 0; text[i] != '\0'; i++)
    {
        if (isalpha(text[i]))
        {
            if (isupper(text[i]))
                c[i] = toupper(key[text[i] - 'A']);
            else
                c[i] = tolower(key[text[i] - 'a']);
        }
    }
    return c;
}

int main(int argc, string argv[])
{
    if (argc != 2)
    {
        printf("Usage: ./substitution key\n");
        return 1;
    }
    if (validkey(argv[1]) == 0)
    {
        string plaintext = get_string("plaintext:  ");
        string ciphertext = substitution(plaintext, argv[1]);
        printf("ciphertext: %s\n", ciphertext);
        return 0;
    }
    else
        return 1;
}
