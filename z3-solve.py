#!/usr/bin/env python3
# pip install z3-solver
import sys
import socket
import subprocess
from multiprocessing import Process, Queue
from z3 import *

class Tube:
    def __init__(self, argv=None, host=None, port=None):
        if argv is not None:
            self.p = subprocess.Popen(
                argv,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            self.f = self.p.stdout
            self.w = self.p.stdin
            self.sock = None
        else:
            self.sock = socket.create_connection((host, port))
            self.f = self.sock.makefile("rb", buffering=0)
            self.w = self.sock.makefile("wb", buffering=0)
            self.p = None

    def sendline(self, data: bytes):
        self.w.write(data + b"\n")
        self.w.flush()

    def recvline(self):
        return self.f.readline()

    def recvall(self, timeout=2):
        if self.sock is not None:
            self.sock.settimeout(timeout)
            chunks = []
            try:
                while True:
                    b = self.sock.recv(4096)
                    if not b:
                        break
                    chunks.append(b)
            except Exception:
                pass
            return b"".join(chunks)
        try:
            return self.p.communicate(timeout=timeout)[0]
        except subprocess.TimeoutExpired:
            return b""

WORD = 0xFFFFFFFF
_ROUNDS = 28
_DELTA = [
    0x243F6A88, 0x85A308D3, 0x13198A2E,
    0x03707344, 0xA4093822, 0x299F31D0,
]
_ROT = [9, 5, 13, 3]
_KROT = [3, 7, 11, 17, 19, 23]
_KOFF = [0, 5, 9, 15, 21, 27]

def rol(x, r):
    return ((x << r) | (x >> (32 - r))) & WORD

def ror(x, r):
    return ((x >> r) | (x << (32 - r))) & WORD

def bv(x):
    return BitVecVal(x & WORD, 32)

def words(bs):
    return [int.from_bytes(bs[i * 4:(i + 1) * 4], "little") for i in range(5)]

def key_schedule(key: bytes):
    T = [int.from_bytes(key[i * 4:(i + 1) * 4], "little") for i in range(6)]
    rks = []
    for i in range(_ROUNDS):
        d = _DELTA[i % 6]
        for j in range(6):
            T[j] = rol((T[j] + rol(d, (5 * i + _KOFF[j]) & 31)) & WORD, _KROT[j])
        rks.append([T[j] for j in range(6) if j != i % 6])
    return rks

def enc_local(pt: bytes, key: bytes) -> bytes:
    st = words(pt[:20].ljust(20, b"\0"))
    for rk in key_schedule(key):
        x0, x1, x2, x3, x4 = st
        k0, k1, k2, k3, k4 = rk
        st = [
            rol((x0 + (x1 ^ k1) + k0) & WORD, 9),
            ror(((x1 ^ k2) + (x2 ^ k3)) & WORD, 5),
            rol(((x2 ^ k4) + (x3 ^ k2) + k0) & WORD, 13),
            ror(((x3 ^ k3) + (x4 ^ k4)) & WORD, 3),
            x0 ^ k0,
        ]
    return b"".join(x.to_bytes(4, "little") for x in st)

def zround(st, rk):
    x0, x1, x2, x3, x4 = st
    k0, k1, k2, k3, k4 = rk
    return [
        RotateLeft(x0 + (x1 ^ k1) + k0, 9),
        RotateRight((x1 ^ k2) + (x2 ^ k3), 5),
        RotateLeft((x2 ^ k4) + (x3 ^ k2) + k0, 13),
        RotateRight((x3 ^ k3) + (x4 ^ k4), 3),
        x0 ^ k0,
    ]

def zkey_schedule(K):
    T = list(K)
    rks = []
    for i in range(_ROUNDS):
        d = _DELTA[i % 6]
        for j in range(6):
            c = rol(d, (5 * i + _KOFF[j]) & 31)
            T[j] = RotateLeft(T[j] + bv(c), _KROT[j])
        rks.append([T[j] for j in range(6) if j != i % 6])
    return rks

def solve_worker(pt_hex, ct_hex, samples, seed, q):
    try:
        pt = bytes.fromhex(pt_hex)
        ct = bytes.fromhex(ct_hex)
        ct_words = words(ct)
        pt_words = words(pt)

        s = SolverFor("QF_BV")
        s.set(random_seed=seed)

        K = [BitVec(f"K{j}", 32) for j in range(6)]
        rks = zkey_schedule(K)

        states = [[bv(x) for x in pt_words]]
        for i in range(_ROUNDS):
            states.append(zround(states[-1], rks[i]))

        for a, b in zip(states[-1], ct_words):
            s.add(a == bv(b))

        for idx, (fr, wi, cf_hex) in enumerate(samples):
            cf_words = words(bytes.fromhex(cf_hex))
            f = BitVec(f"f{idx}", 32)
            s.add(f != bv(0))

            st = list(states[fr])
            st[wi] = st[wi] + f

            for r in range(fr, _ROUNDS):
                st = zround(st, rks[r])

            for a, b in zip(st, cf_words):
                s.add(a == bv(b))

        if s.check() != sat:
            q.put(None)
            return

        m = s.model()
        key = b"".join(
            m.eval(K[i], model_completion=True).as_long().to_bytes(4, "little")
            for i in range(6)
        )

        if enc_local(pt, key).hex() == ct_hex:
            q.put(key.hex())
        else:
            q.put(None)

    except Exception:
        q.put(None)

def solve_with_timeout(pt, ct, samples):
    for seed in range(12):
        q = Queue()
        p = Process(target=solve_worker, args=(pt.hex(), ct.hex(), samples, seed, q))
        p.start()
        p.join(5.5)

        if p.is_alive():
            p.terminate()
            p.join()
            continue

        if not q.empty():
            ans = q.get()
            if ans:
                return bytes.fromhex(ans)

    raise RuntimeError("z3 没在时间内解出，重跑一次脚本")

def parse_ans(line: bytes) -> bytes:
    return bytes.fromhex(line.decode().strip().split()[-1])

def main():

    io = Tube(host='instance.penguin.0ops.sjtu.cn', port=18808)
    pt = b"\x00" * 20

    io.sendline(b"0")
    io.sendline(pt.hex().encode())
    ct = parse_ans(io.recvline())

    plan = [(27, i) for i in range(4) for _ in range(4)]
    plan += [(26, i) for i in range(5) for _ in range(2)]
    plan += [(26, 2)]
    assert len(plan) == 27

    samples = []
    for fr, wi in plan:
        io.sendline(b"1")
        io.sendline(pt.hex().encode())
        io.sendline(f"{fr} {wi}".encode())
        cf = parse_ans(io.recvline())
        samples.append((fr, wi, cf.hex()))

    key = solve_with_timeout(pt, ct, samples)
    print("KEY =", key.hex())

    io.sendline(key.hex().encode())
    print(io.recvall(timeout=2).decode(errors="ignore"))

if __name__ == "__main__":
    main()
