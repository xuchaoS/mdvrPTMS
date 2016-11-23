#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'shangxc'
import unittest
from HTMLTestRunner import HTMLTestRunner
import time
import os

test_dir = '.'
discover = unittest.defaultTestLoader.discover(test_dir, pattern='test*.py')

if __name__ == '__main__':
    # runner = unittest.TextTestRunner()
    # runner.run(discover)
    filename = 'result_%s.html' % time.strftime('%Y%m%d-%H%M%S')
    with open(filename, 'wb') as f:
        runner = HTMLTestRunner(stream=f)
        runner.run(discover)
    os.system('start ' + filename)
