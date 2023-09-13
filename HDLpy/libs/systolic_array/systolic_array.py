#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/13 14:56
# @Author : ChenHaHa

from HDLpy.base import Block, Signal, Clk, Module, sList
from typing import List
from HDLpy.output import display_block_modelsim
from HDLpy.std import print_warning, print_error, print_info


class PE(Module):
    def __init__(self, pe_up=None, pe_left=None, name='PE', block_inst: Block = None, trigger=None, record=True):
        super().__init__()
        self.name = name
        # 目前在类中或者迭代器中例化 Signal ，必须使用给信号一个 name
        self.reg_result = Signal(width=8, value=0, name=self.name + "reg_result", record=record)
        self.reg_a = Signal(width=8, value=0, name=self.name + "reg_a", record=record)
        self.reg_b = Signal(width=8, value=0, name=self.name + "reg_b", record=record)
        self.pe_up = pe_up
        self.pe_left = pe_left

        if block_inst is not None:
            block_inst.add_always_module(self.__call__, *trigger)

    def __call__(self):
        self.reg_result <= (self.reg_a * self.reg_b) + self.reg_result

    def reset(self):
        """
        同步复位
        :return:
        """
        self.reg_result.next_value = 0


class systolic_array(Module):
    def __init__(self, array_size, block_inst: Block = None, trigger: List = None, record=False):
        super().__init__()
        self.array_size = array_size
        self.pulse_num = 0
        self.pe_array = [
            [PE(name=f"PE[{i}][{j}]", block_inst=block_inst, trigger=trigger, record=record) for j in range(self.array_size)] for i in
            range(self.array_size)]
        if block_inst is None:
            print_warning("You instantiate systolic_array without block_inst, the systolic_array will not work !")
        if trigger is None or len(trigger) == 0:
            print_warning("You instantiate systolic_array without trigger, the systolic_array will not work !")
        if block_inst is not None:
            block_inst.add_always_module(self.create_array, *trigger)

    def create_array(self):
        for i in range(self.array_size):
            for j in range(self.array_size):
                if i == 0 and j == 0:
                    continue
                elif i == 0:
                    self.pe_array[i][j].reg_a <= self.pe_array[i][j - 1].reg_a
                elif j == 0:
                    self.pe_array[i][j].reg_b <= self.pe_array[i - 1][j].reg_b
                else:
                    self.pe_array[i][j].reg_a <= self.pe_array[i][j - 1].reg_a
                    self.pe_array[i][j].reg_b <= self.pe_array[i - 1][j].reg_b

    def reset(self):
        for i in range(self.array_size):
            for j in range(self.array_size):
                self.pe_array[i][j].reset()


if __name__ == '__main__':
    # 一个系统只能由一个block，block负责管理所有模块以及信号
    block = Block()
    # 设置时间精度和时间单位
    block.set_time_scale('1ns', '1ns')
    # 创建时钟信号，频率单位为Mhz
    clk = Clk(frequency=100)  # 100MHz, 10ns
    # 初始化时钟信号，否则信号为 “x“
    clk.initial()

    ARRAY_SIZE = 5

    array = systolic_array(ARRAY_SIZE, block_inst=block, trigger=[clk.posedge])
    a_in = [sList([1 for _ in range(ARRAY_SIZE)], return_value=0) for _ in range(ARRAY_SIZE)]
    b_in = [sList([1 for _ in range(ARRAY_SIZE)], return_value=0) for _ in range(ARRAY_SIZE)]

    a_in = sList(iterable=a_in, return_value=0)
    b_in = sList(iterable=b_in, return_value=0)

    for i in range(ARRAY_SIZE):
        for j in range(i):
            a_in[i].insert(0, 0)
            b_in[i].insert(0, 0)
    pulse_num = 0


    @block.always(clk.posedge)
    def systolic_array_run():
        global pulse_num
        for k in range(ARRAY_SIZE):
            array.pe_array[0][k].reg_b <= b_in[k][pulse_num]
            array.pe_array[k][0].reg_a <= a_in[k][pulse_num]
        pulse_num += 1


    block.run('1000ns')

    import os

    working_dir = './working'
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
    display_block_modelsim(block, './working/systolic_array')
