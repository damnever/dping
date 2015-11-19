# -*- coding: utf-8 -*-

from setuptools import setup
from distutils.core import Extension


setup(
    name='dping',
    version='0.1',
    description='A simple ping program write in Python.',
    author='Damnever',
    author_email='dxc.wolf@gmail.com',
    license='The BSD 3-Clause License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='ping',
    packages=['dping'],
    ext_modules=[Extension('dping._sigpending', sources=['dping/_sigpending.c'])],
    entry_points={
        'console_scripts': [
            'dping=dping:ping',
        ]
    },
)
