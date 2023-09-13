#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/10 13:54
# @Author : ChenHaHa

import dis
import inspect
import ast
import re
import importlib
from HDLpy.compile.code import *


def get_function_bytecode(func):
    # 获取字节码对象
    bytecode_obj = dis.Bytecode(func)

    # 将字节码保存到列表中
    bytecode_list = list(bytecode_obj)
    return_list = list()

    # 打印字节码列表
    for instruction in bytecode_list:
        if instruction.opname == 'LOAD_GLOBAL':
            if instruction.argval in DELAY_CMD:
                return_list.append(instruction)
                continue
            func_name = instruction.argval
            if func_name in globals():
                called_func = globals()[func_name]
            elif func_name in SPECIAL_FUNCTION.keys():
                pass
            else:
                raise Exception(f"Instruction {instruction}, Function {func_name} is not defined")
            return_list.append(instruction)
            # return_list += get_function_bytecode(called_func)
        elif instruction.opname == 'CALL_FUNCTION':
            continue
        else:
            return_list.append(instruction)

    return return_list


def get_call_func(func, calls=None):
    if calls is None:
        calls = []

    # 获取函数的源代码
    source = inspect.getsource(func)

    # 使用AST解析源代码
    tree = ast.parse(source)

    # 查找所有函数调用
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # 获取被调用的函数的名称
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                # 获取函数调用的参数值
                args = [ast.dump(arg) for arg in node.args]
                # 保存函数调用及其参数到列表中
                calls.append((func_name, args))
                # 如果这个函数在当前模块中定义，递归地处理它
                if func_name in globals():
                    called_func = globals()[func_name]
                    get_call_func(called_func, calls)

    return calls


def get_func_bytecode(func, *args):
    for arg in args:  # import module
        module = importlib.import_module(arg)
        globals().update({k: v for k, v in module.__dict__.items() if not k.startswith("_")})

    bytes_list = get_function_bytecode(func)
    calls_list = get_call_func(func)

    result = list()

    i = 0
    for bytes_l in bytes_list:
        if bytes_l.opname == 'LOAD_GLOBAL':
            func_name = bytes_l.argval

            if func_name == calls_list[i][0]:
                # cmd = f"{bytes_l.opname} {bytes_l.argval}"
                cmd = [bytes_l.opname, bytes_l.argval]
                if func_name in DELAY_CMD:
                    param = calls_list[i][1][0]
                    match = re.search(r"value=(.*?),", param)
                    if match:
                        cmd.append(match.group(1))
                    else:
                        raise Exception(f"Function {func_name} input error")
                else:
                    if func_name in globals():
                        called_func = globals()[func_name]
                        cmd.append(called_func)
                    elif func_name in SPECIAL_FUNCTION.keys():
                        cmd.append(SPECIAL_FUNCTION[func_name])
                    else:
                        raise Exception(f"Function {func_name} is not defined")
                    for j in range(len(calls_list[i][1])):
                        param = calls_list[i][1][j]
                        match = re.search(r"id='(.*?)'", param)
                        if match:
                            value = match.group(1)
                            cmd.append(value)
                        else:
                            raise Exception(f"Function {func_name} input error")
                i += 1
            else:
                raise Exception(f"Function {func_name} is not defined")
        else:
            cmd = [bytes_l.opname, bytes_l.argval]
        result.append(cmd)
    return result


#  x return   [start_time(0), [[0/1 (Double-operand/ Multi-operand ),target, src1, (src2), operator1, (src3, operator2 ...)][instruction 2]], delay_times(the number of run percision, but not time unit), [], delay_times, [], ...]
# return   [start_time(0), [[target, src1, (src2), operator1, (src3, operator2 ...)][instruction 2]], delay_times(the number of run percision, but not time unit), [], delay_times, [], ...]
def compile_init(bytecodes, signals_inst_dict):
    print("*"*100)
    print(" "*35, "compiling initial block")
    # print(bytecodes)
    times = 0
    # operands = list()
    compiled_instructs = list()
    cmd = list()
    cmd.append('')
    current_cmd = list()
    ignore_num = 0

    compiled_instructs.append(0)

    for bytecode in bytecodes:
        # print(bytecode)
        if ignore_num > 0:
            ignore_num -= 1
            continue
        # print(bytecode, cmd)
        instruction = bytecode[0]
        if instruction in LOAD_CMD:
            if instruction == 'LOAD_CONST':
                # operands.append(bytecode[1])
                cmd.append(bytecode[1])
            elif instruction == 'LOAD_FAST':
                # print("LOAD_FAST", bytecode)
                var_name = bytecode[1]
                if var_name in signals_inst_dict.keys():
                    # print("LOAD_FAST", bytecode, var_name)
                    # operands.append(var_name)
                    cmd.append(var_name)
                    # print(operands)
                else:
                    raise Exception(f"Variable {var_name} is not defined")
            elif instruction == 'LOAD_GLOBAL':
                # if not len(operands) == 0:
                #     raise Exception(f"Instruction {bytecode} error")
                if bytecode[1] in DELAY_CMD:
                    compiled_instructs.append(current_cmd)
                    current_cmd = list()
                    compiled_instructs.append(int(bytecode[2]))
                    ignore_num = 2
                elif bytecode[1] in SPECIAL_FUNCTION:
                    cmd.append(['function', bytecode[1], bytecode[2], [bytecode[3]]])
                    ignore_num = 2
                else:
                    func_param = bytecode[3:]
                    cmd.append(['function', bytecode[1], bytecode[2], func_param])
                    ignore_num = len(func_param)
            else:
                raise Exception(f"Instruction {instruction} is not supported")
        elif instruction in COMPUTE_CMD:
            if instruction in DOUBLE_OP_CMD:
                # if len(operands) == 2:
                #     raise Exception(f"Instruction {bytecode} error")
                # else:
                    # cmd.append('DOUBLE-OPERAND')
                    # print(operands)
                    # cmd.append(operands[0])
                    # cmd.append(operands[1])
                cmd.append(TRANSFORM_DICT[bytecode[0]])
                    # operands = list()
            elif instruction in MULTI_OP_CMD:
                cmd.append(TRANSFORM_DICT[bytecode[0]])
        elif instruction in STORE_CMD:
            cmd[0] = bytecode[1]
            current_cmd.append(cmd)
            cmd = list()
            cmd.append('')
            # operands = list()
        elif instruction == 'RETURN_VALUE':
            compiled_instructs.append(current_cmd)
            current_cmd = list()
    print("*" * 100)
    # print(compiled_instructs)
    return compiled_instructs
