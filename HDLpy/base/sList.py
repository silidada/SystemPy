#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/13 15:34
# @Author : ChenHaHa

from typing import Union, Iterable


def sList_from_list(l: list, return_value: Union[str, int] = 'x'):
    for i in range(len(l)):
        if type(l[i]) == list:
            l[i] = sList_from_list(l[i], return_value)
    return sList(l, return_value)


class sList(list):
    def __init__(self, iterable: Iterable = [], return_value: Union[str, int] = 'x'):
        super().__init__(iterable)
        self.return_value = return_value

    def __getitem__(self, item):
        if item >= len(self):
            return self.return_value
        return super().__getitem__(item)


if __name__ == '__main__':
    a = ['a', 'b', ['c', 'd']]
    print(a)
    b = sList_from_list(a)
    print(b[0], b[1], b[2], b[3])
