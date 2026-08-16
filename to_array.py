def to_array(s):
    a=[]
    for i in range(len(s)):
        if s[i]=='d' and s[i+1]=='b' and s[i+2]==' ':
            x=s[i+3:i+7]
            if x[-1]=='h':
                a.append(int(x[:-1],16))
            else:
                a.append(int(x,16))
    return a
s='''db    1
.data:000000000021D023                 db    1
.data:000000000021D024                 db    1
.data:000000000021D025                 db    1
.data:000000000021D026                 db    1
.data:000000000021D027                 db    0
.data:000000000021D028                 db    0
.data:000000000021D029                 db    0
.data:000000000021D02A                 db    0
.data:000000000021D02B                 db    0
.data:000000000021D02C                 db    1
.data:000000000021D02D                 db    1
.data:000000000021D02E                 db    1
.data:000000000021D02F                 db    1
.data:000000000021D030                 db    1
.data:000000000021D031                 db    0
.data:000000000021D032                 db    1
.data:000000000021D033                 db    1
.data:000000000021D034                 db    1
.data:000000000021D035                 db    0
.data:000000000021D036                 db    1
.data:000000000021D037                 db    1
.data:000000000021D038                 db    0
.data:000000000021D039                 db    0
.data:000000000021D03A                 db    0
.data:000000000021D03B                 db    0
.data:000000000021D03C                 db    1
.data:000000000021D03D                 db    1
.data:000000000021D03E                 db    1
.data:000000000021D03F                 db    0
.data:000000000021D040                 db    0
.data:000000000021D041                 db    1
.data:000000000021D042                 db    0
.data:000000000021D043                 db    1
.data:000000000021D044                 db    1
.data:000000000021D045                 db    0
.data:000000000021D046                 db    1
.data:000000000021D047                 db    1
.data:000000000021D048                 db    1
.data:000000000021D049                 db    1
.data:000000000021D04A                 db    0
.data:000000000021D04B                 db    1
.data:000000000021D04C                 db    0
.data:000000000021D04D                 db    0
.data:000000000021D04E                 db    1
.data:000000000021D04F                 db    0
.data:000000000021D050                 db    1
.data:000000000021D051                 db    1
.data:000000000021D052                 db    1
.data:000000000021D053                 db    1
.data:000000000021D054                 db    0
.data:000000000021D055                 db    1
.data:000000000021D056                 db    1
.data:000000000021D057                 db    0
.data:000000000021D058                 db    1
.data:000000000021D059                 db    0
.data:000000000021D05A                 db    0
.data:000000000021D05B                 db    1
.data:000000000021D05C                 db    1
.data:000000000021D05D                 db    1
.data:000000000021D05E                 db    0
.data:000000000021D05F                 db    0
.data:000000000021D060                 db    0
.data:000000000021D061                 db    0
.data:000000000021D062                 db    1
.data:000000000021D063                 db    1
.data:000000000021D064                 db    0
.data:000000000021D065                 db    1
.data:000000000021D066                 db    1
.data:000000000021D067                 db    1
.data:000000000021D068                 db    1
.data:000000000021D069                 db    1
.data:000000000021D06A                 db    0
.data:000000000021D06B                 db    1
.data:000000000021D06C                 db    1
.data:000000000021D06D                 db    1
.data:000000000021D06E                 db    0
.data:000000000021D06F                 db    0
.data:000000000021D070                 db    0
.data:000000000021D071                 db    1
.data:000000000021D072                 db    1
.data:000000000021D073                 db    0
.data:000000000021D074                 db    0
.data:000000000021D075                 db    1
.data:000000000021D076                 db    1
.data:000000000021D077                 db    1
.data:000000000021D078                 db    1
.data:000000000021D079                 db    0
.data:000000000021D07A                 db    0
.data:000000000021D07B                 db    0
.data:000000000021D07C                 db    0
.data:000000000021D07D                 db    0
.data:000000000021D07E                 db    1
.data:000000000021D07F                 db    1
.data:000000000021D080                 db    1
.data:000000000021D081                 db    0
.data:000000000021D082                 db    1
.data:000000000021D083                 db    0
.data:000000000021D084                 db    0
.data:000000000021D085                 db    0
.data:000000000021D086                 db    0
.data:000000000021D087                 db    0'''
print(to_array(s))
