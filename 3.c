#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

int main(void) {
    int n, sum = 0, val = 0;
    scanf("%d", &n);
    while (n != 0) {
        if (n % 10 == 3) {
            sum += n;
            val++;
        }
        scanf("%d", &n);
    }
    printf("%f", (float)sum / val);
    
    return 0;
}