#!/usr/bin/env python
from setuptools import setup

VERSION = '1.0.0'
DESCRIPTION = "RedisBloomFilter: A bloom filter use redis as backend"

setup(
    name="pybloom",
    version=VERSION,
    description=DESCRIPTION,
    keywords=('data structures', 'bloom filter', 'bloom', 'filter',
              'probabilistic', 'set', 'redis'),
    url="https://github.com/atupal/RedisBloomFilter",
    license="MIT License",
    platforms=['any'],
    test_suite="pybloom.tests",
    zip_safe=True,
    packages=['redisfilter']
)
