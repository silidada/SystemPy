#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/12 16:43
# @Author : ChenHaHa
from SystemPy.base import Signal, Clk


def get_record_signal_inst(block):
    signals = block.record_dict.keys()
    signals = [Clk.get_instance_by_name(signal) for signal in signals]
    return signals
