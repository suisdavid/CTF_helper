S=[]
for i in range(256):
    S.append(i)
key=b'a'*16
enc=bytes.fromhex("58d9ea7139eeed78711d9e556d70f0946c08d6a562b27f485004ca1f25c8888fc50198faf52c")
def KSA(T):
    j=0
    for i in range(256):
        j=(j+S[i]+T[i%16])%256
        S[i],S[j]=S[j],S[i]
def PRGA(enc):
    i=0
    j=0
    ans=""
    for _ in range(38):
        i+=1
        j=(j+S[i])%256
        S[i],S[j]=S[j],S[i]
        t=S[(S[i]+S[j])%256]
        ans+=chr(enc[_]^t)
    return ans
KSA(key)
print(PRGA(enc))
