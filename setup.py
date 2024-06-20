#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/20 20:43
# @Author  : Pointer
# @File    : setup.py
# @Software: PyCharm

from setuptools import setup, find_packages

# 定义包的元数据
setup(
    name='asyncTask',  # 包的名称，在 PyPI 上必须是唯一的
    version='0.1.0',  # 包的版本号，遵循 PEP 440
    packages=find_packages(),  # 自动查找包和子包
    # 手动指定包含哪些包（如果不需要自动查找）
    # packages=['your_package_name', 'your_package_name.subpackage'],

    # 包的元数据
    author='pointer',  # 作者名字
    author_email='pointerstar007@gmail.com',  # 作者邮箱
    description='Lightweight asynchronous distributed task library',  # 包的简短描述
    long_description=open('README.md', encoding='utf-8').read(),  # 包的详细描述（通常来自 README 文件）
    long_description_content_type='text/markdown',  # 指定长描述的内容类型
    url='https://github.com/pointerStar007/asyncTask',  # 项目的URL（如GitHub链接）
    license='MIT',  # 包的许可证类型

    # 包的依赖项
    install_requires=[
        'schedule==1.2.2',
        'colorlog==6.8.2',
        'msgpack==1.0.8',
        'pyyaml==6.0.1',
        'py-redis==1.1.1'
    ],

    # 额外的元数据
    classifiers=[
        'Development Status :: 4 - Beta',  # 开发状态
        'Intended Audience :: Developers',  # 目标受众
        'License :: OSI Approved :: MIT License',  # 许可证
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10+',
        'Topic :: Software Development :: Libraries :: Python Modules',  # 主题
    ],

    # 其他的 setuptools 配置
    # 例如 entry_points、python_requires 等
    # entry_points={
    #     'console_scripts': [
    #         'your-command=your_package_name.your_module:main_func',
    #     ],
    # },
)
