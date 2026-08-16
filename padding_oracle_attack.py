#!/usr/bin/env python3
import requests
from binascii import unhexlify
BASE_URL = "http://0f28a2d6-909f-443f-98d6-175a2807db20.51.79.140.18.nip.io:8080/"  # 改成你的靶场地址
BLOCK_SIZE = 16

s = requests.Session()


def get_token_from_login():
    url = BASE_URL.rstrip("/") + "/login"
    r = s.get(url, timeout=5)
    r.raise_for_status()

    data = r.json()

    iv = unhexlify(data["iv"])
    ciphertext = unhexlify(data["ciphertext"])

    if len(iv) != BLOCK_SIZE:
        raise ValueError("Invalid IV length")

    if len(ciphertext) % BLOCK_SIZE != 0:
        raise ValueError("Ciphertext length is not a multiple of block size")

    print("[+] Got token from /login")
    print("[+] IV:", iv.hex())
    print("[+] Ciphertext:", ciphertext.hex())

    return iv, ciphertext


def is_padding_valid(iv: bytes, ciphertext: bytes) -> bool:
    """
    /decrypt invalid padding response:
        {"error":"bad padding"}

    So:
        - if response JSON has error == "bad padding": invalid
        - otherwise: valid padding
    """
    url = BASE_URL.rstrip("/") + "/decrypt"

    r = s.post(
        url,
        json={
            "iv": iv.hex(),
            "ciphertext": ciphertext.hex()
        },
        timeout=5
    )

    try:
        data = r.json()
        if data.get("error") == "bad padding":
            return False
    except Exception:
        pass

    return True


def split_blocks(data: bytes, size: int = BLOCK_SIZE):
    return [data[i:i + size] for i in range(0, len(data), size)]


def decrypt_block(original_prev: bytes, target_block: bytes) -> bytes:
    """
    CBC decryption:

        P_i = Dec(C_i) xor C_{i-1}

    Padding oracle recovers Dec(C_i), also called the intermediate state.

    We send only one ciphertext block to /decrypt:

        iv = crafted_iv
        ciphertext = target_block

    Then the server decrypts:

        plaintext = Dec(target_block) xor crafted_iv

    By controlling crafted_iv, we force valid PKCS#7 padding byte by byte.
    """
    intermediate = bytearray(BLOCK_SIZE)
    plaintext = bytearray(BLOCK_SIZE)

    for pad in range(1, BLOCK_SIZE + 1):
        pos = BLOCK_SIZE - pad
        crafted_iv = bytearray(BLOCK_SIZE)

        # Make already-recovered suffix decrypt to current padding value.
        for j in range(pos + 1, BLOCK_SIZE):
            crafted_iv[j] = intermediate[j] ^ pad

        found = False

        for guess_plaintext in range(32,127):
            guess=original_prev[pos]^guess_plaintext^pad
            crafted_iv[pos] = guess

            if not is_padding_valid(bytes(crafted_iv), target_block):
                continue

            # Avoid false positive when pad == 1.
            #
            # If changing the previous byte keeps padding valid,
            # then the valid padding is really 01.
            #
            # If it breaks, it was probably accidental 02 02, 03 03 03, etc.
            if pad == 1 and pos > 0:
                check_iv = bytearray(crafted_iv)
                check_iv[pos - 1] ^= 1

                if not is_padding_valid(bytes(check_iv), target_block):
                    continue

            intermediate[pos] = guess ^ pad
            plaintext[pos] = intermediate[pos] ^ original_prev[pos]

            ch = chr(plaintext[pos]) if 32 <= plaintext[pos] <= 126 else "."
            print(
                f"[+] pos={pos:02d} pad={pad:02d} "
                f"intermediate={intermediate[pos]:02x} "
                f"plain={plaintext[pos]:02x} {ch}"
            )

            found = True
            break

        if not found:
            raise RuntimeError(f"Failed to recover byte at position {pos}")

    return bytes(plaintext)


def padding_oracle_decrypt(iv: bytes, ciphertext: bytes) -> bytes:
    blocks = split_blocks(ciphertext)
    previous_blocks = [iv] + blocks[:-1]

    recovered = b""
    st=0
    for i, block in enumerate(blocks):
        if i<st:
            continue
        print(f"\n[*] Decrypting block {i + 1}/{len(blocks)}")

        plain_block = decrypt_block(previous_blocks[i], block)
        recovered += plain_block

        print("[+] Plain block:", plain_block)
        print("[+] Recovered so far:", recovered)

    return recovered


def main():
    iv, ciphertext = get_token_from_login()

    padded_plaintext = padding_oracle_decrypt(iv, ciphertext)

    print("\n[+] Raw plaintext:")
    print(padded_plaintext)



if __name__ == "__main__":
    main()
