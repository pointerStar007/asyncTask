#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/19 13:43
# @Author  : Pointer
# @File    : task.py
# @Software: PyCharm
import time
from enum import Enum
from utils.logs import get_logger


class TaskStus(Enum):
    Pending = 0
    Running = 1
    Finish = 2
    Failure = -1


class Task:  # 基础任务
    task_results: object  # 任务结果
    status: TaskStus

    def __init__(self, async_func, params):

        if not callable(async_func):
            raise TypeError("The desired argument is a callable")
        self.async_fun = async_func
        self.params = params
        self.args = params["args"]
        self.kwargs = params["kwargs"]
        self.status = TaskStus.Pending

    async def run(self):  # 任务体
        self.status = TaskStus.Running
        try:
            self.task_results = await self.async_fun(*self.args, **self.kwargs)
        except Exception as e:
            logger = get_logger(self.async_fun.__name__)
            logger.error(f"Task:{self.async_fun.__name__},error:", e)
            self.status = TaskStus.Failure
            return
        self.status = TaskStus.Finish

    def params_to_dict(self):
        return self.params

    def getResult(self):
        while True:
            if self.status == TaskStus.Finish:
                return self.task_results
            elif self.status == TaskStus.Failure:
                return TaskStus.Failure
