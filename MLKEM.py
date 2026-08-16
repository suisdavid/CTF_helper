from pathlib import *
from quantcrypt.kem import MLKEM_1024
from quantcrypt.cipher import KryptonKEM
import hashlib
import os

def check_skey(skey):
    pk = skey[1536 : 1536 + 1568]
    h_pk = skey[1536 + 1568 : 1536 + 1568 + 32]
    calculated_h_pk = hashlib.sha3_256(pk).digest()
    return calculated_h_pk == h_pk
kem = MLKEM_1024()
kry = KryptonKEM(MLKEM_1024)
with open("output.raw",'rb') as f:
    s=f.read()
skey_len=3168
skeys=[]
for i in range(40):
    skeys.append(s[i*skey_len:(i+1)*skey_len])
c=22
for i in range(39,-1,-1):
    print(i)
    if check_skey(skeys[i]):  
        ct=Path(f'flag_{c}.enc')
        if c==0:
            pt=Path('flag.png')
        else:
            c-=1
            pt=Path(f'flag_{c}.enc')
        kry.decrypt_to_file(skeys[i], ct, pt)
