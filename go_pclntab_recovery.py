from pathlib import Path
import struct

data = Path("checker").read_bytes()

# 这个 Go PE 的 .text 虚拟地址
TEXT_VA = 0x140001000

# 搜 Go pclntab magic
magic = b"\xf1\xff\xff\xff\x00\x00\x01\x08"

candidates = []
start = 0
while True:
    off = data.find(magic, start)
    if off == -1:
        break
    candidates.append(off)
    start = off + 1

def cstr(off):
    end = data.find(b"\x00", off)
    return data[off:end].decode("utf-8", errors="replace")

for base in candidates:
    try:
        fields = struct.unpack_from("<I4BQQQQQQQQ", data, base)
    except struct.error:
        continue

    (
        magic_val,
        pad1,
        pad2,
        min_lc,
        ptr_size,
        nfunc,
        nfiles,
        text_start,
        funcname_off,
        cu_off,
        filetab_off,
        pctab_off,
        pcln_off,
    ) = fields

    # 简单校验：函数名表开头一般能读到 internal/abi...
    name_base = base + funcname_off
    if not data[name_base:name_base + 16].startswith(b"internal/"):
        continue

    print(f"[+] pclntab file offset = {hex(base)}")
    print(f"[+] nfunc = {nfunc}")
    print(f"[+] funcname_off = {hex(funcname_off)}")
    print(f"[+] pcln_off = {hex(pcln_off)}")

    for i in range(nfunc):
        entry_off, func_off = struct.unpack_from("<II", data, base + pcln_off + i * 8)

        # 这个文件里 func_off 是相对 base + pcln_off 的偏移
        func_struct = base + pcln_off + func_off

        entry_check, name_off = struct.unpack_from("<Ii", data, func_struct)
        name = cstr(base + funcname_off + name_off)

        if name.startswith("main."):
            va = TEXT_VA + entry_off
            print(f"{hex(va)}  {name}")

    break
