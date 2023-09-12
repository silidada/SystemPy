# coding: utf-8
from setuptools import setup, find_packages
 
setup(
    name="SystemPy7",
    author="ChenHaha",
    version="1.0.0",
    author_email="596838981@qq.com",
    packages=find_packages(),
    description="System_python",
    long_description="System_python",
    license='Apache2.0',
    install_requires=[
        'requests',
        'tqdm',
        'pyvcd',
    ],
)
