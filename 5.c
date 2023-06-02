#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

struct Car{
    char* brand;
	char* model;
    int price;
};

int sumCarPrice(struct Car cars[], int n) {
    int sum = 0; 
    for (int i = 0; i < n; ++i) {
        sum += cars[i].price; 
    }
    return sum;
}

int main(void) {
    struct Car cars[3] = {{"amg", "amg", 8},
                         {"bmw", "bmw", 16},
                         {"lada", "lada", 25}};
    printf("%d", sumCarPrice(cars, 3));
    return 0;
}