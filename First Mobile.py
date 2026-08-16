b=[23, 22, 26, 26, 25, 25, 25, 26, 27, 28, 30, 30, 29, 30, 32, 32]
ans=[]
s=''
for i in range(16):
    for j in range(256):
        if (j+b[i])%61*2-i==j:
            ans.append(j)
for i in range(16):
    s+=chr(ans[i])
print(s)
