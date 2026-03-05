#include <stdio.h>
#include <stdlib.h>

long ackermann(int m, int n) {
    if(m==0) return n+1;
    if(n==0) return ackermann(m-1,1);
    return ackermann(m-1,ackermann(m,n-1));
}

int main(int argc, char *argv[]) {
    int m = 3, n = 2;
    printf("%ld \n",ackermann(m,n));
    return 0;
}