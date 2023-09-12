# HDLpy 
## 描述
SystemPy用来模拟HDL中的行为，从而快速地验证系统可行性

## 安装
```bash
python setup.py install
# or 
pip install HDLpy
```

## 使用
### base 模块
#### 1. [Signal](HDLpy/base/Signal.py)
`Signal(width=1, value='x', record=False)`
- width: 信号位宽，默认为1
- value: 信号初始值，默认为'x'
- record: 是否记录信号值，默认为False

#### 2. [Clk](HDLpy/base/Signal.py)
`Clk(frequency=1)`
- frequency: 时钟频率，默认为1

#### 3. [Block](HDLpy/base/block.py)
`Block()`

一个系统只能由一个block，block负责管理所有模块以及信号
##### 3.1 set_time_scale
`set_time_scale(time_unit, time_precision)`
- time_unit: 时间单位，可以为 ns, us, ms, s
- time_precision: 时间精度，可以为 ns, us, ms, s
- 例如：`set_time_scale('1ns', '100ps')`

##### 3.2 always
`always(trigger1, trigger2, ...)`
- trigger: 触发信号，可以为多个，使用逗号分隔

例如：`@always(clk.posedge, rst.posedge)`

该函数用来告诉模块，这个函数是一个时序逻辑，并且由 trigger 来触发

##### 3.3 run
`run(time)`
- time: 运行时间，可以为 ns, us, ms, s

例如：`run('1000ns')`

该函数用来运行系统，运行时间为 time

### output 模块
#### 1. [write_vcd](HDLpy/output/write_vcd.py)
##### 1.1. display_block_modelsim
`display_block_modelsim(block, name)`
- block: block对象
- name: 波形文件名

例如：`display_block_modelsim(block, 'counter')`

该函数用来生成波形并显示，首先需要确保已经正确安装modelsim并加入环境变量中

pycharm 中无法打开modelsim，可以使用命令行执行， python -m example.systolic_array

##### 1.2. write_block_wlf

##### 1.3. display_signals_modelsim

##### 1.4. write_wlf

##### 1.5 vcd_to_wlf

##### 1.6. write_vcd

#### 2. [write_wavedrom](HDLpy/output/write_wavedrom.py)
##### 2.1. draw_block_wavedrom
##### 2.2. export_block_wavedrom
##### 2.3. export_wavedrom
##### 2.4. draw_wavedrom



## 例子
### 1. 计数器
```python
from HDLpy.base import Clk, Signal, Block

# 导入显示模块，该模块可以使用modelsim来显示波形
from HDLpy.output import display_block_modelsim
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
```