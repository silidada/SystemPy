#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/11 16:21
# @Author : ChenHaHa

"""
    systolic_array.py
    ~~~~~~~~~~~~~~~~~~~~~~~
    一个 systolic array 的例子
"""

# *********************************** import *****************************************
# 导入基本模块
from HDLpy.base import Block, Signal, Clk, Module

# 导入显示模块，该模块可以使用modelsim来显示波形
from HDLpy.output import display_block_modelsim
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

# *********************** 定义 PE 必须继承 Module 类 ************************
class PE(Module):
    def __init__(self, pe_up=None, pe_left=None, name='PE'):
        super().__init__()
        self.name = name
        # 目前在类中或者迭代器中例化 Signal ，必须使用给信号一个 name
        self.reg_result = Signal(width=8, value=0, name=self.name+"reg_result", record=True)
        self.reg_a = Signal(width=8, value=0, name=self.name+"reg_a", record=True)
        self.reg_b = Signal(width=8, value=0, name=self.name+"reg_b", record=True)
        self.pe_up = pe_up
        self.pe_left = pe_left

    def __call__(self, a=None, b=None):
        if a is None:
            a = self.pe_left.reg_a.value
        if b is None:
            b = self.pe_up.reg_b.value

        self.reg_result <= (a * b) + self.reg_result.value
        self.reg_a <= a
        self.reg_b <= b

    def reset(self):
        """
        同步复位
        :return:
        """
        self.reg_result.next_value = 0
# *************************************************************************

# ******************************* 创建脉动阵列 *******************************
pe_array = []
pe_t = [PE(name="PE[0][0]")]
for i in range(ARRAY_SIZE - 1):
    pe_t.append(PE(pe_left=pe_t[i], name="PE[0][" + str(i + 1) + "]"))
pe_array.append(pe_t)

for i in range(ARRAY_SIZE - 1):
    pe_t = list()
    for j in range(ARRAY_SIZE):
        if j == 0:
            pe_t.append(PE(pe_up=pe_array[i][j], name="PE[" + str(i + 1) + "][0]"))
        else:
            pe_t.append(PE(pe_up=pe_array[i][j], pe_left=pe_t[j-1], name="PE[" + str(i + 1) + "][" + str(j) + "]" ))
    pe_array.append(pe_t)

a_in = [[1 for _ in range(100)] for _ in range(ARRAY_SIZE)]
b_in = [[1 for _ in range(ARRAY_SIZE)] for _ in range(ARRAY_SIZE)]

for i in range(ARRAY_SIZE):
    for j in range(i):
        a_in[i].insert(0, 0)
        b_in[i].insert(0, 0)

for i in b_in:
    print(i)
# *************************************************************************

# *********************** 创建数据出入 **************************************
# 使用 @block.always(trigger) 来告诉模块，这个函数是一个时序逻辑，并且由 trigger 来触发
# 触发信号可以时多个，使用逗号分隔
pulse_num = 0
@block.always(clk.posedge)
def systolic_array():
    global pulse_num
    for k in range(ARRAY_SIZE):
        for v in range(ARRAY_SIZE):
            if k == 0 and v == 0:
                pe_array[k][v](a=a_in[k][pulse_num], b=b_in[k][pulse_num % 5])
            elif k == 0:
                pe_array[k][v](b=b_in[k][pulse_num % 5])
            elif v == 0:
                pe_array[k][v](a=a_in[k][pulse_num])
            else:
                pe_array[k][v]()
    pulse_num += 1
# *************************************************************************

# 开始运行系统，运行时间为 1000ns， 时间单位可以为 ns, us, ms, s
block.run('1000ns')

# 生成波形并显示 首先需要确保已经正确安装modelsim并加入环境变量中
# pycharm 中无法打开modelsim，可以使用命令行执行， python -m example.systolic_array
import os
working_dir = './working'
if not os.path.exists(working_dir):
    os.mkdir(working_dir)
display_block_modelsim(block, './working/systolic_array')
"""
如果你不想打开modelsim，只是希望生成vcd文件，可以使用下面的代码
`write_vcd(signals, block, filename)`
- signals 是一个列表，包含了所有需要显示的信号
- block 就是本例中的 block
- filename 是文件名，不需要加后缀，会自动添加.vcd后缀

生成的文件会在当前目录下
例子： `write_vcd([clk, pe_array[0][0].reg_result], block, 'counter')`

可以使用 `output.utils.get_record_signal_inst(block)` 来获取所有 record 为 True 的信号
例子： `write_vcd(get_record_signal_inst(block), block, 'counter')`


如果你想将vcd文件转换为wlf文件，可以使用下面的代码
vcd_to_wlf(vcd_file, wlf_file)
- vcd_file 是 vcd 文件名，不需要加后缀，会自动添加.vcd后缀
- wlf_file 是 wlf 文件名，不需要加后缀，会自动添加.wlf后缀

如果想直接生成wlf文件，可以使用下面的代码
write_wlf(signals, block, filename)
- signals 是一个列表，包含了所有需要显示的信号
- block 就是本例中的 block
- filename 是文件名，不需要加后缀，会自动添加.wlf后缀

或者
write_block_wlf(block, filename)
- block 就是本例中的 block
- filename 是文件名，不需要加后缀，会自动添加.wlf后缀


"""



