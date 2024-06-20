#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/6/19 17:20
# @Author  : Pointer
# @File    : singletion.py
# @Software: PyCharm


class Singletion:
    _instance = None
    def __new__(cls, *args, **kwargs):

        if not cls._instance:
            cls._instance = super().__new__(cls,*args,**kwargs)
        return cls._instance


if __name__ == '__main__':
    class A(Singletion):
        pass

    a1 = A()
    a2 = A()

    print(id(a1))
    print(id(a2))
