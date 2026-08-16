with open ("flag.txt",'r') as f:
    key1=f.read()
with open("lemur.txt",'r') as f:
    key2=f.read()

res1=''
res2=''
for each in key1:
    if (each>='0' and each<='9') or (each>='A' and each<='F'):
        res1+=each
for each in key2:
    if (each>='0' and each<='9') or (each>='A' and each<='F'):
        res2+=each

