#!/usr/bin/python
# -*- coding:utf-8 -*-
import datetime

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
from autoTest import mqclient
from config import *
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s ')


class TestAuthentication(unittest.TestCase):
    def setUp(self):
        phonenum = random.randint(10000000000, 99999999999)
        self.mq = mqclient.MqClient(MQIP, '123459876543')
        self.mdvr = mdvr.MDVR(phonenum, ip=ACCESSIP, manufacturer_id='12345', terminal_id='9876543',
                              plate='BJ0001', authentication_code='123459876543', terminal_type='abcdef78901234567890',
                              plate_color=1)
        self.mdvr.connect()

    def test19(self):
        '''鉴权码不存在数据接入缓存中但是在数据库中'''
        self.auth(needtomq=True, ispassed=0)

    def test20(self):
        '''鉴权码存在数据接入缓存中'''
        self.auth(needtomq=True, ispassed=0)
        # self.mdvr.close()
        # time.sleep(TINY_DELAY)
        # self.mq.get_sp_message('OnOffline')
        # self.mdvr.connect()
        self.auth(needtomq=False, ispassed=0)

    def test21(self):
        '''鉴权码不存在'''
        self.auth(needtomq=True, ispassed=1)

    def auth(self, needtomq=False, ispassed=0):
        self.mdvr.send_terminal_authentication()
        if needtomq:
            time.sleep(TINY_DELAY)
            body = self.mq.get_sp_message('Authenticate')
            self.assertIsNotNone(body)
            self.assertEqual(self.mdvr.authentication_code, body['UID'])
            self.assertEqual(0, body['SerialNo'])
            self.assertEqual(self.mdvr.authentication_code, body['RegisterNo'])
            self.assertEqual(str(self.mdvr.phoneNum).rjust(12, '0'), body['SIM'])
            self.mq.send_message('AuthenticateResponse', self.mdvr.authentication_code,
                                 {'UID': body['UID'],
                                  'SerialNo': 0,
                                  'RegisterNo': body['UID'],
                                  'SIM': body['SIM'],
                                  'IsPassed': ispassed,
                                  'VehicleId': self.mdvr.plate})
        result, messageid = self.mdvr.receive(LONGER_DELAY)
        self.assertEqual(ispassed, result)
        self.assertEqual(b'\x80\x01', messageid)
        if ispassed == 0:
            time.sleep(TINY_DELAY)
            # routing_key, body = self.mq.get_message()
            # routing_key, body = self.mq.get_message()
            body = self.mq.get_sp_message('OnOffline')
            # self.assertEqual('OnOffline', routing_key)
            self.assertIsNotNone(body)
            self.assertEqual(self.mdvr.authentication_code, body['UID'])
            self.assertEqual((datetime.datetime.now()-datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')[: 14], body['OnOffLineTime'][: 14])
            self.assertEqual(1, body['IsOnline'], body)

        # self.mdvr.close()
        # time.sleep(TINY_DELAY)
        # body = self.mq.get_sp_message('OnOffline')
        # self.assertIsNotNone(body)
        # self.assertEqual(self.mdvr.authentication_code, body['UID'])
        # self.assertEqual(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')[: 14], body['OnOffLineTime'][: 14])
        # self.assertEqual(0, body['IsOnline'], body)

    def tearDown(self):
        self.mq.close()


if __name__ == '__main__':
    unittest.main()
