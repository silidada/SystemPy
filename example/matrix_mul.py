#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/13 18:15
# @Author : ChenHaHa
from typing import List

"""
    本例子演示了如何使用 HDLpy 中的 systolic_array 模块
"""

# *********************************** import *****************************************
# 导入基础模块
from HDLpy.base import Module, Signal, Clk, sList, Block, sList_from_list
# 导入显示模块，该模块可以使用modelsim来显示波形
from HDLpy.output import display_block_modelsim
# 导入脉动阵列模块
from HDLpy.libs.systolic_array import systolic_array
# ************************************************************************************


# *********************************** 创建模块 *****************************************
# 一个系统只能由一个block，block负责管理所有模块以及信号
block = Block()
# 设置时间精度和时间单位
block.set_time_scale('1ns', '1ns')
# 创建时钟信号，频率单位为Mhz
clk = Clk(frequency=100)  # 100MHz, 10ns
# 初始化时钟信号，否则信号为 “x“
clk.initial()
# ************************************************************************************


# *********************************** 定义自己的信号以及逻辑 *****************************************
ARRAY_SIZE = 5
# 例化脉动阵列，需要传递 block 以及触发列表才可以正常工作
sa = systolic_array(array_size=ARRAY_SIZE, block_inst=block, trigger=[clk.posedge], record=False)

result = Signal(width=10, value=0, name="result", record=True)

matrix_a = [[1, 2, 3, 4, 5],[2, 3, 4, 5, 6],[3, 4, 5, 6, 7],[4, 5, 6, 7, 8],[5, 6, 7, 8, 9]]
matrix_b = [[1, 2, 3, 4, 5],[2, 3, 4, 5, 6],[3, 4, 5, 6, 7],[4, 5, 6, 7, 8],[5, 6, 7, 8, 9]]

# 我们使用sList来表示一个列表，这样可以在仿真时，模拟真实情况并避免了越界的问题
# return_value 表示当索引越界时，返回的值，这里我们设置为0，表示当索引越界时，返回0，默认值为 x
matrix_a = sList_from_list(matrix_a, return_value=0)
matrix_b = sList_from_list(matrix_b, return_value=0)

# 使用迭代器例化 Signal 时，必须使用 name 参数，且每一个 name 都必须是唯一的
# 注意：这里 name 千万不能写成数组的形式，如：reg[1][1]，否则波形显示会出错，目前尚不清楚原因，反过来写即可，如：[1][1]reg
regs_a = [[Signal(width=8, value=0, name=f"[{i}][{j}]regs_a", record=True if j == i else False) for j in range(i+1)] for i in range(ARRAY_SIZE)]
regs_b = [[Signal(width=8, value=0, name=f"[{i}][{j}]regs_b", record=True if j == i else False) for j in range(i+1)] for i in range(ARRAY_SIZE)]


# 构建我们的输入，我们需要模拟数据打拍
@block.always(clk.posedge)
def build_window():
    for reg_a in regs_a:
        for i in range(1, len(reg_a)):
            reg_a[i] <= reg_a[i - 1]
    for reg_b in regs_b:
        for i in range(1, len(reg_b)):
            reg_b[i] <= reg_b[i - 1]


# 将数据输入到 systolic_array 中
@block.always(clk.posedge)
def systolic_array_run():
    for k in range(ARRAY_SIZE):
        sa.pe_array[0][k].reg_b <= regs_b[k][-1]
        sa.pe_array[k][0].reg_a <= regs_a[k][-1]

# 输入数据
pulse_num = 0
@block.always(clk.posedge)
def input_data():
    global pulse_num
    for i in range(0, ARRAY_SIZE):
        regs_a[i][0] <= matrix_a[i][pulse_num]
        regs_b[i][0] <= matrix_b[i][pulse_num]
    pulse_num += 1

# 求和
@block.always(clk.posedge)
def array_sum():
    t = 0
    for i in range(ARRAY_SIZE):
        t += sa.pe_array[i][i].reg_result.value
    result <= t


block.run("1000ns")

# 生成波形并显示 首先需要确保已经正确安装modelsim并加入环境变量中
# pycharm 中无法打开modelsim，可以使用命令行执行， python -m example.systolic_array
import os
working_dir = './working'
if not os.path.exists(working_dir):
    os.mkdir(working_dir)

# print(block.record_dict.keys())
display_block_modelsim(block, './working/matrix_mul')


