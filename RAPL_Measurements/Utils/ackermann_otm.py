import sys

sys.setrecursionlimit(10**7)

def ackermann(m,n,dici):
    dici_keys = dici.keys()
    if (m,n) in dici_keys:
        return [dici[(m,n)],dici]
    elif(m==0): 
        return [n+1,dici]
    elif(n==0): 
        result = ackermann(m-1,1,dici)[0]
        dici[(m,n)] = result
        return [result,dici]
    else:
        if (m,n-1) in dici_keys:
            p2 = dici[(m,n-1)]
        else:
            (p2,dici) = ackermann(m,n-1,dici)
        if (m-1,p2) in dici_keys:
            return [dici[(m-1,p2)],dici]
        else:
            (p1,dici) = ackermann(m-1,p2,dici)
            dici[(m-1,p2)] = p1
            return [p1,dici]


print(ackermann(4,1,{})[0])