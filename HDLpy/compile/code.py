#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/10 20:29
# @Author : ChenHaHa

"""
This module is used to define the constants used in the compiler.

Currently, the following constants are defined:
    LOAD_CMD: The command that loads the value of the variable.
        - LOAD_CONST: Load the value of the constant.
        - LOAD_FAST: Load the value of the local variable.
        - LOAD_GLOBAL: Load the value of the global variable.

    STORE_CMD: The command that stores the value of the variable.
        - STORE_FAST: Store the value of the local variable.

    COMPUTE_CMD: The command that computes the value of the variable.
        - BINARY_ADD: Add two values.
        - BINARY_SUBTRACT: Subtract two values.
        - BINARY_MULTIPLY: Multiply two values.
        - BINARY_TRUE_DIVIDE: Divide two values.
        - BINARY_RSHIFT: Right shift two values.
        - BINARY_LSHIFT: Left shift two values.


    we will add more commands in the future.
    welcome to contribute.
"""

LOAD_CMD = {'LOAD_CONST', 'LOAD_FAST', 'LOAD_GLOBAL'}

STORE_CMD = {'STORE_FAST', 'STORE_GLOBAL'}

COMPUTE_CMD = {'BINARY_ADD', 'BINARY_SUBTRACT', 'BINARY_MULTIPLY', 'BINARY_TRUE_DIVIDE', 'BINARY_RSHIFT',
               'BINARY_LSHIFT'}

MULTI_OP_CMD = {'BINARY_ADD', 'BINARY_SUBTRACT', 'BINARY_MULTIPLY', 'BINARY_TRUE_DIVIDE'}
DOUBLE_OP_CMD = {'BINARY_RSHIFT', 'BINARY_LSHIFT'}

DELAY_CMD = {'delay'}

SPECIAL_FUNCTION = {"print": print}

def compile_binary_add(a, b):
    return a + b


def compile_binary_subtract(a, b):
    return a - b


def compile_binary_multiply(a, b):
    return a * b


def compile_binary_true_divide(a, b):
    return a / b


def compile_binary_rshift(a, b):
    return a >> b


def compile_binary_lshift(a, b):
    return a << b


TRANSFORM_DICT = {'BINARY_ADD': compile_binary_add,
                  'BINARY_SUBTRACT': compile_binary_subtract,
                  'BINARY_MULTIPLY': compile_binary_multiply,
                  'BINARY_TRUE_DIVIDE': compile_binary_true_divide,
                  'BINARY_RSHIFT': compile_binary_rshift,
                  'BINARY_LSHIFT': compile_binary_lshift}
