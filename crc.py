import binascii
import struct
crc=0x1E3F88B1
for i in range(65536):
    height=struct.pack('>i',i)
    data=b"\x49\x48\x44\x52\x00\x00\x00\x32"+height+b"\x08\x06\x00\x00\x00"
    cr=binascii.crc32(data)&0xffffffff
    if cr==crc:
        print(i)
        print(height)
