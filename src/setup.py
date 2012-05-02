#!/usr/bin/env python
from setuptools import setup
from prettytable import __version__ as version

setup(
    name='prettytable',
    version=version,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Topic :: Text Processing'
    ],
    description='A simple Python library for easily displaying tabular data in a visually appealing ASCII table format',
    author='Luke Maurits',
    author_email='luke@maurits.id.au',
    url='http://code.google.com/p/prettytable',
    py_modules=['prettytable']
)
