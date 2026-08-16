import paramiko

# 创建 SSH 客户端
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动接受主机密钥

# 连接（密码认证）
client.connect(
    hostname='111.186.57.85',
    port=40150,
    username='guest',
    password='guest',
    timeout=10
)

# 执行命令
stdin, stdout, stderr = client.exec_command(' ')
print(stdout.read())
stdin, stdout, stderr = client.exec_command(' ')
print(stdout.read())
# 关闭连接
client.close()
