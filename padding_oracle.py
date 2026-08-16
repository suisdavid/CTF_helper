from pwn import *
import math,random
from Crypto.Util.number import *
p=remote("chals2.apoorvctf.xyz",13424)
p.recvuntil('"A": ',drop=True)
a=int(p.recvuntil(",",drop=True))
p.recvuntil('"S_0": ',drop=True)
s=int(p.recvuntil("}",drop=True))
p.recvuntil('"flag_ct": "',drop=True)
ct=bytes.fromhex(p.recvuntil('"',drop=True).decode())
print(a)
print(s)
print(ct)
iv=ct[:16]
iv_val=bytes_to_long(iv)
def math_test(d):
    p.sendline(f'{{"option": "math_test", "data": {d}}}')
    p.recvuntil('"result": ',drop=True)
    return int(p.recvuntil("}",drop=True))
def pad_test(msg):
    p.sendline(f'{{"option": "decrypt", "ct": "{msg.hex()}"}}')
    p.recvuntil('"oracle": "',drop=True)
    return p.recvuntil('"',drop=True)==b"padding_ok"
b=math_test(1)-a
mod=0
while mod==0 or isPrime(mod)==False:
    d=random.randint(0,1<<32)
    mod=math.gcd(mod,abs(a*d+b-math_test(d)))
print("MOD=",mod)
b%=mod
flag=b''
multiplier=pow((mod+1)//2,256,mod)
for i in range(3,4):
    lstxor=ct[i*16:(i+1)*16]
    message=ct[(i+1)*16:(i+2)*16]
    decrypted=[0]*16
    message_val=bytes_to_long(message)
    for j in range(1,17):
        for k in range(256):
            payload=b'\x00'*(16-j)+p8(j^k)
            for x in range(16-j+1,16):
                payload+=p8(j^decrypted[x])
            temp=(iv_val<<384)+(bytes_to_long(payload)<<128)+message_val
            s=(a*s+b)%mod
            padding=(s-temp)*multiplier%mod
            real_payload=iv+long_to_bytes(padding).rjust(16,b'\x00')+payload+message
            if pad_test(real_payload):
                decrypted[16-j]=k
                break
        temp=b''
        for k in range(16-j,16):
            temp+=p8(decrypted[k]^lstxor[k])
        print(temp)
    for k in range(16):
        flag+=p8(decrypted[k]^lstxor[k])
    print(flag)
            
