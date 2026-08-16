a=[0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0]
n=10
m=10
for i in range(n):
    s=''
    for j in range(m):
        s+=str(a[i*m+j])
    print(s)
ans=''
ops=['a','d','s','w']
opx=[0,0,1,-1]
opy=[-1,1,0,0]
vis=[0]*(n*m)
def dfs(x,y,s):
    global ans
    if x>=n or y>=m or x<0 or y<0 or a[x*m+y]==1 or vis[x*m+y]==1:
        return 0
    vis[x*m+y]=1
    if x==n-1 and y==m-1:
        ans=s
        return 1
    for i in range(4):
        if dfs(x+opx[i],y+opy[i],s+ops[i]):
            return 1
dfs(0,0,'')
print(ans)
