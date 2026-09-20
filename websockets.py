import requests
import websocket
import json,hashlib
host="fair-gambling-32ee4c6ebd67f772-global.challs.brunnerne.xyz"
hashes=[]
emojis=["🍒", "🍋", "🍇",  "🍉", "🔔",  "⭐",  "💎"]
for each in emojis:
    hashes.append(hashlib.sha1((each+each+each).encode('utf-8')).hexdigest())
ws = websocket.create_connection(f"wss://{host}/ws")

# 发送 JSON
# 接收响应
response = json.loads(ws.recv())
while True:
    if response["next"]["hash"] in hashes:
        sid=response["next"]["sid"]
        ws.send(json.dumps({"type": "spin", "sid": sid}))
        response=json.loads(ws.recv())
        print(response["cash"])
        if response["cash"]>=1000000:
            break
    else:
        ws.send(json.dumps({"type": "spin", "sid": "3734b633-e8a9-4d35-87a7-fae3e40177ab"}))
        response=json.loads(ws.recv())
ws.send(json.dumps({"type": "redeem"}))
print(ws.recv())
ws.close()