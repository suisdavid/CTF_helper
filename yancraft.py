from pwn import *
reg={'a':8,'b':4,'c':16,'d':64,'s':32,'i':1,'f':2}
val={'a':0,'b':0,'c':0,'d':0,'s':0,'i':0,'f':0}
func={'mov':8,'add':64,'stk':128,'stm':1,'ldm':4,'cmp':2,'jmp':32,'sys':1,'open':16,'read_code':32,'read_memory':2,'write':8}
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
def sys_read_memory():
    payload=mov('a',0)+add('a','d')+mov('b',0)+mov('c',0xff)+p8(func['read_memory'])+p8(reg['d'])+p8(func['sys'])
    return payload
def sys_write():
    payload=mov('a',1)+mov('b',0)+mov('c',0xff)+p8(func['write'])+p8(reg['d'])+p8(func['sys'])
    return payload
def get(pos,val):
    return mov('a',pos)+mov('b',val)+stm('a','b')
def get_flag():
    payload=get(0,ord('/'))+get(1,ord('f'))+get(2,ord('l'))+get(3,ord('a'))+get(4,ord('g'))+get(5,0)
    payload+=sys_open(0)+sys_read_memory()+sys_write()
    return payload
payload=get_flag()
ans=b''
for i in range(len(payload)//3):
    ans+=p8(payload[i*3+1])+p8(payload[i*3])+p8(payload[i*3+2])
print(ans)
    
