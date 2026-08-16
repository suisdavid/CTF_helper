s1=''
s2=''
with open("ans.out",'r') as f:
    s1=f.read()
with open("sample.out",'r') as f:
    s2=f.read()
print(s1==s2)
i=0
cnt=1
while s1[i]==s2[i]:
    if s1[i]=='\n':
        cnt+=1
    i+=1
print(i,cnt)
