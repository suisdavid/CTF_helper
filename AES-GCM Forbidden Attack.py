import struct
from minipwn import *
F = GF(1<<128,name='a',modulus=x^128+x^7+x^2+x+1)
a = F.gen()
P = PolynomialRing(F,'x')
x = P.gen()


def convert_to_blocks(a,length=16):
    try:
        a = a.encode()
    except:
        pass
    if not a:
        return []
    if len(a)%length:
        res = [int.from_bytes(a[i*length:length+i*length],byteorder='big') for i in range(len(a)//length+1)]
    else:
        res = [int.from_bytes(a[i*length:length+i*length],byteorder='big') for i in range(len(a)//length)]
    return res

def int_to_poly(a,x):
    poly = 0
    # brillant implement
    bin_a = bin(a)[2:].zfill(128)
    for i in range(len(bin_a)):
        poly += int(bin_a[i])*x^i
    return poly

def poly_to_int(poly):
    return int(bin(poly.integer_representation())[2:].zfill(128)[::-1], 2)


    
def build_poly(addtion,cipher,x,a):
    int_a = convert_to_blocks(addtion)
    int_c = convert_to_blocks(cipher)
    A = [int_to_poly(i,a) for i in int_a]
    C = [int_to_poly(i,a) for i in int_c]
    m = len(A)
    n = len(C)
    # 64bits representation
    L = struct.pack(">QQ",len(addtion)*8,len(cipher)*8)
    L = int_to_poly(int.from_bytes(L,byteorder='big'),a)
#     print(L)
    poly = 0
    for i in range(m+n+1,0,-1):
        if i>= n+2:
            poly += A[m+n+1-i]*x^i
        elif i>=2:
            poly += C[n+1-i]*x^i
        else:
            poly += L*x
    return poly

address = '127.0.0.1'
port = 11111
io = remote(address,port)

def encrypt(mess):
    while True:
        res = io.recvline()
        print(res)
        if b'Select option:' in res:
            io.sendline('1')
            tmp = io.recvline()
            print(tmp)
            io.sendline(mess)
            io.recvline()
            res = io.recvline()
            print(res)
            return res

def decrypt(mess,tag):
     while True:
        res = io.recvline()
        print(res)
        if b'Select option:' in res:
            io.sendline('2')
            tmp = io.recvline()
            print(tmp)
            io.sendline(mess)
            io.sendline(tag)
            io.recvline()
            res = io.recvline()
            print(res)
            return res
def str_to_bytes(a):
    res = b""
    for i in a:
        res += bytes([ord(i)])
    return res

def bytes_to_str(a):
    res = ''
    for i in a:
        res += chr(i)
    return res
        
def attack():
    io.recvuntil('flag ')
    flag_hex = io.recvline()[:-1]
    flag_hex = bytes_to_str(flag_hex)
    tmp = encrypt('a'*32)
    cHex = bytes_to_str(tmp[2:66])
    tHex = bytes_to_str(tmp[70:102])
#     print(len(cHex))
#     print(len(tHex))
    tmp = encrypt('b'*32)
    c2Hex = bytes_to_str(tmp[2:66])
    t2Hex = bytes_to_str(tmp[70:102])

    cipher = bytes.fromhex(cHex)
    cipher2 = bytes.fromhex(c2Hex)
    flag = bytes.fromhex(flag_hex)
    addtion = b""
    poly1 = build_poly(addtion,cipher,x,a)
    poly2 = build_poly(addtion,cipher2,x,a)
    flag_poly = build_poly(addtion,flag,x,a)
    T1 = int_to_poly(int(tHex,16),a)
    T2 = int_to_poly(int(t2Hex,16),a)
    poly = poly1+poly2+T1+T2
    for H,_ in poly.roots():
        S = poly1(H)+T1
        T = flag_poly(H)+S
        tag = hex(poly_to_int(T))[2:]
        decrypt(flag_hex,tag)
        
attack()

