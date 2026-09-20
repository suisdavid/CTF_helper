from pwn import *
import string
S=string.ascii_letters+string.digits+"{}_@!?"
p=remote("wily-courier.picoctf.net",56605)
flag='picoCTF{'
def query(payload):
    p.sendlineafter("encrypted: ",payload)
    p.recvline()
    p.recvline()
    return int(p.recvline())
lst=query(flag)
while flag[-1]!='}':
    for s in S:
        x=query(flag+s)
        if x<=lst:
            flag+=s
            lst=x
            break
    print(flag)
