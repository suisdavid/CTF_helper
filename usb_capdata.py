m={0x04:'a',0x05:'b',0x06:'c',0x07:'d',0x08:'e',0x09:'f',0x0a:'g',0x0b:'h',0x0c:'i',0x0d:'j',0x0e:'k',0x0f:'l',0x10:'m',0x11:'n',0x12:'o',0x13:'p',0x14:'q',0x15:'r',0x16:'s',0x17:'t',0x18:'u',0x19:'v',0x1a:'w',0x1b:'x',0x1c:'y',0x1d:'z',0x1e:'1',0x1f:'2',0x20:'3',0x21:'4',0x22:'5',0x23:'6',0x24:'7',0x25:'8',0x26:'9',0x27:'0',0x28:'\n',0x2c:' ',0x2d:'-',0x2e:'=',0x2f:'[',0x30:']',0x33:';',0x34:"'",0x36:',',0x37:'.',0x38:'/'}
r='';l=0
def shift(c):
    if ord(c)>=ord('A') and ord(c)<=ord('Z'):
        return c.lower()
    if ord(c)>=ord('a') and ord(c)<=ord('z'):
        return c.upper()
    if c=='-':
        return '_'
    if c=='[':
        return '{'
    if c==']':
        return '}'
    if c=='1':
        return '!'
    if c=='2':
        return '@'
    if c=='3':
        return '#'
    if c=='/':
        return '?'
    return c
for x in open('out.txt').read().split():
 if len(x)==16:
  b=bytes.fromhex(x)
  if b[2]and b[2]!=l and not any(b[3:]):
   l=b[2];c=m.get(b[2],'?');r+=shift(c)if b[0]&0x22 else c
print(r)
