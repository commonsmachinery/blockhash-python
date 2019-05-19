#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='blockhash',
    version='0.1.1',
    description='Perceptual image hash calculation tool',
    author='Commons Machinery',
    author_email='dev@commonsmachinery.se',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'blockhash=blockhash.command_line:main',
        ],
    },
    install_requires=['pillow'],
)
