from setuptools import setup

import multiprocessing

setup(
    name='buckeye',
    version='1.2',
    packages=['buckeye'],
    description='Classes and iterators for the Buckeye Corpus',
    url='http://github.com/scjs/buckeye/',
    test_suite='nose.collector',
    tests_require=['nose', 'mock'],
    )
