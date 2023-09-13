#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/13 20:03
# @Author : ChenHaHa

def print_warning(string):
    print(f"\033[93mWarning: {string}\033[0m")

def print_error(string):
    print(f"\033[91mError: {string}\033[0m")

def print_info(string):
    print(f"\033[94mWarning: {string}\033[0m")


if __name__ == '__main__':
    print_warning("This is a warning")
    print_error("This is a error")
    print_info("This is a info")
