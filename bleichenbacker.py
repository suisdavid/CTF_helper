from Crypto.Util.number import *
from typing import List, Tuple
import random
p=getPrime(512)
q=getPrime(512)
N=p*q
phi=(p-1)*(q-1)
E = 65537
D=pow(E,-1,phi)
m=bytes_to_long(b'message')
C=pow(m,E,N)
K = 128


def ceil_div(a: int, b: int) -> int:
    return -(-a // b)


def floor_div(a: int, b: int) -> int:
    return a // b


def merge_intervals(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not intervals:
        return []

    intervals.sort()
    merged = [intervals[0]]

    for a, b in intervals[1:]:
        la, lb = merged[-1]
        if a <= lb + 1:
            merged[-1] = (la, max(lb, b))
        else:
            merged.append((a, b))

    return merged


class RemoteOracle:
    def __init__(self, host: str, port: int):
        self.host=host
        self.port=port
        self.queries=0
    def check_ct(self, ct: int) -> bool:
        self.queries += 1
        block=pow(ct,D,N).to_bytes(K,'big')
        if len(block) < 11:
            return False
        if not block.startswith(b"\x00\x02"):
            return False
        try:
            separator = block.index(b"\x00", 2)
        except ValueError:
            return False
        if separator < 10:
            return False
        return all(byte != 0 for byte in block[2:separator])


def bleichenbacher_attack(n: int, e: int, c0: int, k: int, oracle: RemoteOracle) -> int:
    """
    Recover PKCS#1 v1.5 plaintext integer m from ciphertext c0,
    using an oracle that says whether RSA-decrypted block starts with 00 02 ... 00.
    """

    B = 2 ** (8 * (k - 2))
    lo = 2 * B
    hi = 3 * B - 1

    print(f"[+] B  = {B}")
    print(f"[+] valid plaintext interval = [{lo}, {hi}]")

    # ------------------------------------------------------------
    # Step 1: blinding.
    # Usually the challenge target ciphertext is already conforming.
    # If not, find s0 such that c0 * s0^e mod n becomes conforming.
    # ------------------------------------------------------------
    print("[+] checking whether target ciphertext is already PKCS conforming...")

    if oracle.check_ct(c0):
        s0 = 1
        c = c0
        print("[+] c is already conforming")
    else:
        print("[*] c is not conforming, searching blinding factor s0...")
        s0=random.randint(1,N-1)
        while True:
            ct = (c0 * pow(s0, e, n)) % n
            if oracle.check_ct(ct):
                c = ct
                print(f"[+] found s0 = {s0}")
                break
            s0=random.randint(1,N-1)
            if oracle.queries % 10000 == 0:
                print(f"[*] s0 search: {s0}, queries={oracle.queries}")

    # The interval for the blinded plaintext m' = m * s0 mod n.
    M: List[Tuple[int, int]] = [(lo, hi)]

    # ------------------------------------------------------------
    # Step 2a: find first s >= n / (3B)
    # ------------------------------------------------------------
    s = ceil_div(n, 3 * B)
    print(f"[+] searching first s from {s}...")

    while True:
        ct = (c * pow(s, e, n)) % n
        if oracle.check_ct(ct):
            print(f"[+] found s1 = {s}, queries={oracle.queries}")
            break
        s += 1
        if s % 10000 == 0:
            print(f"[*] s search: {s}, queries={oracle.queries}")

    iteration = 1

    while True:
        # --------------------------------------------------------
        # Step 3: update intervals
        # --------------------------------------------------------
        new_M: List[Tuple[int, int]] = []

        for a, b in M:
            r_min = ceil_div(a * s - hi, n)
            r_max = floor_div(b * s - lo, n)

            for r in range(r_min, r_max + 1):
                new_a = max(a, ceil_div(lo + r * n, s))
                new_b = min(b, floor_div(hi + r * n, s))

                if new_a <= new_b:
                    new_M.append((new_a, new_b))

        M = merge_intervals(new_M)

        if not M:
            raise RuntimeError("interval set became empty; oracle or math is wrong")

        width = sum(b - a for a, b in M)
        print(
            f"[+] iter={iteration}, s={s}, intervals={len(M)}, "
            f"width={width}, queries={oracle.queries}"
        )

        # --------------------------------------------------------
        # Step 4: done
        # --------------------------------------------------------
        if len(M) == 1 and M[0][0] == M[0][1]:
            m_blinded = M[0][0]
            m = (m_blinded * pow(s0, -1, n)) % n
            print("[+] recovered plaintext integer")
            return m

        # --------------------------------------------------------
        # Step 2b / 2c: find next s
        # --------------------------------------------------------
        if len(M) >= 2:
            # 多区间时，直接线性递增找下一个 valid s
            s += 1
            while True:
                ct = (c * pow(s, e, n)) % n
                if oracle.check_ct(ct):
                    break
                s += 1
                if s % 10000 == 0:
                    print(f"[*] multi-interval s search: {s}, queries={oracle.queries}")
        else:
            # 单区间时，用 r 缩小搜索范围，避免暴力扫太久
            a, b = M[0]
            r = ceil_div(2 * (b * s - lo), n)

            found = False
            while not found:
                s_min = ceil_div(lo + r * n, b)
                s_max = floor_div(hi + r * n, a)

                # 防止找到旧的 s 导致死循环
                if s_min <= s:
                    s_min = s + 1

                for cand_s in range(s_min, s_max + 1):
                    ct = (c * pow(cand_s, e, n)) % n
                    if oracle.check_ct(ct):
                        s = cand_s
                        found = True
                        break

                r += 1

                if r % 10000 == 0:
                    print(
                        f"[*] single-interval r search: r={r}, "
                        f"s_range=({s_min}, {s_max}), queries={oracle.queries}"
                    )

        iteration += 1


def decode_pkcs1_v15_block(m: int, k: int) -> bytes:
    block = m.to_bytes(k, "big")

    print("[+] recovered block hex:")
    print(block.hex())

    if not block.startswith(b"\x00\x02"):
        print("[!] warning: block does not start with 00 02")

    sep = block.find(b"\x00", 2)
    if sep == -1:
        raise ValueError("no PKCS#1 separator byte found")

    padding = block[2:sep]
    msg = block[sep + 1:]

    print(f"[+] padding length = {len(padding)}")
    print(f"[+] message length = {len(msg)}")

    return msg


def main():
    print(f"N={N}\nE={E}\nC={C}")
    oracle = RemoteOracle("74.113.234.79",30300)
    
    m = bleichenbacher_attack(N, E, C, K, oracle)
    msg = decode_pkcs1_v15_block(m, K)

    print("[+] plaintext bytes:")
    print(msg)

    try:
        print("[+] plaintext ascii:")
        print(msg.decode())
    except UnicodeDecodeError:
        print("[!] plaintext is not valid UTF-8")


if __name__ == "__main__":
    main()
