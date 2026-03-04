#include <stdio.h>
#include <stdlib.h>

long ackermann(int m, int n) {
    if(m==0) return n+1;
    if(n==0) return ackermann(m-1,1);
    return ackermann(m-1,ackermann(m,n-1));
}

int main(int argc, char *argv[]) {
    int m = 4;
    int n = 1;
    long r = ackermann(m,n);
    printf("%ld \n",r);
    return 0;
}