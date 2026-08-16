import string
S=string.ascii_letters+string.digits+'}_!?'
class LCG:
    def __init__(self,s1,s2,s3):
        self.s1=11
        self.s2=29
        self.s3=7
        self.m1=95
        self.m2=37
        self.m3=19
        self.a1=s1
        self.a2=s2
        self.a3=s3
        self.alphabet='''G!{Qq)EPU-M7yNAKnF%fS=\Z?;+.T2/8Lx65'@*VBw,#k:|~Dr`eOa9H"hb>3^<Jp}[&$iXogzl4vWu(tsc]1YmC_RI0jd'''
    def next(self):
        self.s1=(self.s1*self.a1)%self.m1
        self.s2=(self.s2*self.a2)%self.m2
        self.s3=(self.s3*self.a3)%self.m3
        return self.alphabet[(self.s1-self.s2+self.s3)%(self.m1-1)]

def calc(b1,b2,b3):
    lcg=LCG(b1,b2,b3)
    flag=''
    for i in range(100):
        flag+=lcg.next()
    if flag.find('RS{')!=-1:
        print(flag)
for b1 in range(95):
    for b2 in range(37):
        for b3 in range(19):
                calc(b1,b2,b3)
