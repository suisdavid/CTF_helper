#!/usr/bin/env python3
import time
import ssl
import socket

def get_cn(der_bytes):
    # 在证书 DER 二进制里搜索 CommonName 字段 (OID 2.5.4.3)
    oid = b'\x06\x03\x55\x04\x03'
    idx = der_bytes.find(oid)
    if idx == -1:
        return None
    try:
        val_idx = idx + 5
        length = der_bytes[val_idx + 1]
        if length & 0x80:
            len_bytes = length & 0x7f
            length = int.from_bytes(der_bytes[val_idx + 2 : val_idx + 2 + len_bytes], 'big')
            val_idx += len_bytes
        cn_bytes = der_bytes[val_idx + 2 : val_idx + 2 + length]
        return cn_bytes.decode('utf-8', errors='ignore')
    except Exception:
        return None

def main():
    with open('flag.txt', 'r') as f:
        flag = f.read().strip()

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE          # ← 漏洞：关闭证书验证

    while True:
        try:
            with socket.create_connection(('net-mitm.local', 4443), timeout=3) as sock:
                with context.wrap_socket(sock, server_hostname='net-mitm.local') as ss:
                    der_cert = ss.getpeercert(binary_form=True)
                    cn = get_cn(der_cert)
                    if cn == 'net-mitm.local':   # ← 唯一的"验证"：比对 CN 字符串
                        ss.sendall(f"POST /submit HTTP/1.1\r\nHost: net-mitm.local\r\n"
                                   f"Content-Length: {len(flag)}\r\n\r\n{flag}".encode())
                        print("[client] CN 检查通过，flag 已发送")
                    else:
                        print(f"[client] CN 不匹配: {cn!r}，拒绝发送")
        except Exception as e:
            print(f"[client] 连接失败: {e}")
        time.sleep(3)

if __name__ == '__main__':
    main()
