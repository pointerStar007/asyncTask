#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/19 17:24
# @Author  : Pointer
# @File    : simplebase64.py
# @Software: PyCharm
import base64

def encode_bs64(data):
    # 原始数据（可以是字符串、字节等）

    # 将字符串编码为字节（如果它还不是）
    if isinstance(data, str):
        data = data.encode('utf-8')
    # 使用base64进行编码
    encoded_data = base64.b64encode(data)
    return encoded_data.decode("utf8")

def decode_bs64(encoded_data):
    decoded_data = base64.b64decode(encoded_data)

    # 如果原始数据是字符串，则需要再次解码为字符串
    decoded_data = decoded_data.decode('utf-8')

        # 打印解码后的数据
    return decoded_data

if __name__ == '__main__':
    es = encode_bs64("77859")
    print(es)
    es = decode_bs64(es)
    print(es)
