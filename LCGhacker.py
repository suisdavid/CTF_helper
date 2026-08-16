from pwn import *
import hashlib
from Crypto.Util.number import *
import sys,itertools,string,math
sys.setrecursionlimit(10000000)
p=remote("111.186.57.85",10087)
p.recvuntil("prefix = ",drop=True)
prefix=bytes.fromhex(p.recv(16).decode())
print(prefix)
def search(prefix):
    alphabet=string.printable
    for L in range(1,5):
        print(L)
        for seq in itertools.product(alphabet,repeat=L):
            challenge = ''.join(seq)
            digest = hashlib.sha256(prefix + challenge.encode()).digest()
            if digest.startswith(b'\xdd\xdd\xdd'):
                return challenge
ans=search(prefix)
print(ans)
p.sendlineafter("> ",ans)
def solve0():
    print("Welcome to challenge 0")
    p.recvuntil("challenge 0:\n",drop=True)
    P=int(p.recvline())
    A=int(p.recvline())
    B=int(p.recvline())
    S=int(p.recvline())
    print(P,A,B,S)
    for i in range(3):
        S=(S*A+B)%P
        p.sendline(str(S))
def solve1():
    print("Welcome to challenge 1")
    p.recvuntil("challenge 1:\n",drop=True)
    P=int(p.recvline())
    A=int(p.recvline())
    S0=int(p.recvline())
    S=int(p.recvline())
    print(P,A,S0,S)
    B=(S-S0*A)%P
    for i in range(3):
        S=(S*A+B)%P
        p.sendline(str(S))

def solve2():
    print("Welcome to challenge 2")
    p.recvuntil("challenge 2:\n",drop=True)
    P=int(p.recvline())
    S0=int(p.recvline())
    S1=int(p.recvline())
    S=int(p.recvline())
    print(P,S0,S1,S)
    A=(S-S1)*pow(S1-S0,-1,P)%P
    B=(S-S1*A)%P
    for i in range(3):
        S=(S*A+B)%P
        p.sendline(str(S))

def solve3():
    print("Welcome to challenge 3")
    p.recvuntil("challenge 3:\n",drop=True)
    s=[]
    b=[]
    n=6
    for i in range(n):
        s.append(int(p.recvline()))
    print(s)
    S=s[-1]
    for i in range(n-1):
        b.append(s[i+1]-s[i])  
    x=[]
    P=0
    for i in range(n-3):
        for j in range(i+2,n-1):
            x.append(abs(b[i]*b[j]-b[(i+j)//2]*b[(i+j+1)//2]))
    for each in x:
        P=math.gcd(each,P)
    print(P)
    A=(s[2]-s[1])*pow(s[1]-s[0],-1,P)%P
    B=(s[2]-s[1]*A)%P
    for i in range(3):
        S=(S*A+B)%P
        p.sendline(str(S))
solve0()
solve1()
solve2()
solve3()
print(p.recv())
print(p.recv())
