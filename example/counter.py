#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/9 15:59
# @Author : ChenHaHa
"""
    counter.py
    ~~~~~~~~~~~~~~~~~~~~~~~
    一个 counter 的例子
"""
# *********************************** import *****************************************
# 导入基本模块
from base import Clk, Signal, Block

# 导入显示模块，该模块可以使用modelsim来显示波形
from output import display_block_modelsim
# ************************************************************************************

# *********************************** 创建模块 *****************************************
# 一个系统只能由一个block，block负责管理所有模块以及信号
block = Block()
# 设置时间精度和时间单位
block.set_time_scale('1ns', '100ps')

# 创建时钟信号，频率单位为Mhz
clk = Clk(frequency=100)  # 100MHz, 10ns
# 创建信号，默认位宽为 1， 初始值是‘x’， record为True时表示追踪该信号的值
cnt = Signal(width=4, value=0, record=True)
a = Signal(width=4, value=0, record=True)
# 初始化时钟信号，否则信号为 “x“
clk.initial()

# *********************************** 定义自己的信号以及逻辑 *****************************************
# 使用 @block.always(trigger) 来告诉模块，这个函数是一个时序逻辑，并且由 trigger 来触发
# 触发信号可以时多个，使用逗号分隔
@block.always(clk.posedge)
def test():
    cnt <= cnt + 1
# ************************************************************************************************


# 开始运行系统，运行时间为 1000ns， 时间单位可以为 ns, us, ms, s
block.run('1000ns')

# 生成波形并显示 首先需要确保已经正确安装modelsim并加入环境变量中
# pycharm 中无法打开modelsim，可以使用命令行执行， python -m example.systolic_array
display_block_modelsim(block, 'counter')

