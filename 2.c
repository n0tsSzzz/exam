#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>


float sumFoo(int n) {
    float sum = 1.0, zxc;
    for (int i = 3; i <= n; i++) {
        zxc = ((float)1 / ((i) * (i - 1)));
        sum += zxc;
    }

    return sum;
}


int main(void) {
    int n;
    scanf("%d", &n);
    printf("%f", sumFoo(n));

    return 0;
}