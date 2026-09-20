#!/usr/bin/env python3
"""
JITFP Solver - Time-synced sampling.
The JIT service patches check function comparison bytes just-in-time,
one per second, synced with the binary's check loop.
We sample at each second to capture the correct character for each position.
"""
import os, struct, time, subprocess, sys, select

dword_4020 = [
    30, 22, 11, 32, 25, 4, 9, 7, 19, 23, 5, 26, 18, 27, 16, 1,
    8, 15, 2, 14, 3, 13, 24, 21, 12, 17, 6, 10, 29, 28, 20, 31, 0
]

def log(msg):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()

def read_mem(pid, addr, size):
    with open(f"/proc/{pid}/mem", "rb") as mem:
        mem.seek(addr)
        return mem.read(size)

def get_base(pid):
    with open(f"/proc/{pid}/maps", "r") as f:
        for line in f:
            if "ad7e550b" in line:
                return int(line.split("-")[0], 16)
    return None

def read_cmp_byte(pid, func_addr):
    """Read the comparison byte from a check function."""
    code = read_mem(pid, func_addr, 16)
    for j in range(len(code) - 3):
        if code[j] == 0x80 and code[j+1] == 0x7d and code[j+2] == 0xfc:
            return code[j+3]
    return None

dummy_flag = "picoCTF{MOHAMEDISTHEGOATHEHEHEHE}"
log(f"Starting binary with faake flag ({len(dummy_flag)} chars)")

proc = subprocess.Popen(
    ["./ad7e550b", dummy_flag],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
pid = proc.pid
log(f"PID: {pid}")

time.sleep(0.5)

base = get_base(pid)
if base is None:
    log("No base addr!")
    proc.kill()
    sys.exit(1)
log(f"Base: {hex(base)}")

# First, we need to compare on-disk vs runtime code
log("\n=== Comparing disk vs runtime ===")
with open("./ad7e550b", "rb") as f:
    disk = f.read()

# Compare check functions region (0x11D5 - 0x1932)
try:
    rt_checks = read_mem(pid, base + 0x11D5, 0x1932 - 0x11D5)
    disk_checks = disk[0x11D5:0x1932]
    check_diffs = [(0x11D5+i, disk_checks[i], rt_checks[i])
                   for i in range(len(disk_checks)) if disk_checks[i] != rt_checks[i]]
    if check_diffs:
        log(f"Check functions: {len(check_diffs)} bytes modified!")
        for addr, d, r in check_diffs[:20]:
            log(f"  {hex(addr)}: disk=0x{d:02x} runtime=0x{r:02x}")
    else:
        log("Check functions: identical")
except Exception as e:
    log(f"Error comparing checks: {e}")

# Compare main function (0x1982 - 0x1B1B)
try:
    rt_main = read_mem(pid, base + 0x1982, 0x1B1B - 0x1982)
    disk_main = disk[0x1982:0x1B1B]
    main_diffs = [(0x1982+i, disk_main[i], rt_main[i])
                  for i in range(len(disk_main)) if disk_main[i] != rt_main[i]]
    if main_diffs:
        log(f"Main function: {len(main_diffs)} bytes modified!")
        for addr, d, r in main_diffs[:20]:
            log(f"  {hex(addr)}: disk=0x{d:02x} runtime=0x{r:02x}")
    else:
        log("Main function: identical")
except Exception as e:
    log(f"Error comparing main: {e}")

# Compare permutation table
try:
    rt_perm = read_mem(pid, base + 0x4020, 33 * 4)
    disk_perm = disk[0x3020:0x3020 + 33*4]  # file offset = VA - 0x1000 for data segment
    # Actually data is at file offset 0x3000 for VA 0x4000, so 0x4020 -> file 0x3020
    if rt_perm != disk_perm:
        log("Permutation table: MODIFIED!")
        for i in range(33):
            rv = struct.unpack("<I", rt_perm[i*4:(i+1)*4])[0]
            dv = struct.unpack("<I", disk_perm[i*4:(i+1)*4])[0]
            if rv != dv:
                log(f"  [{i}] disk={dv} runtime={rv}")
    else:
        log("Permutation table: identical")
except Exception as e:
    log(f"Error comparing perm: {e}")

log("\n=== Initial function pointer table ===")
table_data = read_mem(pid, base + 0x4120, 33 * 8)
initial_ptrs = []
for i in range(33):
    ptr = struct.unpack("<Q", table_data[i*8:(i+1)*8])[0]
    initial_ptrs.append(ptr)
    if ptr:
        off = ptr - base
        cb = read_cmp_byte(pid, ptr)
        log(f"  [{i:2d}] off={hex(off)} cmp={hex(cb) if cb else '?'} ('{chr(cb) if cb else '?'}')")
    else:
        log(f"  [{i:2d}] NULL")

# Now do time-synced sampling over the execution
# The binary timeline:
# t~0: banner prints (32 '=' + 'v\n')
# t~1: sleep(1) ends, check j=0
# t~2: sleep(1) ends, check j=1
# ...
# t~33: sleep(1) ends, check j=32
# t~34: null check

log("\n=== Time-synced sampling (every 0.5s for 40s) ===")
start_time = time.time()
samples = []

for tick in range(80):
    t = time.time() - start_time

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        log(f"  Process exited at t={t:.1f}")
        break

    try:
        # Read table
        td = read_mem(pid, base + 0x4120, 33 * 8)
        ptrs = []
        for i in range(33):
            ptrs.append(struct.unpack("<Q", td[i*8:(i+1)*8])[0])

        # Read comparison bytes from each function
        cmp_bytes = []
        for i in range(33):
            if ptrs[i]:
                cb = read_cmp_byte(pid, ptrs[i])
                cmp_bytes.append(cb)
            else:
                cmp_bytes.append(None)

        samples.append((t, ptrs, cmp_bytes))

        # Log changes from initial state
        changes = []
        for i in range(33):
            if ptrs[i] != initial_ptrs[i]:
                changes.append(f"tbl[{i}]")
            if cmp_bytes[i] and initial_ptrs[i]:
                init_cb = read_cmp_byte(pid, initial_ptrs[i]) if tick == 0 else None
                # Just track the current comparison byte

        # Build current flag from this snapshot
        flag_now = []
        for j in range(33):
            idx = dword_4020[j]
            if idx < len(ptrs) and ptrs[idx]:
                cb = cmp_bytes[idx]
                if cb:
                    flag_now.append(chr(cb))
                else:
                    flag_now.append("?")
            else:
                flag_now.append("?")

        flag_str = "".join(flag_now)
        if tick % 2 == 0:
            log(f"  t={t:5.1f} flag={flag_str}")
    except Exception as e:
        log(f"  t={t:.1f} error: {e}")

    time.sleep(0.5)

log("\n=== Flag reconstruction ===")
final_flag = []
for j in range(33):
    target_time = j + 1.5
    best_sample = None
    best_dt = float('inf')
    for t, ptrs, cmp_bytes in samples:
        dt = abs(t - target_time)
        if dt < best_dt:
            best_dt = dt
            best_sample = (t, ptrs, cmp_bytes)

    if best_sample:
        t, ptrs, cmp_bytes = best_sample
        idx = dword_4020[j]
        cb = cmp_bytes[idx] if idx < len(cmp_bytes) else None
        ch = chr(cb) if cb else '?'
        final_flag.append(ch)
        log(f"  flag[{j:2d}]: '{ch}' (from sample at t={t:.1f}, target t={target_time:.1f})")
    else:
        final_flag.append("?")

flag_result = "".join(final_flag)
log(f"\nFinal flag: {flag_result}")
print(flag_result)

proc.kill()
proc.wait()
