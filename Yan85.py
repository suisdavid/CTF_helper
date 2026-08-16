from pwn import *
code=[32, 8, 106, 4, 8, 104, 32, 2, 4, 64, 16, 32, 4, 8, 1, 4, 64, 16, 1, 8, 67, 0, 1, 1, 1, 8, 79, 0, 1, 1, 1, 8, 82, 0, 1, 1, 1, 8, 82, 0, 1, 1, 1, 8, 69, 0, 1, 1, 1, 8, 67, 0, 1, 1, 1, 8, 84, 0, 1, 1, 1, 8, 33, 0, 1, 1, 1, 8, 32, 0, 1, 1, 1, 8, 89, 0, 1, 1, 1, 8, 111, 0, 1, 1, 1, 8, 117, 0, 1, 1, 1, 8, 114, 0, 1, 1, 1, 8, 32, 0, 1, 1, 1, 8, 102, 0, 1, 1, 1, 8, 108, 0, 1, 1, 1, 8, 97, 0, 1, 1, 1, 8, 103, 0, 1, 1, 1, 8, 58, 0, 1, 1, 1, 8, 10, 0, 1, 1, 8, 8, 20, 32, 8, 1, 8, 32, 1, 1, 8, 47, 8, 8, 128, 8, 2, 1, 1, 8, 102, 8, 8, 129, 8, 2, 1, 1, 8, 108, 8, 8, 130, 8, 2, 1, 1, 8, 97, 8, 8, 131, 8, 2, 1, 1, 8, 103, 8, 8, 132, 8, 2, 1, 1, 8, 0, 8, 8, 133, 8, 2, 1, 32, 8, 128, 4, 8, 0, 4, 32, 1, 4, 8, 0, 4, 64, 16, 8, 8, 255, 32, 8, 0, 32, 64, 1, 1, 32, 1, 4, 8, 0, 4, 64, 16, 8, 8, 0, 8, 64, 1, 32, 8, 1, 8, 32, 1, 32, 8, 0, 2, 32, 0, 0, 1, 32, 0, 1, 4, 0, 1, 8, 8, 1, 0, 4, 1, 0, 32, 1, 0, 64, 8, 91, 32, 8, 48, 4, 8, 109, 8, 8, 9, 1, 8, 2, 1, 64, 64, 0, 1, 1, 64, 8, 138, 8, 8, 0, 1, 128, 8, 1, 8, 4, 16, 4, 1, 1, 8, 160, 10, 4, 1, 1, 8, 116, 8, 8, 107, 8, 2, 1, 1, 8, 10, 8, 8, 108, 8, 2, 1, 1, 8, 98, 8, 8, 109, 8, 2, 1, 1, 8, 244, 8, 8, 110, 8, 2, 1, 1, 8, 124, 8, 8, 111, 8, 2, 1, 1, 8, 72, 8, 8, 112, 8, 2, 1, 1, 8, 217, 8, 8, 113, 8, 2, 1, 1, 8, 170, 8, 8, 114, 8, 2, 1, 1, 8, 57, 8, 8, 115, 8, 2, 1, 1, 8, 213, 8, 8, 116, 8, 2, 1, 1, 8, 48, 8, 8, 117, 8, 2, 1, 64, 8, 189, 32, 64, 8, 4, 64, 8, 1, 8, 255, 32, 64, 1, 4, 64, 1, 0, 1, 32, 0, 1, 4, 32, 16, 32, 4, 16, 4, 32, 128, 4, 4, 1, 0, 32, 1, 0, 1, 8, 158, 1, 4, 1, 1, 8, 255, 8, 64, 1, 1, 8, 0, 8, 128, 1, 1, 8, 140, 1, 4, 1, 1, 1, 8, 64, 1, 0, 4, 8, 1, 4, 64, 16, 1, 8, 73, 0, 1, 1, 1, 8, 78, 0, 1, 1, 1, 8, 67, 0, 1, 1, 1, 8, 79, 0, 1, 1, 1, 8, 82, 0, 1, 1, 1, 8, 82, 0, 1, 1, 1, 8, 69, 0, 1, 1, 1, 8, 67, 0, 1, 1, 1, 8, 84, 0, 1, 1, 1, 8, 33, 0, 1, 1, 1, 8, 10, 0, 1, 1, 8, 8, 11, 32, 8, 1, 8, 32, 1, 32, 8, 1, 2, 32, 0, 0, 1, 32, 0, 1, 4, 0, 1, 8, 4, 8, 1, 4, 64, 16, 1, 8, 75, 0, 1, 1, 1, 8, 69, 0, 1, 1, 1, 8, 89, 0, 1, 1, 1, 8, 58, 0, 1, 1, 1, 8, 32, 0, 1, 1, 8, 8, 5, 32, 8, 1, 8, 32, 1, 8, 1, 0, 4, 1, 0, 32, 1, 0, 0, 1, 32, 0, 1, 4, 0, 1, 8, 4, 8, 48, 8, 8, 11, 32, 8, 0, 1, 32, 1, 8, 1, 0, 4, 1, 0, 32, 1, 0, 64, 8, 84, 0]
reg_name={32:'a',4:'b',8:'c',1:'d',16:'s',64:'i',2:'f'}
val={'a':0,'b':0,'c':0,'d':0,'s':0,'i':0,'f':0}
data=[0]*10000
def get_code(s):
    a=[]
    for i in range(len(s)):
        if s[i]=='d' and s[i+1]=='b' and s[i+2]==' ':
            t=s[i+3:i+7]
            if t[-1]=='h':
                a.append(int(t[:-1],16))
            else:
                a.append(int(t))
    return a

def stk(a,b):
    if b:
        print("Push",reg_name[b])
        val['s']+=1
        data[val['s']]=val[reg_name[b]]
    if a:
        print("Pop",reg_name[a])
        val[reg_name[a]]=data[val['s']]
        val['s']-=1
def mov(a,b):
    print("Mov",reg_name[a],b)
    val[reg_name[a]]=b
def add(a,b):
    print("Add",reg_name[a],reg_name[b])
    val[reg_name[a]]=(val[reg_name[a]]+val[reg_name[b]])%256
def stm(a,b):
    print("*",reg_name[a],"=",reg_name[b])
    data[val[reg_name[a]]]=val[reg_name[b]]
def ldm(a,b):
    print(reg_name[a],"=*",reg_name[b])
    val[reg_name[a]]=data[val[reg_name[b]]]
def cmp(a,b):
    print("Cmp",reg_name[a],reg_name[b])
    input()
    val['f']=(val[reg_name[a]]!=val[reg_name[b]])
def jmp(a,b):
    if a and val['f']==0:
        print("Jmp", val[reg_name[b]])
        val['i']=val[reg_name[b]]
def sys(a,b):
    if a==32:
        print("Read_code to ",3*val['b'],",maxlen=",val['c'])
        x=input()
        if len(x)>val['c']:
            x=x[:val['c']]
        for i in range(len(x)):
            code[3*val['b']+i]=ord(x[i])
        val[reg_name[b]]=len(x)
    elif a==1:
        print("Read_Memory to ",val['b'],",maxlen=",val['c'])
        input()
        x='b\xf4|H\xd9\xaa9\xd50t\n'
        if len(x)>val['c']:
            x=x[:val['c']]
        for i in range(len(x)):
            data[val['b']+i]=ord(x[i])
        val[reg_name[b]]=len(x)
    elif a==8:
        print("Write_memory",val['b'],"maxlen=",val['c'])
        res=''
        for i in range(val['c']):
            res+=chr(data[val['b']+i])
        print(res)
    elif a==2:
        print("exit")
        exit(0)
    else:
        print("Unknown")
        exit(0)

func={1:stk,2:stm,4:jmp,8:mov,16:ldm,32:sys,64:add,128:cmp}
def solve(op,a,b):
    print(f"a:{val['a']},b:{val['b']},c:{val['c']},d:{val['d']},s:{val['s']},i:{val['i']},f:{val['f']}")
    func[op](a,b)
while True:
    val['i']+=1
    solve(code[val['i']*3-2],code[val['i']*3-3],code[val['i']*3-1])
    
