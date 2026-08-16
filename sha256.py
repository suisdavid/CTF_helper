# 常数初始化
H = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]
 
# 将输入的文本转换为二进制
def turn_binary(message):
    binary = message.encode('utf8')
    return binary
 
# 填充二进制编码
def padding_binary(binary):
    l = len(binary) * 8
    k = (448 - (l + 8)) % 512
    if k == 0:
        k = 512
    k = k // 8
    M = binary + b'\x80' + b'\x00' * k + l.to_bytes(8, byteorder='big')
    # print(f"M：{M.hex()}")
    return M
 
# X右移n位
def ROTR(x, n):
    x = (x >> n) | (x << 32 - n)
    return x
 
def cycle(M):
    a = H[0]
    b = H[1]
    c = H[2]
    d = H[3]
    e = H[4]
    f = H[5]
    g = H[6]
    h = H[7]
    W = [0] * 64
    for t in range(0, 16):
        W[t] = M[t * 4:t * 4 + 4]
        # 将W记成16进制
        W[t] = int(W[t].hex(), 16)
    for t in range(16, 64):
        # ^是异或运算
        S1 = ROTR(W[t - 2], 17) ^ ROTR(W[t - 2], 19) ^ (W[t - 2] >> 10)
        S0 = ROTR(W[t - 15], 7) ^ ROTR(W[t - 15], 18) ^ (W[t - 15] >> 3)
        # 运算时超过8位16进制数字，为去掉8位前多余的数值进行压缩 & 0xFFFFFFFF
        W[t] = (S1 + W[t - 7] + S0 + W[t - 16]) & 0xFFFFFFFF
    # print(f"W:{W}")
    for t in range(0, 64):
        S1 = ROTR(e, 6) ^ ROTR(e, 11) ^ ROTR(e, 25)
        Ch = (e & f) ^ ((~e) & g)
        S0 = ROTR(a, 2) ^ ROTR(a, 13) ^ ROTR(a, 22)
        Maj = (a & b) ^ (a & c) ^ (b & c)
        T1 = h + S1 + Ch + K[t] + W[t]
        T2 = S0 + Maj
        h = g
        g = f
        f = e
        e = (d + T1) & 0xFFFFFFFF
        d = c
        c = b
        b = a
        a = (T1 + T2) & 0xFFFFFFFF
    # ha = (a, b, c, d, e, f, g, h)
    # for ha in ha:
    #     print(hex(ha))
    # input('按enter继续……')
 
    H[0] = a + H[0] & 0xFFFFFFFF
    H[1] = b + H[1] & 0xFFFFFFFF
    H[2] = c + H[2] & 0xFFFFFFFF
    H[3] = d + H[3] & 0xFFFFFFFF
    H[4] = e + H[4] & 0xFFFFFFFF
    H[5] = f + H[5] & 0xFFFFFFFF
    H[6] = g + H[6] & 0xFFFFFFFF
    H[7] = h + H[7] & 0xFFFFFFFF
 
def encode(M):
    print("————————加密过程————————")
    for i in range(0, len(M) // 64):
        cycle(M[i * 64: i * 64 + 64])
        print(f"第{i + 1}次迭代，H：{H}")
 
# 正式开始运行！
print("————————SHA256————————")
message = input('请输入需要加密的信息：')
print('————————加密准备————————')
# 将文本转换为二进制表示
binary_message = turn_binary(message)
padded_message = padding_binary(binary_message)
# 输出中间结果
print("原始文本:", message)
print("二进制表示:", binary_message)
print("填充后二进制字符串：", padded_message)
# 加密
encode(padded_message)
 
sha256 = ''
print("————————加密验证————————")
print("H十六进制表示：")
for sha in H:
    print(f"{hex(sha)}")
    sha256 = sha256 + sha.to_bytes(4, byteorder='big').hex()
print(f"加密结果：{sha256}")
 
import hashlib
ha = message.encode('utf8')
print(f"标准加密：{hashlib.sha256(ha).hexdigest()}")
if sha256 == hashlib.sha256(ha).hexdigest():
    print('结果一致')
else:
    print("结果有误，请检查代码")
