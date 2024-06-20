#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/19 17:15
# @Author  : Pointer
# @File    : simplemd5.py
# @Software: PyCharm


import hashlib


def compute_md5(data:str):
    # 创建一个md5 hash对象
    md5_hash = hashlib.md5()
    # 更新hash对象，传入要哈希的数据（bytes类型）
    md5_hash.update(data.encode('utf-8'))  # 如果数据是字符串，需要先编码为bytes
    # 完成计算并返回摘要（hexdigest）
    return md5_hash.hexdigest()

if __name__ == '__main__':
    md_ = compute_md5("hello")
    print(md_)
