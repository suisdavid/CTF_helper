from pwn import *
from binascii import a2b_hex
import decimal
from Crypto.Util.number import *


def lsbOracle(c):
    r.sendline(str(c))
    m=r.recv()
    if b"KO" not in m and b"OK" not in m:
        m=r.recv()
        print("NO!!!",m)
    return b"KO" in m

def revealFlag(c,n,c0):
            k = n.bit_length() #二进制长度数，这里是1024
            low = 0
            high = n
            for i in range(k):
                plaintext = (low + high) // 2
                if pow(plaintext,e,n)==c0:
                    return plaintext
                state = lsbOracle(c)
                if not state:  # state = 0
                    high = plaintext #0<high<n/2
                else:
                    low = plaintext
                    print(high,low)
                c = (c * pow(2,e,n)) % n
            return high
	

if __name__ == '__main__':
	r = remote("crypto1.0ops.sjtu.cn",10002)
	n = int(r.recvline()[4:-1])
	print("n: ",n)
	e = int(r.recvline()[4:-1])
	print("e: ",e)
	x=r.recvline()
	c = int(x[16:-1])
	print("c: ",c)
	res = revealFlag((c * pow(2,e,n)) % n, n,c)
	print(res)
	res_hex = hex(res)
	#print res_hex
	print(a2b_hex(res_hex[2:])) #一种方式打印flag
	print(long_to_bytes(res)) #另一种
