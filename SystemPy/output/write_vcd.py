#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/12 15:17
# @Author : ChenHaHa

from vcd import VCDWriter
from SystemPy.base import Signal
from SystemPy.base import Block
import os
from SystemPy.output.utils import get_record_signal_inst


def write_vcd(signals: list, block: Block, filename="vcd_output"):
    """
    该函数用于将signals中所有的信号输出到vcd文件中
    :param signals: 列表，包含了所有需要显示的信号
    :param block: Block类的实例
    :param filename: 保存的文件名
    :return:
    """
    signals_values = []
    signals_vars = []
    precision = block.precision
    # print(precision, 'ps')
    unit_convert = {0: 'ps', 1: 'ns', 2: 'us', 3: 'ms', 4: 's'}
    unit = unit_convert[(len(str(precision)) - 1) // 3]
    precision = precision // (10 ** (3 * (len(str(precision)) - 1) // 3))
    # print(precision, unit)

    # writer = VCDWriter(open(f'{filename}.vcd', 'w'), timescale=f'{block.precision} ps', date='today')
    # writer = VCDWriter(open(f'{filename}.vcd', 'w'), timescale=str(block.precision) + ' ps', date='today')
    writer = VCDWriter(open(f'{filename}.vcd', 'w'), timescale=f'{precision} {unit}', date='today')
    for index, signal in enumerate(signals):
        name = signal.name
        if not signal.record:
            print(f"Warning: {name} is not record")
            continue
        if name not in block.record_dict.keys():
            print(f"Warning: {name} is not record")
            continue
        data = block.record_dict[name]

        var = writer.register_var('top', name, 'wire', size=signal.width)
        signals_vars.append(var)
        signals_values.append(data)

    for timestamp in range(len(signals_values[0])):
        for index, signal in enumerate(signals):
            writer.change(signals_vars[index], timestamp, signals_values[index][timestamp])

    writer.close()


def vcd_to_wlf(vcd_file: str, wlf_file: str):
    """
    该函数用于将vcd文件转换为wlf文件
    :param vcd_file: 待转换的vcd文件名，需要后缀
    :param wlf_file: 转换后的wlf文件名，需要后缀
    :return:
    """
    import subprocess

    try:
        # ModelSim命令脚本
        do_script = """
        vcd2wlf {vcd_file} {wlf_file}
        quit
        """.format(vcd_file=vcd_file, wlf_file=wlf_file)

        # 将命令脚本写入临时文件
        with open("temp.do", "w") as f:
            f.write(do_script)

        # 使用subprocess运行ModelSim命令行工具
        subprocess.run(["vsim", "-c", "-do", "temp.do"])

        # 删除临时文件
        os.remove("temp.do")
    except Exception as e:
        print(e)
        print("Error: vcd to wlf failed. You should insure that ModelSim is installed and added to the environment "
              "variable PATH.")


def write_wlf(signals: list, block: Block, filename: str = "wlf_output"):
    """
    该函数用于将signals中所有的信号输出到wlf文件中
    使用该函数前，首先确保ModelSim已经安装并且已经添加到环境变量PATH中
    :param signals: 列表，包含了所有需要显示的信号
    :param block: Block类的实例
    :param filename:保存的文件名
    :return:
    """
    write_vcd(signals, block, filename)
    vcd_to_wlf(filename + '.vcd', filename + '.wlf')


def display_signals_modelsim(signals: list, block, filename="wlf_output"):
    """
    该函数用于在ModelSim中显示signals中所有的信号
    注意：使用该函数前，首先确保ModelSim已经安装并且已经添加到环境变量PATH中
    :param signals: 列表，包含了所有需要显示的信号
    :param block: Block类的实例
    :param filename: 保存的文件名
    :return:
    """
    write_vcd(signals, block, filename)

    # add wave -position insertpoint systolic_array:/top/clk
    # dataset open {}
    do_script_content = """
        vcd2wlf {vcd_file} {wlf_file}
        OpenFile {wlf_file}
        add wave *
        """.format(vcd_file=filename + '.vcd', wlf_file=filename + '.wlf')

    with open("temp.do", "w") as f:
        f.write(do_script_content)

    # subprocess.run(["vsim", "-do", "temp.do"])
    os.system("vsim -do temp.do")
    os.remove("temp.do")


def write_block_wlf(block: Block, filename: str = "wlf_output"):
    """
    该函数用于将block中所有record为True的信号输出到wlf文件中
    注意：使用该函数前，首先确保ModelSim已经安装并且已经添加到环境变量PATH中
    :param block: Block类的实例
    :param filename: 保存的文件名
    :return:
    """
    signals = get_record_signal_inst(block)
    write_wlf(signals, block, filename)


def display_block_modelsim(block: Block, filename: str = "wlf_output"):
    """
    该函数用于在ModelSim中显示block中所有record为True的信号
    注意：使用该函数前，首先确保ModelSim已经安装并且已经添加到环境变量PATH中
    :param block: Block类的实例
    :param filename: 波形输出的文件名
    :return:
    """
    signals = get_record_signal_inst(block)
    display_signals_modelsim(signals, block, filename)
