import galois
GF=galois.GF(2)
a=[0 for i in range(129)]
a[128]=a[127]=a[126]=a[121]=a[0]=1
p=galois.Poly(a,field=GF)
a=b"CryptoHack"
p1=bytes.fromhex("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
p2=bytes.fromhex("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
              
def get(x):
    l=[]
    for i in range(128):
        l.append((x>>i)&1)
    l.append(0)
    l.reverse()
    return galois.Poly(l,field=GF)
def G(x):
    l=[0 for i in range(129)]
    l[x]=1
    l.reverse()
    return galois.Poly(l,field=GF)
C1=get(0xff44b60bbc7df806118a203d0a339f38)
C2=get(0xee55a71aad6ce917009b312c1b228e29)
T1=get(0x767997e196b47446d7477685d6ca30af)
T2=get(0x8f0ac0ed50e8c37e1a172c93674e70bc)
L1=L2=get(0x00000000000000800000000000000080)
while len(a)%16:
    a+=bytes.fromhex('00')


g=(C1+C2)*G(2)%p+(L1+L2)*G(1)%p+(T1+T2)
print(g.roots())
