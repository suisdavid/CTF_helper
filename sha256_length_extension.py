#!/usr/bin/env python3
import struct
import json

orig_msg = bytes.fromhex(
    "757365723d677565737426726f6c653d766965776572"
)
old_tag = "de5f5fd011553fd8f50797dc78f059aa1bccc4849a93d490b81275ebcb9c6514"
# Change this depending on what the server accepts as admin.
extra = b"&role=admin"
extra = b"&admin=true"
# extra = b"&user=admin"

K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]

def rotr(x, n):
    return ((x >> n) | (x << (32 - n))) & 0xffffffff

def sha256_pad(length):
    return (
        b"\x80"
        + b"\x00" * ((56 - (length + 1) % 64) % 64)
        + struct.pack(">Q", length * 8)
    )

def compress(block, h):
    w = list(struct.unpack(">16I", block))
    for i in range(16, 64):
        s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
        s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
        w.append((w[i - 16] + s0 + w[i - 7] + s1) & 0xffffffff)

    a, b, c, d, e, f, g, hh = h

    for i in range(64):
        S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)
        ch = (e & f) ^ ((~e) & g)
        t1 = (hh + S1 + ch + K[i] + w[i]) & 0xffffffff
        S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)
        maj = (a & b) ^ (a & c) ^ (b & c)
        t2 = (S0 + maj) & 0xffffffff

        hh, g, f, e, d, c, b, a = (
            g,
            f,
            e,
            (d + t1) & 0xffffffff,
            c,
            b,
            a,
            (t1 + t2) & 0xffffffff,
        )

    return [
        (h[0] + a) & 0xffffffff,
        (h[1] + b) & 0xffffffff,
        (h[2] + c) & 0xffffffff,
        (h[3] + d) & 0xffffffff,
        (h[4] + e) & 0xffffffff,
        (h[5] + f) & 0xffffffff,
        (h[6] + g) & 0xffffffff,
        (h[7] + hh) & 0xffffffff,
    ]

def continue_sha256(old_digest_hex, already_hashed_len, extra):
    h = list(struct.unpack(">8I", bytes.fromhex(old_digest_hex)))

    forged_tail = extra + sha256_pad(already_hashed_len + len(extra))

    for i in range(0, len(forged_tail), 64):
        h = compress(forged_tail[i:i + 64], h)

    return b"".join(struct.pack(">I", x) for x in h).hex()

for secret_len in range(16,17):
    glue = sha256_pad(secret_len + len(orig_msg))

    forged_msg = orig_msg + glue + extra

    already_hashed_len = secret_len + len(orig_msg) + len(glue)

    forged_tag = continue_sha256(
        old_tag,
        already_hashed_len,
        extra,
    )

    print("secret_len =", secret_len)
    print(json.dumps({
        "msg": forged_msg.hex(),
        "tag": forged_tag,
    }, separators=(",", ":")))
