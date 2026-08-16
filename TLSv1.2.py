import struct, socket, hashlib, hmac, math, re
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PCAP_PATHS = [
    Path("upload/complete-http(1).pcapng"),
    Path("complete-http.pcapng"),
]

def aes_cbc_dec(key, iv, ct):
    dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    return dec.update(ct) + dec.finalize()

def tls12_prf(secret, label, seed, out_len):
    seed = label.encode() + seed
    a = hmac.new(secret, seed, hashlib.sha256).digest()
    out = b""
    while len(out) < out_len:
        out += hmac.new(secret, a + seed, hashlib.sha256).digest()
        a = hmac.new(secret, a, hashlib.sha256).digest()
    return out[:out_len]

def parse_pcapng(path):
    data = path.read_bytes()
    pkts, off = [], 0
    while off + 12 <= len(data):
        bt, bl = struct.unpack_from("<II", data, off)
        body = data[off + 8: off + bl - 4]
        off += bl
        if bt != 6:
            continue

        _, _, _, caplen, _ = struct.unpack_from("<IIIII", body, 0)
        frame = body[20:20 + caplen]

        ip = frame[4:]  # macOS DLT_NULL header is 4 bytes
        if len(ip) < 20 or ip[0] >> 4 != 4 or ip[9] != 6:
            continue

        ihl = (ip[0] & 15) * 4
        total = int.from_bytes(ip[2:4], "big")
        tcp = ip[ihl:total]
        sport, dport, seq, ack, offflags, win = struct.unpack_from("!HHIIHH", tcp, 0)
        hlen = (offflags >> 12) * 4
        flags = offflags & 0x1ff
        payload = tcp[hlen:]
        pkts.append((sport, dport, seq, flags, payload))
    return pkts

def rebuild_streams(pkts, port=1337):
    client_port = None
    for sport, dport, seq, flags, payload in pkts:
        if dport == port and flags & 2:
            client_port = sport
            break

    streams = {"c2s": [], "s2c": []}
    seen = set()
    for sport, dport, seq, flags, payload in pkts:
        if not payload:
            continue
        key = (sport, dport, seq, payload)
        if key in seen:
            continue
        seen.add(key)

        if sport == client_port and dport == port:
            streams["c2s"].append((seq, payload))
        elif sport == port and dport == client_port:
            streams["s2c"].append((seq, payload))

    return {k: b"".join(p for _, p in sorted(v)) for k, v in streams.items()}

def tls_records(stream):
    out, i = [], 0
    while i + 5 <= len(stream):
        typ = stream[i]
        ver = stream[i + 1:i + 3]
        ln = int.from_bytes(stream[i + 3:i + 5], "big")
        frag = stream[i + 5:i + 5 + ln]
        out.append((typ, ver, frag))
        i += 5 + ln
    return out

def handshakes(frag):
    out, i = [], 0
    while i + 4 <= len(frag):
        typ = frag[i]
        ln = int.from_bytes(frag[i + 1:i + 4], "big")
        raw = frag[i:i + 4 + ln]
        body = frag[i + 4:i + 4 + ln]
        out.append((typ, body, raw))
        i += 4 + ln
    return out

def factor_sparse_n(n):
    B = 1 << 32
    TOP = 1 << 31

    nd = []
    x = n
    while x:
        nd.append(x % B)
        x //= B

    sol = []
    for p0 in range(1, 256, 2):
        if nd[0] % p0 == 0:
            q0 = nd[0] // p0
            if 1 <= q0 <= 255 and q0 & 1:
                sol.append(([p0], [q0]))

    for k in range(1, 31):
        ns = []
        for ps, qs in sol:
            known = sum(ps[i] * qs[k - i] for i in range(1, k))
            R = nd[k] - known
            p0, q0 = ps[0], qs[0]
            for pk in range(1, 256):
                rem = R - q0 * pk
                if rem % p0:
                    continue
                qk = rem // p0
                if 1 <= qk <= 255:
                    ns.append((ps + [pk], qs + [qk]))
        sol = ns

    for ps, qs in sol:
        known = sum(ps[i] * qs[31 - i] for i in range(1, 31))
        for a in range(1, 256):
            for b in range(1, 256):
                total = known + qs[0] * (TOP + a) + ps[0] * (TOP + b)
                if total % B != nd[31]:
                    continue

                pd = ps + [TOP + a]
                qd = qs + [TOP + b]
                p = sum(v * (B ** i) for i, v in enumerate(pd))
                q = sum(v * (B ** i) for i, v in enumerate(qd))
                if p * q == n:
                    return p, q

    raise RuntimeError("factor failed")

def rsa_decrypt_pkcs1_v15(cbytes, n, e, p, q):
    d = pow(e, -1, math.lcm(p - 1, q - 1))
    k = (n.bit_length() + 7) // 8
    block = pow(int.from_bytes(cbytes, "big"), d, n).to_bytes(k, "big")
    sep = block.find(b"\x00", 2)
    return block[sep + 1:]

def decrypt_record(key, mac_key, seq, typ, ver, frag):
    iv, ct = frag[:16], frag[16:]
    print("encrypted message iv=",iv.hex(),"ct=",ct.hex())
    dec = aes_cbc_dec(key, iv, ct)

    padlen = dec[-1]
    assert dec[-padlen - 1:] == bytes([padlen]) * (padlen + 1)

    body = dec[:-padlen - 1]
    pt, mac = body[:-20], body[-20:]

    hdr = seq.to_bytes(8, "big") + bytes([typ]) + ver + len(pt).to_bytes(2, "big")
    good = hmac.new(mac_key, hdr + pt, hashlib.sha1).digest()
    assert hmac.compare_digest(mac, good)

    return pt

def main():
    pcap = next(p for p in PCAP_PATHS if p.exists())
    pkts = parse_pcapng(pcap)
    streams = rebuild_streams(pkts)
    rec = {k: tls_records(v) for k, v in streams.items()}

    transcript = b""
    client_random = server_random = None
    cert_der = encrypted_pms = None
    use_ems = False

    for ht, body, raw in handshakes(rec["c2s"][0][2]):
        transcript += raw
        if ht == 1:
            client_random = body[2:34]

    for typ, ver, frag in rec["s2c"]:
        if typ == 20:
            break
        if typ != 22:
            continue
        for ht, body, raw in handshakes(frag):
            transcript += raw
            if ht == 2:
                server_random = body[2:34]
                pos = 34
                sid_len = body[pos]
                pos += 1 + sid_len
                cipher = int.from_bytes(body[pos:pos + 2], "big")
                pos += 3
                assert cipher == 0x002f

                if pos < len(body):
                    end = pos + 2 + int.from_bytes(body[pos:pos + 2], "big")
                    pos += 2
                    while pos + 4 <= end:
                        et = int.from_bytes(body[pos:pos + 2], "big")
                        el = int.from_bytes(body[pos + 2:pos + 4], "big")
                        pos += 4
                        if et == 0x0017:
                            use_ems = True
                        pos += el

            elif ht == 11:
                cert_len = int.from_bytes(body[3:6], "big")
                cert_der = body[6:6 + cert_len]

    for typ, ver, frag in rec["c2s"][1:]:
        if typ == 20:
            break
        if typ != 22:
            continue
        for ht, body, raw in handshakes(frag):
            transcript += raw
            if ht == 16:
                ln = int.from_bytes(body[:2], "big")
                encrypted_pms = body[2:2 + ln]

    cert = x509.load_der_x509_certificate(cert_der)
    pub = cert.public_key().public_numbers()
    n, e = pub.n, pub.e
    print("RSA pubkey:",n,e)
    p, q = factor_sparse_n(n)
    print(encrypted_pms.hex())
    premaster = rsa_decrypt_pkcs1_v15(encrypted_pms, n, e, p, q)
    print("premaster key:",premaster)
    print(client_random.hex(),server_random.hex(),transcript.hex())
    if use_ems:
        seed = hashlib.sha256(transcript).digest()
        master = tls12_prf(premaster, "extended master secret", seed, 48)
    else:
        master = tls12_prf(premaster, "master secret", client_random + server_random, 48)
    print("master key:",master)
    key_block = tls12_prf(master, "key expansion", server_random + client_random, 72)

    client_mac = key_block[0:20]
    server_mac = key_block[20:40]
    client_key = key_block[40:56]
    server_key = key_block[56:72]

    plains = []
    for name, key, mac_key in [
        ("c2s", client_key, client_mac),
        ("s2c", server_key, server_mac),
    ]:
        encrypted = False
        seq = 0
        for typ, ver, frag in rec[name]:
            if typ == 20:
                encrypted = True
                seq = 0
                continue
            if not encrypted:
                continue
            pt = decrypt_record(key, mac_key, seq, typ, ver, frag)
            plains.append(pt)
            seq += 1

    all_plain = b"\n".join(plains)
    print(all_plain.decode("latin1", errors="replace"))

    m = re.findall(rb"[A-Za-z0-9_]+CTF\{[^}\r\n]+\}", all_plain)
    if m:
        print("\nFLAG =", m[-1].decode())

if __name__ == "__main__":
    main()
