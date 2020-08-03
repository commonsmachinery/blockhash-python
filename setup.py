#!/usr/bin/env python

import os
import setuptools

import blockhash

_APP_PATH = os.path.dirname(blockhash.__file__)

with open(os.path.join(_APP_PATH, 'resources', 'README.md')) as f:
      long_description = f.read()

with open(os.path.join(_APP_PATH, 'resources', 'requirements.txt')) as f:
      install_requires = [s.strip() for s in f.readlines()]

setuptools.setup(
    name='phash-blockhashio',
    version=blockhash.__version__,
    description='Perceptual image hash calculation tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Commons Machinery',
    author_email='dev@commonsmachinery.se',
    license='MIT',
    scripts=[
        'blockhash/resources/scripts/blockhash'
    ],
    install_requires=install_requires,
    tests_require=install_requires + ['nose2'],
    url='https://github.com/dsoprea/blockhash-python',
    packages=setuptools.find_packages(exclude=['tests']),
    include_package_data=True,
    package_data={
        'blockhash': [
            'resources/README.md',
            'resources/requirements.txt',
        ],
    },
)
