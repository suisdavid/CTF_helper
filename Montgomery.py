p=(2**255)-19
A=486662
B=1
def fastpow(base,pw):
    x=1
    while pw:
        if pw&1:
            x=x*base%p
        base=base*base%p
        pw>>=1
    return x

def inv(x):
    return fastpow(x,p-2)

class Point:
    x=0
    y=0
    def __init__(self,x1,y1):
        self.x=x1
        self.y=y1
    def add(self,Q):
       k=((Q.y-self.y)*inv(Q.x-self.x))%p
       x3=(k**2)%p*B-A-self.x-Q.x
       x3%=p
       y3=k*(self.x*2+Q.x+A)%p-B*(k**3)%p-self.y
       y3%=p
       return Point(x3,y3)
    def mul(self,n):
        base=Point(self.x,self.y)
        X=base
        n-=1
        while n:
            if n&1:
                X=X.add(base)
            base=base.add(base)
            n>>=1
        return X
    def check(self):
        return (self.y**2)*B%p==((self.x**3)+(self.x**2)*A+self.x)%p
        
G=Point(9,43114425171068552920764898935933967039370386198203806730763910166200978582548)
assert((G.y**2)*B%p==((G.x**3)+(G.x**2)*A+G.x)%p)
k=0x1337c0decafe
print(G.mul(k).x)
