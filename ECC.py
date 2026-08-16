p=63079
A=56540
B=43233
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
        if Q.x==0 and Q.y==0:
            return Point(self.x,self.y)
        if self.x==0 and self.y==0:
            return Q
        if self.x!=Q.x:
            m=(self.y-Q.y)*inv(self.x-Q.x)%p
            x2=(m*m-self.x-Q.x)%p
            y2=(-self.y-m*(x2-self.x))%p
            return Point(x2,y2)
        elif self.y!=Q.y:
            return Point(0,0)
        else:
            m=(self.x*self.x*3+A)%p*inv(self.y*2%p)%p
            x2=(m*m-self.x-Q.x)%p
            y2=(-self.y-m*(x2-self.x))%p
            return Point(x2,y2)
    def mul(self,n):
        X=Point(0,0)
        base=Point(self.x,self.y)
        while n:
            if n&1:
                X=X.add(base)
            base=base.add(base)
            n>>=1
        return X
x=Point(48622,27709).add(Point(9460,13819))
print(x.x,x.y)

