#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <limits.h>

void changeMin(int arr[], int n) {
    int min = INT_MAX;
    int min1 = INT_MAX;
    int min_i;
    int min1_i;
    int z;
    for (int i = 0; i < n; i++) {
        if (arr[i] < min){
            min_i = i;
            min = arr[i];
        }
    }
    for (int i = 0; i < n; i++) {
        if (arr[i] < min1 && arr[i] > min) {
            min1 = arr[i];
            min1_i = i;
        }
    }
    z = arr[min_i];
    arr[min_i] = arr[min1_i];
    arr[min1_i] = z;
}


int main(void) {
    int n;
    scanf("%d", &n);
    int zxc[n];
    for (int i = 0; i < n; i++) {
        scanf("%d", &zxc[i]);
    }
    changeMin(zxc, n);
    for (int i = 0; i < n; i++) {
        printf("%d ", zxc[i]);
    }
    return 0;
}