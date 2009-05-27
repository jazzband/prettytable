#!/usr/bin/env python
from setuptools import setup
from prettytable import __VERSION__ as version

setup(
    name='prettytable',
    version=version,
    description='A simple Python library for easily displaying tabular data in a visually appealing ASCII table format',
    author='Luke Maurits',
    author_email='luke@maurits.id.au',
    url='http://www.luke.maurits.id.au/software/prettytable',
    license='http://www.luke.maurits.id.au/software/bsdlicense.txt',
    py_modules=['prettytable']
)
