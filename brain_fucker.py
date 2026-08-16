code=''
n=len(code)
print(n)
a=[0]*1000000
base=500000
idx=base
stk=[]
mat=[0]*n
cnt=[0]*n
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
i=0
l=r=base
mn=base
mx=base
ans=''
while i<n:
    each=code[i]
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
        ans+=chr(a[idx])
    elif each==',':
        a[idx]=ord(input("输入字符:")[0])
    elif each=='[':
        if a[idx]==0:
            i=mat[i]
    elif each==']':
        if a[idx]!=0:
            i=mat[i]
    i+=1
        
print(ans)
