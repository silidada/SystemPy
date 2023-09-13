#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/9 13:52
# @Author : ChenHaHa
from abc import ABC
import inspect
import re
from typing import Union

_MAX_WIDTH = 9999


class Module:
    _modules = dict()

    def __init__(self):
        if self.__class__ not in self._modules.keys():
            self._modules[self.__class__] = []
        self.name = str(self.__class__) + str(len(self._modules[self.__class__]))
        self._modules[self.__class__].append(self.name)

    def __setattr__(self, name, value):
        # print(name, value)
        super().__setattr__(name, value)


def max_width_signal(width, value):
    if value > width ** 2 - 1:
        return value & (2 ** width - 1)
    return value


class Signal:
    _instance = []
    _instance_dict = dict()
    _clk_instance = []
    _instance_code_line = dict()
    _clk_instance_dict = dict()

    def __init__(self, width=1, value: Union[str, int] = 'x', record=False, name=None, ignore=False):
        # super().__init__()
        self.width = width
        self.value = value
        self.max_value = 2 ** width - 1
        self.next_value = value
        if self.__class__ == Signal:
            Signal._instance.append(self)
        self.record = record

        if ignore: return

        # 获取调用此构造函数的代码行
        frame = inspect.currentframe().f_back
        code = frame.f_code
        line_no = frame.f_lineno
        with open(code.co_filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 使用正则表达式从代码行中解析变量名
        match = re.search(r'(\w+)\s*=\s*Signal\(', lines[line_no - 1])
        if name:
            self.name = name
            Signal._instance_dict[self.name] = self
            Signal._instance_code_line[self.name] = (line_no, code.co_filename, lines[line_no - 1])
        else:
            if match:
                self.name = match.group(1)
            else:
                self.name = None

            if self.__class__ == Signal:
                if self.name in Signal._instance_dict.keys():
                    raise Exception(
                        f"Signal {self.name} is already defined, in line {line_no} of {code.co_filename} \n "
                        f"{lines[line_no - 1]} \n "
                        f"and line {Signal._instance_code_line[self.name][0]} of"
                        f" {Signal._instance_code_line[self.name][1]} \n "
                        f"{Signal._instance_code_line[self.name][2]}")
                else:
                    Signal._instance_dict[self.name] = self
                    Signal._instance_code_line[self.name] = (line_no, code.co_filename, lines[line_no - 1])

    def update(self):
        self.value = self.next_value

    def set(self, value):
        self.value = value
        self.next_value = value

    def __str__(self):
        return str(self.value)

    def __add__(self, other):
        other1 = self._get_other_value(other)
        if self.value == 'x' or other1 == 'x':
            return 'x'
        if self.value == 'z' or other1 == 'z':
            return 'z'
        assert isinstance(other1, int)
        assert isinstance(self.value, int)
        other1: int
        self.value: int
        if isinstance(other, Signal):
            return Signal(_MAX_WIDTH, self.value + other1, ignore=True)
        return self.value + other1

    def __le__(self, other):
        # 模拟verilog中的 <=
        if isinstance(other, Signal):
            other = other.value

        if self.value == 'x' or other == 'x':
            self.next_value = 'x'
            return self
        if self.value == 'z' or other == 'z':
            self.next_value = 'z'
            return self

        if other > self.max_value:
            other = other & (2 ** (self.width - 1))
        self.next_value = other
        return self

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        raise NotImplementedError

    def __lt__(self, other):
        return self.value < other.value

    def __and__(self, other):
        if self.value == 'x' or other.value == 'x':
            return 'x'
        if self.value == 'z' or other.value == 'z':
            return 'z'
        assert isinstance(other.value, int)
        assert isinstance(self.value, int)
        return self.value & other.value

    def __or__(self, other):
        if self.value == 'x' or other.value == 'x':
            return 'x'
        if self.value == 'z' or other.value == 'z':
            return 'z'
        assert isinstance(other.value, int)
        assert isinstance(self.value, int)
        return self.value | other.value

    def __xor__(self, other):
        if self.value == 'x' or other.value == 'x':
            return 'x'
        if self.value == 'z' or other.value == 'z':
            return 'z'
        assert isinstance(other.value, int)
        assert isinstance(self.value, int)
        return self.value ^ other.value

    def __invert__(self):
        if self.value == 'x':
            return 'x'
        if self.value == 'z':
            return 'z'
        assert isinstance(self.value, int)
        return ~self.value

    def __lshift__(self, other):
        if self.value == 'x' or other.value == 'x':
            return 'x'
        if self.value == 'z' or other.value == 'z':
            return 'z'
        assert isinstance(other.value, int)
        assert isinstance(self.value, int)
        return self.value << other.value

    def __rshift__(self, other):
        if self.value == 'x' or other.value == 'x':
            return 'x'
        if self.value == 'z' or other.value == 'z':
            return 'z'
        assert isinstance(other.value, int)
        assert isinstance(self.value, int)
        return self.value >> other.value

    def __mul__(self, other):
        other1 = self._get_other_value(other)
        if self.value == 'x' or other1 == 'x':
            return 'x'
        if self.value == 'z' or other1 == 'z':
            return 'z'

        other1: int
        if isinstance(other, Signal):
            return Signal(_MAX_WIDTH, self.value * other1, ignore=True)
        return self.value * other1

    def __hash__(self):
        return id(self)

    def __call__(self, target):
        if isinstance(target, int):
            self.value = max_width_signal(self.width, target)
            return self
        elif isinstance(target, Signal):
            self.value = max_width_signal(self.width, target.value)
            return self
        else:
            raise TypeError

    @staticmethod
    def _get_other_value(other):
        if isinstance(other, Signal):
            return other.value
        return other

    @classmethod
    def get_all_instances(cls):
        return cls._instance

    @classmethod
    def update_all(cls):
        for instance in cls._instance:
            instance.update()

    @classmethod
    def get_clk_instances(cls):
        return cls._clk_instance

    @classmethod
    def get_instance_name(cls):
        return cls._instance_dict

    @classmethod
    def get_instance_by_name(cls, name):
        if name not in cls._instance_dict.keys():
            if name not in cls._clk_instance_dict.keys():
                raise Exception(f"Signal {name} is not defined")
            else:
                return cls._clk_instance_dict[name]
        return cls._instance_dict[name]


class Clk(Signal):
    def __init__(self, frequency, value='x', record=True):
        """
        only support MHz
        :param frequency:
        :param value:
        """
        super().__init__(1, value, record)
        # self.status = ['low', 'posedge', 'high', 'negedge']
        self.status = [0, 1]
        self.state = 'x'
        self.frequency = frequency
        self.period = 1 / frequency * (10 ** 6)  # unit: ps
        self.half_period = self.period // 2
        Signal._clk_instance.append(self)
        self.time = 0
        self.precision = 0
        self.prev_state = 'x'
        self.width = 1

        # 获取调用此构造函数的代码行
        frame = inspect.currentframe().f_back
        code = frame.f_code
        line_no = frame.f_lineno
        with open(code.co_filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # 使用正则表达式从代码行中解析变量名
        match = re.search(r'(\w+)\s*=\s*Clk\(', lines[line_no - 1])
        if match:
            self.name = match.group(1)
        else:
            self.name = None

        if self.name in Signal._clk_instance_dict.keys():
            raise Exception(
                f"Signal {self.name} is already defined, in line {line_no} of {code.co_filename} \n "
                f"{lines[line_no - 1]} \n "
                f"and line {Signal._clk_instance_dict[self.name][0]} of"
                f" {Signal._clk_instance_dict[self.name][1]} \n "
                f"{Signal._clk_instance_dict[self.name][2]}")
        else:
            Signal._clk_instance_dict[self.name] = self

    def initial(self):
        self.state = 0
        # self.state = 'low'

    def set_time_scale(self, precision):
        self.precision = precision

    def update(self):
        self.time += self.precision
        if self.time >= self.half_period:
            self.time -= self.half_period
            self.step()
        else:

            self.prev_state = self.state

    def step(self):

        if self.state == 1:
            self.prev_state = 1
            self.state = 0
        elif self.state == 0:
            self.prev_state = 0
            self.state = 1
        else:
            self.state = 'x'

    def posedge(self):
        if self.prev_state == 0 and self.state == 1:
            return True
        else:
            return False

    def negedge(self):
        if self.prev_state == 1 and self.state == 0:
            return True

    def __call__(self, *args, **kwargs):
        return self.step()

    def __str__(self):
        return 'high' if self.state == 1 else 'low'


if __name__ == '__main__':
    print(max_width_signal(2, 6))
