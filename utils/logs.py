#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/19 20:48
# @Author  : Pointer
# @File    : logs.py
# @Software: PyCharm


import logging
import logging.handlers
import colorlog
import socket
import os
from config.config import sys_config


# 获取本地IP地址（IPv4）
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # 连接到Google的公共DNS服务器
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        return "Unknown"

    # 初始化colorama（仅在Windows上需要）


try:
    from colorama import init

    init(autoreset=True)
except ImportError:
    pass

logs = {}


def get_logger(name=None, level=logging.INFO):
    # 创建一个logger

    _name = name if name else __name__
    if _name in logs:  # 如果存在直接返回，保持证同名的 logger 只有一个
        return logs[_name]
    logger = logging.getLogger(_name)
    logs[_name] = logger  # 加入到字典
    logger.setLevel(level)
    # 设置额外的日志字段
    log_record_factory = logging.getLogRecordFactory()

    def custom_log_record_factory(*args, **kwargs):
        record = log_record_factory(*args, **kwargs)
        record.hostname = socket.gethostname()  # 主机名
        record.ip = get_local_ip()  # IP地址
        record.pid = os.getpid()  # 进程ID
        return record

    logging.setLogRecordFactory(custom_log_record_factory)
    # 创建一个formatter并添加到handler
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s %(asctime)s %(levelname)-8s%(reset)s| %(log_color)s [%(hostname)s:%(ip)s:%(process)d] PID:%(pid)s |%(log_color)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bold',
        },
        secondary_log_colors={

        },
        style='%',
    )

    # 创建一个handler，用于写入日志文件（这里我们写入到控制台）
    if name is not None:
        if not os.path.exists(f"logs/{name}_logs"):
            os.makedirs(f"logs/{name}_logs")
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | [%(hostname)s:%(ip)s:%(process)d] PID:%(pid)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S")
        fileHandler = logging.handlers.RotatingFileHandler(f'logs/{name}_logs/{name}.log', maxBytes=5 * 1024 * 1024,
                                                           backupCount=10)
        errorFileHandler = logging.handlers.RotatingFileHandler(f'logs/{name}_logs/{name}_error.log',
                                                                maxBytes=5 * 1024 * 1024, backupCount=10)
        fileHandler.setLevel(logging.INFO)
        errorFileHandler.setLevel(logging.ERROR)
        fileHandler.setFormatter(file_formatter)
        errorFileHandler.setFormatter(file_formatter)

        logger.addHandler(fileHandler)
        logger.addHandler(errorFileHandler)

    if sys_config["log_to_console"]: # 如果设置了这个选项将不输出到控制台
        return logger
    handler = logging.StreamHandler()
    # handler.setLevel(logging.INFO)

    # 将formatter添加到handler
    handler.setFormatter(formatter)

    # 给logger添加handler
    logger.addHandler(handler)
    return logger
