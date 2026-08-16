import random
p=3564625681460390929881227635631045656663925422561280528974142079390139643508987899
x=38261089807612932187270844464172183203782906902660221667752197493367152208082348

def fastpow(base,pw):
    x=1
    while pw:
        if pw&1:
            x=x*base%p
        base=base*base%p
        pw//=2
    return x
    

def mul(x,y,v):
    return ((x[0]*y[0]+v*(x[1]*y[1]%p))%p,(x[0]*y[1]+x[1]*y[0])%p)


def fastpw(base,pw,v):
    x=(1,0)
    while pw:
        if pw&1:
            x=mul(x,base,v)
        base=mul(base,base,v)
        pw//=2
    return x

def get(l):
    ans=[]
    for a in l:
        r=random.randint(1,100)
        while fastpow(r*r+p-a,(p-1)//2)!=p-1:
            r=random.randint(1,100)
        v=r*r+p-a
        res=fastpw((r,1),(p+1)//2,v)
        ans.append(res[0])
        ans.append(p-res[0])
    return ans

ans=get([x])
for each in ans:
    assert(each**2%p==x)
print(ans)

