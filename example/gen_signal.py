#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/13 21:31
# @Author : ChenHaHa

from HDLpy.base import Block, Signal, Clk, Module, sList, delay

# 导入显示模块，该模块可以使用modelsim来显示波形
from HDLpy.output import display_block_modelsim

block = Block()
block.set_time_scale('1ns', '1ns')
clk = Clk(frequency=100)  # 100MHz, 10ns
clk.initial()

rst = Signal(width=1, value='x', name="rst", record=True)
a = Signal(width=8, value=0, name="a", record=True)
b = Signal(width=8, value=0, name="b", record=True)


@block.initial()
def test():
    global rst, a, b
    delay(10)
    rst = 0
    delay(10)
    a = 10
    rst = 1
    delay(50)
    b = 20
    rst = 0

    delay(10)
    a = 0
    b = 0


block.run("1000ns")

import os

working_dir = './working'
if not os.path.exists(working_dir):
    os.mkdir(working_dir)
display_block_modelsim(block, f"{working_dir}/gen_signal")
