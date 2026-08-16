import os
import base64
from Crypto.Cipher import AES
from Crypto.Util.number import bytes_to_long
from flag import flag
key=os.urandom(2)*8
iv=os.urandom(16)
print(bytes_to_long(key)^bytes_to_long(iv))
aescbc=AES.new(key, AES.MODE_CBC, iv)
c=aescbc.encrypt(flag)
print(base64.b64encode(c))

#252369267708781763135546880686284112070
#b'VmRpnFd4Avj21+aL7CLSBn027HoNnAPSpq+zagj+RFk='
#hint：flag总长度为32位