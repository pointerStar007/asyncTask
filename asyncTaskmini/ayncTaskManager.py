#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/19 19:02
# @Author  : Pointer
# @File    : AyncTaskManager.py
# @Software: PyCharm
# import asyncio
import asyncio
import json
import os
import time
from datetime import datetime
from asyncTaskmini.async_task import TaskStus
from asyncTaskmini.async_queue import RedisTaskQueue
from utils.logs import get_logger, get_local_ip
from utils.singletion import Singletion
import schedule
from redis import Redis
from config.config import sys_config


class TryLog:

    def __init__(self, queue):
        self.logger = get_logger(f'{queue.task_queue_name}_exec')

    def try_log(self, status, message):
        try:
            match status:
                case TaskStus.Failure.value:
                    self.error(message)
                case TaskStus.Finish.value:
                    self.info(message)
                case _:
                    self.waring(message)
        except:
            self.try_log(status, message)
        # try:
        #     self.log[status](message)
        # except:  # 防止文件分割时导致访问受限
        #     self.try_log(status, message)

    def info(self, message):
        try:
            self.logger.info(message)
        except:
            self.info(message)

    def debug(self, message):
        try:
            self.logger.debug(message)
        except:
            self.debug(message)

    def waring(self, message):
        try:
            self.logger.warning(message)
        except:
            self.waring(message)

    def error(self, message):
        try:
            self.logger.error(message)
        except:
            self.error(message)


async def async_task_exec(queue, currt=50):
    log = TryLog(queue)
    count_job = {
        "run_count_min": 0,
        "err_count_min": 0,
        "success_count_min": 0
    }

    task_list = await queue.pull_running()

    def clear_count():
        redis = Redis.from_url(queue.connect_string)
        total = redis.llen(queue.task_queue_name)  # 剩余
        speed = round(count_job['run_count_min'] / 60)  # 每秒执行数
        total_seconds = total / speed if speed != 0 else 0  # 剩余执行时间 / S
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        log.info(
            f"async_queue | {queue.task_queue_name} run_count/min : {count_job['run_count_min']}, success_count_min/min : {count_job['success_count_min']}, err_count/min : {count_job['err_count_min']},tasks remaining:{total}"
            f"exec speed:{speed}/s,Time remaining:{hours}:{minutes}:{seconds}")
        run_count = {
            "IP": get_local_ip(),
            "PID": os.getpid(),
            "queue_name": queue.task_queue_name,
            "run_count": count_job["run_count_min"],
            "success_count_min": count_job["success_count_min"],
            "err_count": count_job["err_count_min"],
            "task_remaining": total,
            "exec_speed": f"{speed}/s",
            "time_remaining": f"{hours}:{minutes}:{seconds}",
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        redis.lpush(f"{queue.task_queue_name}_running_count", json.dumps(run_count, ensure_ascii=True))
        count_job["run_count_min"] = 0
        count_job["success_count_min"] = 0
        count_job["err_count_min"] = 0

    schedule.every(1).minute.do(clear_count)
    while True:
        schedule.run_pending()
        task_list.extend([await queue.pull() for i in range(currt)])
        task_list = [do_task(log, queue, task, count_job) for task in task_list if task]
        await asyncio.gather(*task_list)
        task_list.clear()  # 清空



async def do_task(log, queue, task, count_job):
    if task:
        start = time.time()
        await task.run()
        res = task.getResult()
        log.try_log(task.status.value,
                    f"Task:{task.async_fun}|args:{task.args},kwargs:{task.kwargs}|status:{task.status}|res:{res},runtime:{round(time.time() - start, 2)}s")
        count_job["run_count_min"] += 1
        if task.status.value == TaskStus.Failure.value:
            count_job["err_count_min"] += 1
            await queue.retry(task)  # 重发
        else:
            count_job["success_count_min"] += 1
            await queue.finish(task)


class AyncTaskManager(Singletion):
    # max_connections = sys_config["MAX_CONNECTIONS"]
    # redis_connect = sys_config["REDIS_CONNECT"]
    __jobs = {}
    __logs = {}
    __currts = {}

    def __init__(self, max_connections=None, redis_connect=None):
        self.max_connections = max_connections if max_connections else sys_config["MAX_CONNECTIONS"]
        self.redis_connect = redis_connect if redis_connect else sys_config["REDIS_CONNECT"]

    def enroll(self, job, queue_name, currt=10, redis_connect=None, max_connections=None):
        redis_connect = redis_connect if redis_connect else self.redis_connect
        max_connections = max_connections if max_connections else self.max_connections
        queue = RedisTaskQueue(job, redis_connect, queue_name, max_connections=max_connections)
        self.__jobs[job] = queue
        self.__logs[job] = get_logger(f"{queue_name}_push")
        self.__currts[job] = currt

    async def exec(self):  # 执行任务监听
        async def async_generator():
            for job in self.__jobs:
                yield job

        async for job in async_generator():
            await async_task_exec(self.__jobs[job], self.__currts[job])

    async def exec_job(self, job):
        await async_task_exec(self.__jobs[job], self.__currts[job])

    async def push(self, job, *args, **kwargs):  # 推送任务
        try:
            await self.__jobs[job].push(*args, **kwargs)
        except Exception as e:
            self.__logs[job].error(f"{e}|{args}|{kwargs}")
        self.__logs[job].info(f"you sucess push one task |{job}|{args}|{kwargs}")

    async def close(self, job):
        await self.__jobs[job].pool.aclose()


# 装饰器
def at(queue_name, currt=10, redis_connect=None, max_connections=None):
    async_task_manager = AyncTaskManager()  # 管理器

    def decorator(job):
        async_task_manager.enroll(job, queue_name, currt, redis_connect, max_connections)  # 注册到管理器

        class AsyncTask(Singletion):
            is_close = False

            def __call__(self, *args, **kwargs):
                return job(*args, **kwargs)  # 同步执行，返回原本的执行方式

            async def push(self, *args, **kwargs):
                if self.is_close:
                    raise RuntimeError("the redis-pool is closed")
                await async_task_manager.push(job, *args, **kwargs)

            async def exec(self):
                if self.is_close:
                    raise RuntimeError("the redis-pool is running")
                logger = get_logger()
                logger.info(f"{queue_name} is running")
                await async_task_manager.exec_job(job)

            async def close(self):
                logger = get_logger()
                logger.info(f"{queue_name} is closed")
                await async_task_manager.close(job)
                self.is_close = True

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                await async_task_manager.close(job)
                self.is_close = True

        async_task = AsyncTask()
        return async_task

    return decorator


if __name__ == '__main__':
    pass
    # queue = RedisTaskQueue(job, "redis://localhost:6380", "test_queue", max_connections=50)
    # asyncio.run(async_task_exec(queue))
