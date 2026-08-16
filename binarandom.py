import random
from SECRET import flag

def random_shuffler(a, seed):
    random.seed(seed)
    random.shuffle(a)
    return a

p=[]
for i in flag:
    now = bin(ord(i)).replace('0b', '')
    if len(now) < 7:
        now = '0'*(7-len(now)) + now
    p.append(now)

d=['','','','','','','']
for i in p:
    for j in range(7):
        d[j] += i[j]

seed=random.randint(114514,1919810)
for i in range(7):
    now = random_shuffler(list(d[i]), seed)
    print(int(''.join(now), 2))
"""
output:
502000127
401997630
180303717
474190135
138669659
178962539
254230901
"""