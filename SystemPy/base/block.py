#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/9 13:43
# @Author : ChenHaHa
from SystemPy.base import Clk, Signal, draw_wave
import tqdm
from SystemPy.compile import *
from threading import Thread

# 暂无解决多个触发同时触发的问题


# class
#
#
# class Always:
#     def __init__(self):
#         pass
#
#     def


class Block(object):
    supported_block_type = ['always']
    supported_trigger_type = ['posedge', 'negedge']

    def __init__(self):
        self.block_dict = dict()
        self.trigger_set = set()
        self.trigger_dict = dict()
        # unit: ps
        self.precision = 1
        self.unit = 1
        self.time = 0
        self.unit_convert = {'ps': 1, 'ns': 1000, 'us': 1000000, 'ms': 1000000000, 's': 1000000000000}
        for block_type in self.supported_block_type:
            self.block_dict[block_type] = list()
        self.record_dict = dict()
        self._time_tree = dict()

    def set_time_scale(self, unit, precision):
        """
        设置时间精度
        :param precision: 格式 1ns or 1ps or ..
        :param unit: 格式 1ns or 1ps or ..
        :return: None
        """
        self.precision = int(precision[:-2]) * self.unit_convert[precision[-2:]]
        self.unit = int(unit[:-2]) * self.unit_convert[unit[-2:]]

    def always(self, *args):
        def decorator(func):
            for arg in args:
                self.trigger_set.add(arg)
                if arg not in self.trigger_dict.keys():
                    self.trigger_dict[arg] = list()
                self.trigger_dict[arg].append(func)
            self.block_dict['always'].append((func, args))

        return decorator

    def trigger(self):
        for activate_func in self.trigger_set:
            if activate_func():
                for func in self.trigger_dict[activate_func]:
                    func()
        Signal.update_all()

    def record(self):
        signals = Signal.get_all_instances()
        clks = Signal.get_clk_instances()
        for clk_ in clks:
            if clk_.record:
                self.record_dict[clk_.name].append(clk_.state)
        for signal in signals:
            if signal.record:
                # self.record_dict[signal].append(signal.value)
                self.record_dict[signal.name].append(signal.value)

    @staticmethod
    def executor(instructions):
        # print('instructions: ', instructions)
        all_signals = Signal.get_instance_name()
        for instruction in instructions:
            # print('instruction: ', instruction)
            # it should be list
            assert isinstance(instruction, list)

            target = all_signals[instruction[0]]

            # 运算
            target = all_signals[instruction[0]]
            if isinstance(target, str):
                target = all_signals[target]
            if not isinstance(target, Signal):
                raise Exception(f"Instruction {instruction} is not supported, the first element should be a Signal")

            operators = list()
            for i in range(1, len(instruction)):
                # print(operators)
                current_op = instruction[i]
                # print('instruction: ', instruction)
                # print('current_op: ', current_op)
                if isinstance(current_op, str):
                    operators.append(current_op)
                elif isinstance(current_op, int):
                    operators.append(current_op)
                elif isinstance(current_op, Signal):
                    operators.append(current_op.value)
                elif callable(current_op):
                    if not len(operators) == 2:
                        raise Exception(f"Instruction {instruction} is not supported, ")
                    operator1 = operators.pop(0)
                    operator2 = operators.pop(0)
                    if isinstance(operator1, Signal):
                        operator1 = operator1.value
                    elif isinstance(operator1, str):
                        operator1 = all_signals[operator1].value
                    elif isinstance(operator1, int):
                        pass
                    else:
                        raise Exception(f"Instruction {instruction} is not supported, ")
                    if isinstance(operator2, Signal):
                        operator2 = operator2.value
                    elif isinstance(operator2, str):
                        operator2 = all_signals[operator2].value
                    elif isinstance(operator2, int):
                        pass
                    else:
                        raise Exception(f"Instruction {instruction} is not supported, ")
                    operators.append(current_op(operator1, operator2))
                elif isinstance(current_op, list):
                    if current_op[1] == 'print':
                        # print("--- --- "*10)
                        print("print: ", end='\t')
                        for print_thing in current_op[3]:
                            if isinstance(print_thing, str):
                                if print_thing in all_signals.keys():
                                    print("Signal: ", print_thing, ": ", "current value: ", all_signals[print_thing].value, ", ", "next value:", all_signals[print_thing].next_value)
                                else:
                                    print(print_thing)
                            elif isinstance(print_thing, Signal):
                                print("Signal: ", print_thing.name, ": ", "current value:", print_thing.value, ", ", "next value:", print_thing.next_value)
                            else:
                                print(print_thing)
                        # print("--- --- " * 10)
                        continue
                    args = current_op[3]
                    for arg in args:
                        if isinstance(arg, int):
                            operators.append(arg)
                        elif isinstance(arg, str):
                            operators.append(all_signals[arg].value)
                        elif isinstance(arg, Signal):
                            operators.append(arg.value)
                        else:
                            raise Exception(f"Instruction {instruction} is not supported, ")
                    func = current_op[2]
                    # print(operators, current_op)
                    r = func(*operators)
                    operators = list()
                    operators.append(r)
            # 赋值
            if len(operators) == 1:
                if isinstance(operators[0], int):
                    target.set(operators[0])
                elif isinstance(operators[0], Signal):
                    target.set(operators[0].value)
                continue

    def run(self, time='100ns'):
        clk_list = Signal.get_clk_instances()
        # 给每一个时钟时间精度
        for clk_ in clk_list:
            clk_.set_time_scale(self.precision)

        signals = Signal.get_all_instances()
        for signal in signals:
            if signal.record:
                # self.record_dict[signal] = list()
                self.record_dict[signal.name] = list()
        clks = Signal.get_clk_instances()
        for clk_ in clks:
            if clk_.record:
                self.record_dict[clk_.name] = list()

        time = int(time[:-2]) * self.unit_convert[time[-2:]]
        times = time // self.precision
        with tqdm.tqdm(total=times) as pbar:
            pbar.set_description('Running')
            for i in range(times):
                # change time trigger time first
                if i in self._time_tree.keys():
                    # print('time: ', i)
                    self.executor(self._time_tree[i])
                for clk_ in clk_list:
                    clk_.update()
                self.trigger()
                self.record()
                pbar.update(1)
        # draw_wave(time, self.record_dict)

    def initial(self):
        """
        暂不支持多文件编写initial模块，目前支持在 initial 模块中调用同一文件下的函数
        暂不支持在在传递参数处进行计算， 如： a = func1(b + c)
        暂不支持在函数返回处进行计算， 如： a = func(b) + c， 但是可以写成 a = func(b); a = a + c
        :return:
        """
        def wrapper(func):
            # print(f"Function '{func.__name__}' is from module '{func.__module__}'")
            bytecode = get_func_bytecode(func, func.__module__)
            compiled_code = compile_init(bytecode, Signal.get_instance_name())
            times = 0
            for code in compiled_code:
                if isinstance(code, int):
                    code_t = code * self.unit // self.precision
                    if code_t in self._time_tree.keys():
                        raise Exception(f"Time {code} is already used")
                    else:
                        times = code_t
                else:
                    self._time_tree[times] = code
            print(self._time_tree)
        return wrapper

    def delay(self, time):
        """
        单位是在 set_time_scale 中设置的 unit
        :param time:
        :return:
        """
        delay_time = time * self.unit
        delay_times = delay_time // self.precision

        return delay_times

    def test(self):
        for block_type in self.supported_block_type:
            for func in self.block_dict[block_type]:
                func[0]()


# block = Block()
# block.set_time_scale('1ns', '100ps')
#
# a = Signal(width=4, value=0)
# b = Signal(width=4, value=1)
# c = Signal(width=4, value=2)
# d = Signal(width=4, value=3)
#
# clk = Clk(frequency=100)  # 100MHz, 10ns
# clk.initial()


# @block.always(clk.posedge)
# def test():
#     global a, b, c
#     print('test')
#     a <= b + c
#
#
# @block.always(clk.posedge)
# def test2():
#     global a, c, d
#     d <= a + c


# if __name__ == '__main__':
#     print(clk)
#     block.trigger()
#     print(a)
#     print(d)
#     block.run('14ns')
#     print(a)
#     print(d)
