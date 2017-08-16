#!/usr/bin/env python

from setuptools import setup
import sys


if sys.version_info < (3,):
    print("crypto-arbitrage requires Python version >= 3.0")
    sys.exit(1)

setup(name='crypto-arbitrage',
      packages = ["arbitrage"],
      version='0.3',
      description='crypto asset arbitrage opportunity watcher, market maker, hedge and arbitrage',
      author='Phil Song',
      author_email='songbohr@gmail.com',
      url='https://github.com/philsong/crypto-arbitrage',
      arbitrage=['bin/crypto-arbitrage'],
      test_suite='nose.collector',
      tests_require=['nose'],
  )
