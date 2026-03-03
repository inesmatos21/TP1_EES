#include <stdio.h>
#include <stdlib.h>

long fib(int n) {
    if (n <= 1)
        return n;
    else
        return fib(n - 1) + fib(n - 2);
}

int main(int argc, char *argv[]) {
    int n = 42;
    long r = fib(n);

    return 0;
}