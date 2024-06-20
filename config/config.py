#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/20 13:26
# @Author  : Pointer
# @File    : config.py
# @Software: PyCharm
import os
import shutil
import yaml

def load_config():
    work_dir = os.getcwd()
    config_file_path = os.path.join(work_dir, 'config.yaml')
    if not os.path.exists(config_file_path):
        module_path = os.path.abspath(__file__)
        module_dir = os.path.dirname(module_path)
        shutil.copy2(os.path.join(module_dir,"configTemplate","config.yaml"), config_file_path)

    with open(config_file_path, 'r',encoding="utf8") as file:
        data = yaml.safe_load(file)
        return data

sys_config = load_config()

if __name__ == '__main__':
    load_config()