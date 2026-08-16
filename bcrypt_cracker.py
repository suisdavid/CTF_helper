import bcrypt
import string
s=string.ascii_letters+string.digits+"!?_,"
hashed = b'$2b$10$Ni0U3D5ibg1NY6G/k8CDHuXG7m/WNZzuV/9PDPnRzgKs4wUjaTwGO'

ls=[
    "jenny"      
]
for i in ls:
    print(bcrypt.checkpw(i.encode('utf-8'),hashed))
