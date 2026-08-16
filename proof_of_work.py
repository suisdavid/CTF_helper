from pwn import *
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.number import *
p=remote("111.186.57.85",10086)
p.recvuntil("prefix = ",drop=True)
prefix=bytes.fromhex(p.recvuntil('\n',drop=True).decode())
print(prefix)
def proof_of_work(prefix):
    for i in range(128):
        tmp1=prefix+chr(i).encode()
        for j in range(128):
            tmp2=tmp1+chr(j).encode()
            for k in range(128):
                tmp3=tmp2+chr(k).encode()
                tmp=hashlib.sha256(tmp3).digest()
                if tmp.startswith(b'\xdd\xdd\xdd'):
                    return tmp3[len(prefix):]
    for i in range(128):
        tmp1=prefix+chr(i).encode()
        for j in range(128):
            tmp2=tmp1+chr(j).encode()
            for k in range(128):
                tmp3=tmp2+chr(k).encode()
                for l in range(128):
                    tmp4=tmp3+chr(l).encode()
                    tmp=hashlib.sha256(tmp4).digest()
                    if tmp.startswith(b'\xdd\xdd\xdd'):
                        return tmp4[len(prefix):]
                    
challenge=proof_of_work(prefix)
print(challenge)
p.sendlineafter("> ",challenge)
p.recvuntil("welcome to AESLAB\n",drop=True)
enc_flag=bytes.fromhex(p.recvuntil("\n",drop=True).decode())
print(enc_flag)

