file="snake"
with open(file,'rb') as f:
    s=f.read()
with open('output','w') as f:
    f.write(s.hex())
