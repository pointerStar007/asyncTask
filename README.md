# Project description

| 欢迎选用 asyncTask , Welcome to asyncTask

- 这是一个基于原生 asyncio 和 redis-py 构建的轻量级异步分布式任务库，方便你可以构建 asyncio 的分布式任务系统。
- This is a lightweight asynchronous distributed task library built on top of native asyncio and redis-py, so that you
  can build asyncio's distributed task system.

# Install

~~~
pip install asyncTaskmini
~~~

# example

- QuickStart

~~~python

import asyncio
from asyncTaskmini import at
from aiohttp import ClientSession


# max_connections redis-pool 的最大连接数 currt 并发数 ，req_queue->存储在redis上的任务队列
@at("req_queue", max_connections=30, currt=30)
async def request(url):
  async with ClientSession() as s:
    async with await s.get(url) as r:
      print(r)


# req_queue2 is which queue your want to Save in for a redis -list
# max_connections the max_connections for the redis-pool
# currt The number of tasks that a worker can execute at the same time,
# You can think of it as the number of concurrent transactions
@at("req_queue2", max_connections=30, currt=30)
async def request2(url):  # 
  async with ClientSession() as s:
    async with await s.get(url) as r:
      print(r)


async def main():
  url = "https://baidu.com"
  for i in range(1000):
    await request2.push(url)
    await request.push(url)

  await asyncio.gather(*[request.exec(), request2.exec()])  # 监听执行,worker 从redis 的对应 queue 中拉取任务进行载入,阻塞


if __name__ == '__main__':
  asyncio.run(main())
~~~

- In particular, only the parameters currently supported are common data types in python, such as string, int, float,
  dict, set, tuple, etc., but do not include object types, if you want to use custom types as parameters, he may not be
  applicable, because the serialization used by AsyncTask is msgpack, it does not currently support object types, I have
  tried to use pickle before, but there are still some problems, Therefore, custom object types are not supported for
  the time being


- 特别说明，目前仅支持的参数为python常见的数据类型，如 字符串、int、float、dict、set、tuple 等，但是不包括对象类型，如果你想用自定义类型作为参数，他可能不适用，因为 AsyncTask 使用的序列化是
  msgpack，它目前不支持对象类型，之前尝试过使用 pickle ，但是还有一些问题存在，所以暂时不支持自定义的对象类型


- When you run it for the first time, a log folder will be created in the path of the script you executed, which will be
  used to store the relevant log files; and the associated configuration file to quickly configure the connection to
  redis, if you don't need the console to output the relevant log information, you can set the log_to_console to True


- 当你第一次运行，会在你执行的脚本路径中创建一个日志文件夹，用于存放相关日志文件；以及相关的配置文件，用于快速配置 redis 的连接，如果你不需要在控制台输出相关的日志信息，你可以将log_to_console设置为True


- If you want to use custom logs, you can override `asyncTask.utils.logs.get_logger`
  like `def get_logger(name=None, level=logging.INFO):`


- 关于日志，使用了 colorlog, 并且跟踪了计算机的 ip、Pid 、job的执行对象和参数等，如果你想用自定义日志，你可以覆盖 `asyncTask.utils.logs.get_logger`
  like `def get_logger(name=None, level=logging.INFO):`

# Distributed tasks

- First of all, you need to have a Redis, which currently only supports Redis, and your cluster can access a Redis
  service.


- 首先你需要有一个redis，目前只支持redis，你的集群都可以访问的一个redis 服务。


- Then you can plan which nodes are used as pushers and which nodes are used as workers, and of course you can also
  start multiple processes on the same computer to act as pushers and workers respectively


- 然后你可以规划哪些节点作为pusher 哪些节点作为 worker，当然你也可以在同一台计算机中开启多个进程分别扮演pusher 和worker

## pusher

- The pusher is dedicated to the initial task, and this task of yours may form a chain of diffuse tasks.


- pusher 专门负责初始的任务，你的这个任务可能会形成一个扩散的任务链。

~~~python

import asyncio
from asyncTaskmini import at
from aiohttp import ClientSession


# max_connections redis-pool 的最大连接数 currt 并发数 ，req_queue->存储在redis上的任务队列
@at("req_queue", max_connections=30, currt=30)
async def request(url):
  async with ClientSession() as s:
    async with await s.get(url) as r:
      # do some thing
      await request2.push(url)
      #  If you have resolved the sub-link here, 
      #  you can directly push the sub-linked task here 
      #  and share it with all workers in the cluster


@at("req_queue2", max_connections=30, currt=30)
async def request2(url):  # 假如这是一个子链接的任务
  async with ClientSession() as s:
    async with await s.get(url) as r:
      print(r)


async def main():
  url = "https://baidu.com"
  await request.push(url)  # 在此 push 你的首个任务， Push your first task
  # or
  await asyncio.gather(*[request.push(url) for i in range(100)])
  # 假设你有100个链接要分发，你可以这样并发的分发
  # Let's say you have 100 links to distribute, you can distribute them concurrently

  # async with request as r:  # 异步上下文管理器，隐式管理自动关闭，但是并不推荐
  #     for i in range(10000):
  #         await r.push(url)

  # Asynchronous Context Manager, implicit management is automatically turned off, but not recommended

  # It is recommended to use Display Release
  await request.close()  # 释放资源, 显式管理，过多 job 时推荐


if __name__ == '__main__':
  asyncio.run(main())
~~~

## worker

- Responsible for pulling task parameters from the Redis task queue and rebuilding the task and execution


- 负责从redis的任务队列中拉取任务参数并重新构建Task和执行

~~~python

import asyncio
from asyncTaskmini import at
from aiohttp import ClientSession


# max_connections redis-pool 的最大连接数 currt 并发数 ，req_queue->存储在redis上的任务队列
@at("req_queue", max_connections=30, currt=30)
async def request(url):
  async with ClientSession() as s:
    async with await s.get(url) as r:
      # do some thing
      await request2.push(url)
      #  If you have resolved the sub-link here, 
      #  you can directly push the sub-linked task here 
      #  and share it with all workers in the cluster


@at("req_queue2", max_connections=30, currt=30)
async def request2(url):  # 假如这是一个子链接的任务
  async with ClientSession() as s:
    async with await s.get(url) as r:
      print(r)


async def main():
  await asyncio.gather(*[request.exec(), request2.exec()])  # 监听执行|Listen to execution


if __name__ == '__main__':
  asyncio.run(main())
~~~

- worker 你可以部署到任何可以访问到 这个redis中任务队列的地方，你无需担心计算机故障或者程序故障导致的中断，任何中断都不会使得任务丢失，除非队列被删除或者redis缓存被清除。因为worker 从redis中拉取任务的同时要同时添加到一个set中缓存，这样才算成功拉取一个参数，如果中途程序被中断，新开启的worker会重新拉取缓冲中的所有任务，这里可能会有一些任务被其他worker执行，导致重复执行，所以可能会有重复的数据，但绝对不会丢失。 


- Workers can be deployed anywhere you can access the task queue in Redis, you don't have to worry about interruptions caused by computer failures or program failures, and any interruption will not cause tasks to be lost unless the queue is deleted or the Redis cache is cleared. Because the worker pulls the task from Redis and adds it to a set cache at the same time, so that a parameter can be successfully pulled, if the program is interrupted in the middle of the process, the newly opened worker will re-pull all the tasks in the buffer, and there may be some tasks that are executed by other workers, resulting in repeated execution, so there may be duplicate data, but it will never be lost. 


- 后续版本，内容：主要是在 对象序列化、任务消息中间件 和 任务流量监控方面【目前存储在redis，后续可能会加入Web页面监控】等进行优化。


- Subsequent versions, content: mainly in object serialization, task message middleware and task traffic monitoring [currently stored in redis, may be added in the future web page monitoring] and other optimizations.