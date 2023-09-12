from compile import get_func_bytecode
from base import Block, Signal, Clk, Module

block = Block()
block.set_time_scale('1ns', '1ps')
clk = Clk(frequency=100)  # 100MHz, 10ns
clk.initial()
a = Signal(width=4, value=0)
b = Signal(width=4, value=1)
c = Signal(width=4, value=2)
d = Signal(width=4, value=3)
e = Signal(width=4, value=4)
f = Signal(width=4, value=5)


def fun1():
    return 100


def func2(x):
    return 50 * x + 100


def func3(x, y):
    return x + y / 10


def func4(x):
    return x >> 1


def delay(t):
    block.delay(t)


@block.initial()
def func_test():
    a = 11
    c = a << 1
    print(c)
    b = a + 20
    print(b)
    delay(1)
    c = fun1()
    print(c)
    d = func2(a)

    e = func3(a, b)
    f = func4(a)
    # return c + d + e + f


block.run('1000ns')
# get_func_bytecode(func_test)
