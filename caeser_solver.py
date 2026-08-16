from PIL import Image
import numpy as np
image1=Image.open("bliss.png")
image2=Image.open("bliss_shifted.png")
array1=np.array(image1)
array2=np.array(image2)
n=len(array1)
ans=[0]*n
for i in range(n):
    a1=array1[i]
    a2=array2[i]
    for j in range(len(a1)):
        flg=1
        for k in range(len(a1)):
            if (a2[k]==a1[(j+k)%len(a1)]).all()==0:
                flg=0
                break
        if flg==1:
            print(i,j)
            ans[i]=j
