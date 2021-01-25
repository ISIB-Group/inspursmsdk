#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup for inspur_sdk."""

import ast
import io
import setuptools
from setuptools import setup

INSTALL_REQUIRES = (
    ['pycryptodome >= 3.5.0', 'PyYAML', 'requests >= 2.9.1', 'Jpype1']
)


def version():
    """Return version string."""
    with io.open('ism.py') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


with io.open('README.md') as readme:
    setup(
        name='inspursmsdk',
        version=version(),
        description='inspur server manager api',
        long_description=readme.read(),
        license='Expat License',
        author='Wangbaoshan',
        author_email='wangbaoshan@inspur.com',
        url='https://github.com/ISIB-Group/inspursmsdk',
        classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
        ],
		install_requires=INSTALL_REQUIRES,
        py_modules=['ism'],
		packages=setuptools.find_packages(),
		include_package_data=True
    )
