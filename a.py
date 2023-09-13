#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/12 20:42
# @Author : ChenHaHa

import numpy as np

def a (*args):
    def decorator(func):
        print(args, func)
        return func

    return decorator

# @a()
# def b():
#     pass

class c:
    def __init__(self):
        a(self.__call__)

    def __call__(self, *args, **kwargs):
        pass

def b(hh, *args):
    print(hh, args)


if __name__ == '__main__':
    b(2, 3, 4, 5, 6, 7, 8, 9, 0, hh=1)
