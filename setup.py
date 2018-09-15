#!/usr/bin/env python
from setuptools import setup
from prettytable import __version__ as version


with open('README.md') as f:
    long_description = f.read()

setup(
    name='prettytable',
    version=version,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: BSD License',
        'Topic :: Text Processing'
    ],
    license="BSD (3 clause)",
    description='A simple Python library for easily displaying tabular data in a visually appealing ASCII table format',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Luke Maurits',
    author_email='luke@maurits.id.au',
    maintainer='Jazz Band',
    url='https://github.com/jazzband/prettytable',
    py_modules=['prettytable'],
    test_suite="prettytable_test",
)
