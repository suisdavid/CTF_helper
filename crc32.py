import itertools
import string
import binascii
dic=string.ascii_letters+string.digits+'+'+'='+'_'
crc=0x71DB239F
i=0
for txt in itertools.product(dic,repeat=6):
    i+=1
    if i%100000==0:
        print(i)
        print(txt)
    txt=''.join(txt)
    encoded_txt=txt.encode('utf-8')
    if binascii.crc32(encoded_txt)&0xffffffff == crc:
        print(txt)
        exit(0)
