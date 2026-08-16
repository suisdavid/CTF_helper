import msoffcrypto
file=open('word','rb')
enc=msoffcrypto.OfficeFile(file)
enc.load_key(password="q1w2e3r4t5")

with open("decrypted.docx",'wb') as f:
    enc.decrypt(f)
file.close()
