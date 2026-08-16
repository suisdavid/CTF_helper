#!/usr/bin/env python
# -*- coding:utf-8 -*-
 
from PIL import Image
data=[] 
a =[1, 196, 5, 244, 87, 212, 92, 81, 81, 77, 69, 69, 181, 21, 245, 183, 208, 21, 64, 127, 239, 255, 4, 106, 173, 217, 64, 216, 83, 124, 235, 128, 165, 29, 45, 239, 253, 173, 80, 18, 56, 223, 112, 163, 69, 61, 229, 20, 60, 116, 82, 59, 223, 74, 199, 1, 112, 47, 255, 255, 240]
for each in a:
    s=[]
    x=each
    for i in range(8):
        s.append(x%2)
        x>>=1
    for i in range(7,-1,-1):
        data.append(s[i])
top = len(data)//21
n = 0
for w in range(21,top+1):
    n += 1
    h = len(data) // w + 1
    print(str(n)+'.png:',w,'*',h)
    img = Image.new('1', (w, h), 255)
    for i in range(len(data)):
        img.putpixel((i % w, i // w), int(data[i]) * 255)
    img.save(str(n)+'.png')
