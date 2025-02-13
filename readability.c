#include <cs50.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

int count_letters(string text)
{
    int i, count = 0, l = strlen(text);
    for (i = 0; i < l; i++)
        if (isalpha(text[i]))
            count++;
    return count;
}

int count_words(string text)
{
    int i, count = 1, l = strlen(text);
    for (i = 0; i < l; i++)
        if (text[i] == ' ' && isalpha(text[i + 1]))
            count++;
    return count;
}

int count_sentences(string text)
{
    int i, count = 0, l = strlen(text);
    for (i = 0; i < l; i++)
        if (text[i] == '.' || text[i] == '!' || text[i] == '?' || text[i] == ':')
            count++;
    return count;
}

int main(void)
{
    string text = get_string("Text: ");
    int letters = count_letters(text);
    int words = count_words(text);
    int sentences = count_sentences(text);
    float index, L, S;
    L = (letters / (float) words) * 100;
    S = (sentences / (float) words) * 100;
    index = 0.0588 * L - 0.296 * S - 15.8;
    index = round(index);
    if (index < 1)
        printf("Before Grade 1\n");
    else if (index >= 1 && index <= 16)
        printf("Grade %d\n", (int) index);
    else
        printf("Grade 16+\n");
}
