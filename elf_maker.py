import struct

base = 0x400000
b = bytearray(112)

# ELF64 标识
b[:16] = b'\x7fELF' + bytes([2, 1, 1, 0]) + bytes(8)

# e_type = ET_EXEC，e_machine = EM_X86_64，e_version = 1
struct.pack_into('<HHI', b, 16, 2, 62, 1)

# 入口：基址 + 文件偏移 40
struct.pack_into('<Q', b, 24, base + 40)

# 程序头从偏移 56 开始，与 ELF 头重叠 8 字节
struct.pack_into('<Q', b, 32, 56)

# e_ehsize = 64
# e_phentsize = 56
# e_phnum = 1，同时令 p_type = PT_LOAD
# e_shentsize = 0
# e_shnum = 5，同时令 p_flags = R|X
# e_shstrndx = 0
struct.pack_into('<HHHHHH', b, 52, 64, 56, 1, 0, 5, 0)

# p_offset = 0，p_vaddr = 0x400000
struct.pack_into('<QQ', b, 64, 0, base)

# 文件偏移 40，放在 e_shoff/e_flags 中：
#
# mov esi, 0x400000    ; write 的缓冲区地址
# inc edi              ; fd = 1
# mov al, 1            ; SYS_write
# nop
# jmp 文件偏移 80
b[40:52] = bytes.fromhex(
    'be 00 00 40 00'    # mov esi, 0x400000
    'ff c7'             # inc edi
    'b0 01'             # mov al, 1
    '90'                # nop
    'eb 1c'             # jmp 0x50
)

# 文件偏移 80，放在 p_paddr 中：
#
# mov dl, 0x70         ; 长度 112，入口时 rdx 的高位为 0
# syscall              ; write(1, 0x400000, 112)
# mov al, 60           ; SYS_exit
# jmp 文件偏移 96
b[80:88] = bytes.fromhex(
    'b2 70'
    '0f 05'
    'b0 3c'
    'eb 08'
)

# p_filesz = 112
struct.pack_into('<Q', b, 88, 112)

# 文件偏移 96：jmp 文件偏移 104
# 同时 p_memsz 的数值为 0x06eb = 1771，大于 p_filesz
b[96:104] = bytes.fromhex(
    'eb 06 00 00 00 00 00 00'
)

# 文件偏移 104，放在 p_align 中：
#
# xor edi, edi         ; 退出状态 0
# syscall              ; exit(0)
b[104:112] = bytes.fromhex(
    '31 ff 0f 05 00 00 00 00'
)

assert len(b) == 112

with open('tiny112', 'wb') as f:
    f.write(b)

print('generated tiny112:', len(b), 'bytes')