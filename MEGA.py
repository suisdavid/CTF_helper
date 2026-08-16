from pwn import *
from Crypto.Util.number import *
from hashlib import sha256
from Crypto.Hash import SHA256, SHA512
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
import json


conn=remote("socket.cryptohack.org",13410)
x=conn.recv()
y=conn.recv()
x=x+y
print(x)
s1=x.find(ord('{'))
s2=x.find(ord('}'))
v=x[s1:s2+1]
s=''
for each in v:
    s+=chr(each)
s=eval(s)
master_key_enc=s["master_key_enc"]
n=s["share_key_pub"][0]
e=65537
share_key_enc=bytes.fromhex(s["share_key_enc"])
x=x[s2+1:]
s1=x.find(ord('{'))
s2=x.find(ord('}'))
v=x[s1:s2+1]
s=''
for each in v:
    s+=chr(each)
s=eval(s)
node_key_enc=s["node_key_enc"]
file_enc=s["file_enc"]
x=x[s2+1:]
s1=x.find(ord('{'))
s2=x.find(ord('}'))
v=x[s1:s2+1]
s=''
for each in v:
    s+=chr(each)
s=eval(s)
p=s["share_key"][2]
q=n//p
phi=(p-1)*(q-1)
d=pow(e,-1,phi)
u=pow(p,-1,q)
def format_number(num):
    num_bytes = long_to_bytes(num)
    return long_to_bytes(len(num_bytes), 2) + num_bytes

def format_rsa_privkey():
    data = b""
    data += format_number(p)
    data += format_number(q)
    data += format_number(d)
    data += format_number(u)
    return pad(data, 16)
data=format_rsa_privkey()
u0=bytes_to_long(data[-32:-16])
ndata=share_key_enc[:-32]+bytes.fromhex(node_key_enc)+share_key_enc[-16:]
print(ndata)
msg={"action":"wait_login"}
conn.send(json.dumps(msg))
print(conn.recv())
print(conn.recv())
m=p+q
SID_enc=pow(m,e,n)
msg={"action":"send_challenge","SID_enc":long_to_bytes(SID_enc).hex(),"share_key_enc":ndata.hex(),"master_key_enc":master_key_enc.hex()}
conn.send(json.dumps(msg))
rr=conn.recv()
print(rr)
newm=bytes_to_long(eval(rr)["SID"])*(2**128)
if (newm-m)%p!=0:
    newm+=(p-(newm-m)%p)
deltam=((newm-m)//p)%q
t=(m%q-m%p)%q
deltax=pow(t*256,-1,q)*deltam%q
if u0+deltax>=(2**128):
    deltax-=q
node_key=long_to_bytes(u0+deltax)
print(AES.new(node_key, AES.MODE_ECB).decrypt(file_enc))

