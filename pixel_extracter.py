import struct
from PIL import Image

# ========== 1. 读取 .tsc 文件 ==========
with open('chall.txt', 'rb') as f:
    data = f.read()

# ========== 2. 解析文件头 ==========
magic       = data[0:4]                          # "TSCF"
version     = struct.unpack('<I', data[4:8])[0]  # 1
width       = struct.unpack('<I', data[8:12])[0] # 60
height      = struct.unpack('<H', data[12:14])[0]# 61
format_spec = data[14:17]                        # 3 bytes

print(f"Magic: {magic}")
print(f"Version: {version}")
print(f"Width: {width}")
print(f"Height: {height}")
print(f"Format spec: {format_spec.hex()}")

# ========== 3. 提取 RGBA 像素数据 ==========
pixel_data = bytearray(data[17:]) # 头部长度 17 bytes
for i in range(width * height):
    pixel_data[i * 4 + 3] = 255
pixel_data=bytes(pixel_data)
img = Image.frombytes('RGBA', (width, height), pixel_data)
img.save('extracted_duck.png')
print(f"[+] 图片已保存: extracted_duck.png ({width}x{height})")

# ========== 4. 从彩色噪点中提取 Flag ==========
flag_chars = []
pixel_count = width * height

for i in range(pixel_count):
    offset = i * 4
    r, g, b, a = pixel_data[offset:offset+4]
    
    # 排除灰度身体像素：max(R,G,B) - min(R,G,B) < 5
    if max(r, g, b) - min(r, g, b) >= 0:
        # R/G/B 每个通道解码为一个可打印 ASCII 字符
        if 32 <= r <= 126 and 32 <= g <= 126 and 32 <= b <= 126:
            flag_chars.append(chr(r))
            flag_chars.append(chr(g))
            flag_chars.append(chr(b))

flag = ''.join(flag_chars)
print(f"[+] Flag: {flag}")
