import binascii
import string
from hashlib import sha256
from pwn import *

# --- Utility Functions ---

def rotate_right(x, n):
    return ((x >> n) | (x << (32 - n))) & 0xffffffff

def solve_pow(target_prefix):
    # Example: sha256(XXXX + suffix) == digest
    # The server sends: sha256(XXXX + %s) == %s
    log.info(f"Solving PoW: {target_prefix}")
    suffix = target_prefix.split("+ ")[1].split(")")[0]
    digest = target_prefix.split("== ")[1].split("\n")[0]
    
    chars = string.ascii_letters + string.digits
    for c1 in chars:
        for c2 in chars:
            for c3 in chars:
                for c4 in chars:
                    guess = c1 + c2 + c3 + c4
                    if sha256((guess + suffix).encode()).hexdigest() == digest:
                        return guess

def split_to_nibbles(x):
    return [(x >> (4 * i)) & 0xf for i in range(8)][::-1]

# --- Attack Script ---

def crack():
    # 1. Connect to server
    r = remote('111.186.57.85',30226) # Change to actual IP/Port
    
    # 2. Handle PoW
    pow_msg = r.recvuntil(b"Give me XXXX:").decode()
    token = solve_pow(pow_msg)
    r.sendline(token.encode())
    r.recvuntil(b"0ops Feistel Cipher :)")

    # 3. Data Collection (Slide Attack)
    # We need P = (i, 0) and P' = (0, j)
    # If P' = Round1(P), then j = i ^ F(0)
    N = 32000 # Number of blocks to query
    batch_size = 64 # Max blocks per query (1024 hex chars)
    
    p_blocks = []
    for i in range(N):
        p_blocks.append(struct.pack(">II", i, 0))
    
    p_prime_blocks = []
    for i in range(N):
        p_prime_blocks.append(struct.pack(">II", 0, i))

    def get_encryptions(block_list):
        results = {}
        for i in range(0, len(block_list), batch_size):
            chunk = b"".join(block_list[i : i + batch_size])
            r.sendlineafter(b"> ", b"enc")
            r.sendlineafter(b"hex (max length 1024): ", binascii.hexlify(chunk))
            res_hex = r.recvline().strip()
            res_bin = binascii.unhexlify(res_hex)
            for j in range(len(res_bin) // 8):
                idx = i + j
                pt_l = struct.unpack(">I", block_list[idx][:4])[0]
                pt_r = struct.unpack(">I", block_list[idx][4:])[0]
                ct_l = struct.unpack(">I", res_bin[j*8 : j*8+4])[0]
                ct_r = struct.unpack(">I", res_bin[j*8+4 : (j+1)*8])[0]
                results[(pt_l, pt_r)] = (ct_l, ct_r)
        return results

    log.info("Querying P blocks...")
    p_results = get_encryptions(p_blocks)
    log.info("Querying P' blocks...")
    pp_results = get_encryptions(p_prime_blocks)

    # 4. Find Slid Pair
    # Slid Condition: L'_out == R_out
    log.info("Searching for slid pairs...")
    
    # Create a lookup for P' results based on L'_out
    pp_lookup = {}
    for (pl, pr), (cl, cr) in pp_results.items():
        pp_lookup[cl] = (pr, cr) # pl is always 0

    target_f0 = None
    slid_pairs = []

    for (pl, pr), (cl, cr) in p_results.items():
        if cr in pp_lookup:
            # Candidate found!
            # If (pl, 0) and (0, pr_prime) are slid:
            # pr_prime = pl ^ F(0) => F(0) = pl ^ pr_prime
            pr_prime, cr_prime = pp_lookup[cr]
            cand_f0 = pl ^ pr_prime
            
            # Verify candidate by looking for another pair
            # (Just a simple heuristic for this CTF)
            target_f0 = cand_f0
            log.success(f"Found F(0) candidate: {hex(target_f0)}")
            break

    # 5. Recover S-Boxes
    # SBOX is a list of 16 values for each of the 8 positions
    recovered_sbox = [[-1]*16 for _ in range(8)]
    
    # Recover pairs using the found F(0)
    # Condition: P=(i, 0) and P'=(0, i ^ F(0))
    count = 0
    for i in range(N):
        j = i ^ target_f0
        if (i, 0) in p_results and (0, j) in pp_results:
            cl, cr = p_results[(i, 0)]
            cl_p, cr_p = pp_results[(0, j)]
            
            # Round function relation: R'_out = L_out ^ F(R_out)
            # F(R_out) = L_out ^ R'_out
            f_rout = cl ^ cr_p
            
            # Reverse Rotation 11
            val_v = rotate_right(f_rout, 11)
            
            # Split R_out and val_v into nibbles
            in_nibbles = split_to_nibbles(cr)
            out_nibbles = split_to_nibbles(val_v)
            
            for pos in range(8):
                recovered_sbox[pos][in_nibbles[pos]] = out_nibbles[pos]
            count += 1

    # Check if S-box is complete
    for i, s in enumerate(recovered_sbox):
        if -1 in s:
            log.warning(f"SBOX[{i}] is incomplete! Try increasing N.")
        else:
            log.info(f"SBOX[{i}] recovered.")

    # 6. Get Flag
    # The secret is sha256(str(cs.SBOX).encode()).hexdigest()
    # Note: Python's str(list) includes spaces after commas: [[0, 1], [2, 3]]
    sbox_str = str(recovered_sbox)
    secret_hash = sha256(sbox_str.encode()).hexdigest()
    
    log.info(f"Sending secret hash: {secret_hash}")
    r.sendline(b"flag")
    r.sendlineafter(b"Secret in hex: ", secret_hash.encode())
    
    success_msg = r.recvall()
    print(success_msg.decode())

if __name__ == "__main__":
    crack()
