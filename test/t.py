#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/20 22:21
# @Author  : Pointer
# @File    : t.py
# @Software: PyCharm


import asyncio
from asyncTask import at
from aiohttp import ClientSession


# max_connections redis-pool 的最大连接数 currt 并发数 ，req_queue->存储在redis上的任务队列
@at("req_queue", max_connections=30, currt=30)
async def request(url):
    async with ClientSession() as s:
        async with await s.get(url) as r:
            print(r)

async def mian():
    await request.push("http://bing.com")

    await request.close()

if __name__ == '__main__':
    asyncio.run(mian())