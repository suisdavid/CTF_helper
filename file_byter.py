with open("g",'r') as f:
    s=f.read()
with open("code",'wb') as f:
    f.write(bytes.fromhex(s))
