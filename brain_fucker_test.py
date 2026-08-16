import string
S=string.ascii_letters+string.digits+'{}_'
with open("bf.bf") as f:
    code=f.read()
n=len(code)
print(n)
stk=[]
mat=[0]*n
cnt=[0]*n
a=[0]*1000000
base=500000
mn=mx=base
key_list=[944]
tmp=1
for i in range(len(code)):
    if code[i]=='\n':
        tmp+=1
    cnt[i]=tmp
    if code[i]=='[':
        stk.append(i)
    elif code[i]==']':
        j=stk.pop()
        mat[i]=j
        mat[j]=i
def get_status(i,idx):
    return (mn,mx,a[mn:mx+1],i,idx)

def solve(payload,target):
    global mn,mx
    for j in range(mn,mx+1):
        a[j]=0
    t=0
    payload=payload+'a'*(30-len(payload))
    mn=base
    mx=base
    i=0
    idx=base
    output=''
    flg=0
    lst=0
    hsh=[]
    while i<n and len(hsh)<500:
        each=code[i]
        if t>=23 and cnt[i]>=581 and cnt[i]<=660 and code[i:i+25]=='<[-<->] +<[>-<[-]]>[-<+>]':
            print(cnt[i],a[mn:mx+1])
        lst=cnt[i]
        if each=='>':
            idx+=1
            mx=max(mx,idx)
        elif each=='<':
            idx-=1
            mn=min(mn,idx)
        elif each=='+':
            a[idx]=(a[idx]+1)%256
        elif each=='-':
            a[idx]=(a[idx]-1)%256
        elif each=='.':
            output+=chr(a[idx])
            if "Sorry" in output:
                return 0
        elif each==',':
            a[idx]=ord(payload[t])
            t+=1
        elif each=='[':
            if a[idx]==0:
                i=mat[i]
        elif each==']':
            if a[idx]!=0:
                i=mat[i]
        i+=1
    return hsh
flag='CTF{y0u_R'
target=0
lsthsh=[]
while flag[-1]!='}':
    for each in S:
        hsh=solve(flag+each,target)
        print(each,hsh)
        if lsthsh!=[] and hsh!=lsthsh:
            print(hsh,lsthsh)
            flag+=each
            target+=1
            print(flag)
            break
        lsthsh=hsh
        
        
