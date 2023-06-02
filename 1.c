#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>


int isPalindrom(int num) {
    int n = num, rev = 0;
 
    while (n)
    {
        int r = n % 10;
        rev = rev * 10 + r;
        n = n / 10;
    }

    return (num == rev);
}

int main(void) {
    int n;
    scanf("%d", &n);
    printf("%d", isPalindrom(n));

    return 0;
}