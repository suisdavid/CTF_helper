#!/usr/bin/env python3
"""
DS_Store 递归分析脚本
用法: python3 ds_store_analyzer.py <目录路径>
"""
import os
import sys
import json
from collections import defaultdict

try:
    from ds_store import DSStore
except ImportError:
    print("[!] 请先安装: pip install ds-store")
    sys.exit(1)

def analyze_file(filepath):
    """分析单个 .DS_Store 文件"""
    results = []
    try:
        with DSStore.open(filepath, 'r+') as d:
            for item in d:
                code = item.code.decode('ascii', errors='replace')
                val = item.value
                if isinstance(val, bytes):
                    val_str = f"<BLOB:{len(val)}>"
                else:
                    val_str = val
                results.append({
                    'filename': item.filename,
                    'code': code,
                    'value': val_str
                })
    except Exception as e:
        return {'error': str(e)}
    return results

def recursive_analyze(root_dir):
    """递归分析目录下所有 .DS_Store"""
    all_data = {}
    for dirpath, _, filenames in os.walk(root_dir):
        if '.DS_Store' in filenames:
            full_path = os.path.join(dirpath, '.DS_Store')
            rel_path = os.path.relpath(full_path, root_dir)
            all_data[rel_path] = analyze_file(full_path)
    return all_data

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} <目录路径>")
        sys.exit(1)

    target = sys.argv[1]
    data = recursive_analyze(target)

    # 输出 JSON
    print(json.dumps(data, indent=2, default=str))

    # 输出摘要
    print(f"\n[*] 共分析 {len(data)} 个 .DS_Store 文件")
    for path, records in data.items():
        if 'error' in records:
            print(f"    [!] {path}: 解析失败 - {records['error']}")
        else:
            files = set(r['filename'] for r in records)
            print(f"    [+] {path}: {len(files)} 个项目")
