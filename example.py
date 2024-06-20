#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/20 13:37
# @Author  : Pointer
# @File    : example.py
# @Software: PyCharm

import asyncio
from asyncTaskmini import at
from aiohttp import ClientSession


# max_connections redis-pool 的最大连接数 currt 并发数 ，req_queue->存储在redis上的任务队列
@at("req_queue", max_connections=30, currt=30)
async def request(url):
    async with ClientSession() as s:
        async with await s.get(url) as r:
            print(r)


@at("req_queue2", max_connections=30, currt=30)
async def request2(url):
    async with ClientSession() as s:
        async with await s.get(url) as r:
            print(r)


# request.exec() 后 会在redis 中的 req_queue 拉取任务，并将拉取的 任务缓存到 {task_queue_name}_running 的 set 中
# 如果 任务顺利完成则会将完成的任务从 set 中剔除，如果 worker 被意外中断，则已经被拉取的任务不会丢失，等待新的 worker 启动时会读取 set 中的成员，并将其全部载入队列
# 如果有中断，重新启动的 worker 会读取启动时 redis 中对应的 set 所有的成员，这些成员有可能已经是 其他 worker 的任务，这意味着必定有一些 任务会被重复执行。
# request.push(url) # 会将任务推送到 req_queue


async def main():
    url = "https://baidu.com"
    for i in range(1000):
        await request2.push(url)
        await request.push(url)
    # await request2.push(url)
    # await request.push(url)
    # async with request as r:  # 异步上下文管理器，隐式管理自动关闭
    #     for i in range(10000):
    #         await r.push(url)
    # await request2.close()  # 释放资源, 显式管理，过多 job 时推荐，
    # await request.close()  # 释放资源, 显式管理，过多 job 时推荐，
    # # # # await request2.exec()  # 监听执行,worker 从redis 的对应 queue 中拉取任务进行载入
    await asyncio.gather(*[request.exec(), request2.exec()])  # 监听执行,worker 从redis 的对应 queue 中拉取任务进行载入,阻塞


if __name__ == '__main__':
    asyncio.run(main())

