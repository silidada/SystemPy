#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/12 13:56
# @Author : ChenHaHa

from SystemPy.base import Signal, Clk
from SystemPy.output.utils import get_record_signal_inst


def write_data(clk):
    clk_wave = ''
    for i in range(0, len(clk), 1):
        prev_clk = clk[i - 1] if i > 0 else None
        if clk[i] == prev_clk:
            clk_wave += '.'
        else:
            clk_wave += str(clk[i])
    return clk_wave


def write_data_bus(data):
    data_wave = ''
    data_values = []
    for i in range(0, len(data), 1):
        prev_data = data[i - 1] if i > 0 else None
        if data[i] == prev_data:
            data_wave += '.'
        else:
            data_wave += '='
            data_values.append(data[i])

    return data_wave, data_values


def generate_signal_wavedrom(signal, block):
    name = signal.name
    if not signal.record:
        print(f"Warning: {name} is not record")
        return None, None
    if name not in block.record_dict.keys():
        print(f"Warning: {name} is not record")
        return None, None
    data = block.record_dict[name]
    if signal.width == 1:
        data_wave = write_data(data)
        data_values = []
    else:
        data_wave, data_values = write_data_bus(data)
    return data_wave, data_values


def generate_signals_wavedrom(signals, block):
    data_wave = ''
    data_values = []
    for signal in signals:
        data_wave, data_values = generate_signal_wavedrom(signal, block)
        if data_wave is None:
            continue

    return data_wave, data_values


def generate_wavedrom(signals, block):
    wavedrom_code = """
        { "signal": [ \n
    """
    for index, signal in enumerate(signals):
        code = f'{{ "name": "{signal.name}", '
        data_wave, data_values = generate_signal_wavedrom(signal, block)
        if data_wave is None:
            continue
        code += f'"wave": "{data_wave}"'
        if data_values:
            if len(data_values):
                code += f', data: {data_values}'

        if index != len(signals) - 1:
            code += '}, \n'
        else:
            code += '} \n'
        wavedrom_code += code
    wavedrom_code += ']}'

    # print(wavedrom_code)
    return wavedrom_code


def draw_wavedrom(signals, block, file_name='waveform1'):
    """
    该函数用于将signals中所有的信号保存到svg矢量图中
    :param signals:  列表，包含了所有需要显示的信号
    :param block:  Block类的实例
    :param file_name:  保存的文件名
    :return:
    """
    wavedrom_code = generate_wavedrom(signals, block)
    # print(wavedrom_code)
    from wavedrom import render
    svg = render(wavedrom_code)
    svg.saveas(file_name + ".svg")


def export_wavedrom(signals, block, file_name='waveform1'):
    """
    该函数用于将signals中所有的信号输出到wavedrom格式的文件中
    :param signals:  列表，包含了所有需要显示的信号
    :param block:  Block类的实例
    :param file_name:  保存的文件名
    :return:
    """
    wavedrom_code = generate_wavedrom(signals, block)
    # print(wavedrom_code)
    with open(file_name + ".json", 'w') as f:
        f.write(wavedrom_code)


def export_block_wavedrom(block, file_name='block_waveform'):
    """
    该函数用于将block中所有的信号输出到wavedrom格式的文件中
    :param block:  Block类的实例
    :param file_name:  保存的文件名
    :return:
    """
    signals = get_record_signal_inst(block)
    export_wavedrom(signals, block, file_name)


def draw_block_wavedrom(block, file_name='block_waveform'):
    """
    该函数用于将block中所有的信号保存到svg矢量图中
    :param block:  Block类的实例
    :param file_name:  保存的文件名
    :return:
    """
    signals = get_record_signal_inst(block)
    draw_wavedrom(signals, block, file_name)
