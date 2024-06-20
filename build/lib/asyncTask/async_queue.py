#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/19 13:49
# @Author  : Pointer
# @File    : queue.py
# @Software: PyCharm
from abc import ABCMeta, abstractmethod
from redis import asyncio as aioredis
from asyncTask.async_task import Task
import msgpack
import uuid


class TaskQueue(metaclass=ABCMeta):
    task_queue_name: str

    @abstractmethod
    async def push(self, *args, **kwargs):  # 将任务推送至消息中间件
        ...

    @abstractmethod
    async def pull(self):  # 从消息中间件中拉取一个Task,并保证数据不丢失，并返回
        ...

    @abstractmethod
    async def finish(self, task):
        ...

    @abstractmethod
    async def pull_running(self):
        ...

    async def retry(self, task):
        params = task.params_to_dict()
        del params["tag"]
        await self.push(*params["args"], **params["kwargs"]) # 重新推送
        await self.finish(task) # 清除缓存


class RedisTaskQueue(TaskQueue):

    def __init__(self, job, connect_string: str, task_queue_name: str, max_connections=10):
        if not callable(job):
            raise TypeError("The desired argument is a callable")
        self.job = job
        self.task_queue_name = task_queue_name
        self.connect_string = connect_string
        self.pool = aioredis.ConnectionPool.from_url(connect_string, max_connections=max_connections)

    async def push(self, *args, **kwargs):
        redis = aioredis.Redis(connection_pool=self.pool)
        await redis.rpush(self.task_queue_name, msgpack.packb({"args": args, "kwargs": kwargs,"tag":str(uuid.uuid4())})) # uuid 防止重复

    async def pull(self):
        redis = aioredis.Redis(connection_pool=self.pool)
        async with redis.pipeline(transaction=True) as pipe:
            params = await pipe.lpop(self.task_queue_name).execute()
            params = params[0]
            if params:
                await pipe.sadd(f"{self.task_queue_name}_running", params)  # 防丢失缓存
                await pipe.execute()
                params = msgpack.unpackb(params)

        return Task(self.job, params) if params else None

    async def pull_running(self):
        redis = aioredis.Redis(connection_pool=self.pool)
        params_set = await redis.smembers(f"{self.task_queue_name}_running")
        params_set = [msgpack.unpackb(param) for param in params_set]
        return [Task(self.job, params) for params in params_set]

    async def finish(self, task):
        redis = aioredis.Redis(connection_pool=self.pool)
        params = task.params_to_dict()
        await redis.srem(f"{self.task_queue_name}_running", msgpack.packb(params))


if __name__ == '__main__':
    pass
    # asyncio.run(main())
