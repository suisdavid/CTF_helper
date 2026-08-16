import random
def random_shuffler(a,seed):
    random.seed(seed)
    random.shuffle(a)
    return a
seed=668598
t=['11101111010111110100111111111', '10111111101011111111100111110', '01010101111110011011101100101', '11100010000111001000100110111', '01000010000111110111001011011', '01010101010101100000001101011', '01111001001110100000101110101']
flg="flag{"
p=[]
mp=[]
s=[]
ans=[]
ss=''
for i in range(7):
    x=[]
    res=[]
    a=t[i]
    for j in range(29):
        x.append(j)
        res.append('0')
    x=random_shuffler(x,seed)
    for j in range(29):
        res[x[j]]=a[j]
    ans.append(res)
for i in range(29):
    x=0
    for j in range(7):
        x=x*2+ord(ans[j][i])-ord('0')
    ss+=chr(x)

print(ss)

            #', '10111111101011111111100111110', '01010101111110011011101100101', '11100010000111001000100110111', '01000010000111110111001011011', '01010101010101100000001101011', '01111001001110100000101110101']
