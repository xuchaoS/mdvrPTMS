#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'shangxc'
import sys

sys.path.append('..')
import unittest
import time
import random
import json
import binascii
import mdvr
# import mqclient
from gpsAutoTest import mqclient
from gpsAutoTest.config import *
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s ')


class TestRegister(unittest.TestCase):
    def setUp(self):
        self.mq = mqclient.MqClient(MQIP, '123459876543')

    def test7(self):
        '''正常注册'''
        self.register()

    def test13(self):
        '''正常注册（所有字段默认）'''
        self.register()

    def test14(self):
        '''正常注册（终端型号小于20位）'''
        self.register(terminal_type='12')

    def test15(self):
        '''正常注册（终端ID小于7位）'''
        self.mq.close()
        self.mq = mqclient.MqClient(MQIP, '123450000098')
        self.register(terminal_id='98', authentication_code='123450000098')

    def test16(self):
        '''正常注册（车牌颜色为0，车辆标志为VIN）'''
        self.register(plate_color=0, plate='abcdefg1234567890')

    def test17(self):
        '''正常注册（车牌标识含中文等非ascii字符）'''
        self.register(plate='京A0001')

    def tearDown(self):
        self.mdvr.close()
        self.mq.close()

    def register(self, phonenum=18812349876, ip=ACCESSIP, manufacturer_id='12345', terminal_id='9876543',
                 plate='BJ0001', authentication_code='123459876543', terminal_type='abcdef78901234567890',
                 plate_color=1,
                 resultnum=0):
        self.mdvr = mdvr.MDVR(phonenum, ip=ip, manufacturer_id=manufacturer_id, terminal_id=terminal_id,
                              plate=plate, authentication_code=authentication_code, terminal_type=terminal_type,
                              plate_color=plate_color, port=8896)
        self.mdvr.connect()
        self.mdvr.send_register()
        time.sleep(TINY_DELAY)
        # body = self.mq.get_sp_message('Register')
        # self.assertIsNotNone(body)
        # self.assertEqual(self.mdvr.authentication_code, body['UID'])
        # self.assertEqual(0, body['SerialNo'])
        # self.assertEqual(self.mdvr.manufacturer_id, body['ManufactureId'])
        # self.assertEqual(self.mdvr.terminal_type, body['Model'])
        # self.assertEqual(self.mdvr.terminal_id.rjust(7, '0'), body['TerminalId'])
        # self.assertEqual(self.mdvr.plate, body['VehicleId'], '车牌号不正确')
        # self.assertEqual(str(self.mdvr.phoneNum).rjust(12, '0'), body['SIM'])
        # self.mq.send_message('RegisterResponse', self.mdvr.authentication_code, {'UID': body['UID'],
        #                                                                          'SerialNo': 0,
        #                                                                          'ResultType': resultnum,
        #                                                                          'RegisterNo': body['UID'],
        #                                                                          'SIM': body['SIM'],
        #                                                                          'VehicleId': body['VehicleId']})
        result, messageid = self.mdvr.receive(LONGER_DELAY)
        self.assertEqual(resultnum, result)
        self.assertEqual(b'\x81\x00', messageid)


if __name__ == '__main__':
    unittest.main()
    input()
