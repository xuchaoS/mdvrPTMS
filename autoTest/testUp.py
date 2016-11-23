#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'shangxc'
import sys

sys.path.append('..')
import datetime
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

BINDIND_KEY = ('Register',
               # 'RegisterResponse',
               'UnRegister',
               # 'UnRegisterResponse',
               'Authenticate',
               # 'AuthenticateResponse',
               # 'OnOffline',
               'AlarmInfo',
               'ManualConfirmAlert',
               'BusinessAlert',
               'DeviceAlert',
               # 'RoundRegion',
               # 'DelRoundRegion',
               # 'SquareRegion',
               # 'DelSquareRegion',
               # 'PolygonsRegion',
               # 'DelPolygonsRegion',
               # 'RouteInfo',
               # 'DelRouteRegion',
               'GenenalResponse',
               'QueryAllParam',
               'QueryPartParam',
               'SetTermParam',
               'QueryParaResponse',
               'Test808')


class TestUp(unittest.TestCase):
    def setUp(self):
        self.mq = mqclient.MqClient(MQIP, '123459876543')
        self.mdvr = mdvr.MDVR(18812345678, ip=ACCESSIP, manufacturer_id='12345', terminal_id='9876543',
                              plate='BJ0001', authentication_code='123459876543', terminal_type='abcdef78901234567890',
                              plate_color=1)
        self.mdvr.connect()
        self.mdvr.send_terminal_authentication()
        time.sleep(TINY_DELAY)
        body = self.mq.get_sp_message('Authenticate')
        if body:
            self.mq.send_message('AuthenticateResponse', self.mdvr.authentication_code,
                                 {'UID': body['UID'],
                                  'SerialNo': 0,
                                  'RegisterNo': body['UID'],
                                  'SIM': body['SIM'],
                                  'IsPassed': 0,
                                  'VehicleId': self.mdvr.plate})
        self.mdvr.receive(LONGER_DELAY)

    def test18(self):
        '''正常注销'''
        self.mdvr.send_logout()
        time.sleep(TINY_DELAY)
        body = self.mq.get_sp_message('UnRegister')
        self.assertIsNotNone(body)
        self.assertEqual(self.mdvr.authentication_code, body['UID'])
        self.assertEqual(1, body['SerialNo'])
        self.assertEqual(self.mdvr.authentication_code, body['RegisterNo'])
        self.assertEqual(str(self.mdvr.phoneNum).rjust(12, '0'), body['SIM'])
        self.mq.send_message('UnRegisterResponse', self.mdvr.authentication_code, {'UID': body['UID'],
                                                                                   'SerialNo': 1,
                                                                                   'RegisterNo': body['UID'],
                                                                                   'SIM': body['SIM'],
                                                                                   'IsPassed': 0})
        self.get_and_assert_reply()
        self.assert_clean()

    def test23(self):
        '''终端心跳'''
        self.mdvr.send_heart_beat()
        self.get_and_assert_reply()
        self.assert_clean()

    def test24(self):
        '''正常位置信息汇报（无报警）'''
        self.mdvr.set_gps(mdvr.GPS(longitude=136.9876, latitude=66.6599, height=200, speed=30, direction=300))
        self.mdvr.send_location_information()
        time.sleep(TINY_DELAY)
        self.get_and_assert_gps()
        self.get_and_assert_reply()
        self.assert_clean()

    def test25(self):
        '''南纬、西经的经纬度（经纬度为为负）'''
        self.mdvr.set_gps(mdvr.GPS(longitude=-136.9876, latitude=-39.1234, height=200, speed=30, direction=300))
        self.mdvr.send_location_information()
        time.sleep(TINY_DELAY)
        self.get_and_assert_gps()
        self.get_and_assert_reply()
        self.assert_clean()

    def test81(self):
        '''位置信息无效'''
        self.mdvr.set_gps(mdvr.GPS())
        self.mdvr.send_location_information()
        time.sleep(TINY_DELAY)
        self.get_and_assert_gps()
        self.get_and_assert_reply()
        self.assert_clean()

    def test26(self):
        '''一键报警'''
        self.mdvr.set_gps(mdvr.GPS(longitude=136.9876, latitude=39.1234, height=200, speed=30, direction=300))
        self.mdvr.alarm_flag[0] = 1
        self.mdvr.send_location_information()
        time.sleep(TINY_DELAY)
        self.get_and_assert_gps()
        self.get_and_assert_AlarmInfo(1)
        self.get_and_assert_reply()
        self.assert_clean()

    def test27(self):
        '''支持的报警标志位全部为1'''
        self.mdvr.set_gps(mdvr.GPS(longitude=-136.9876, latitude=-39.1234, height=200, speed=30, direction=300))
        self.mdvr.alarm_flag = [1 for i in self.mdvr.alarm_flag]
        self.mdvr.send_location_information()
        time.sleep(TINY_DELAY)
        self.get_and_assert_gps()
        self.get_and_assert_AlarmInfo(1)
        self.get_and_assert_BusinessAlert(1, range(14))
        self.get_and_assert_DeviceAlert(1, range(8))
        self.get_and_assert_reply()
        self.assert_clean()

    def test28(self):
        '''2次支持的报警标志位全部为1'''
        self.mdvr.set_gps(mdvr.GPS(longitude=-136.9876, latitude=-39.1234, height=200, speed=30, direction=300))
        self.mdvr.alarm_flag = [1 for i in self.mdvr.alarm_flag]
        self.mdvr.send_location_information()
        time.sleep(TINY_DELAY)
        self.get_and_assert_gps()
        self.get_and_assert_AlarmInfo(1)
        self.get_and_assert_BusinessAlert(1, range(14))
        self.get_and_assert_DeviceAlert(1, range(8))
        self.get_and_assert_reply()
        self.mdvr.alarm_flag = [1 for i in self.mdvr.alarm_flag]
        self.mdvr.send_location_information()
        time.sleep(TINY_DELAY)
        self.get_and_assert_gps()
        self.get_and_assert_AlarmInfo(2)
        self.get_and_assert_BusinessAlert(2, [5, 1, 2, 8, 10, 11])
        self.get_and_assert_DeviceAlert(2, [])
        self.get_and_assert_reply()
        self.assert_clean()

    def test29(self):
        '''1次支持的报警标志位全部为1，1次报警标志位全部为0'''
        self.mdvr.set_gps(mdvr.GPS(longitude=-136.9876, latitude=-39.1234, height=200, speed=30, direction=300))
        self.mdvr.alarm_flag = [1 for i in self.mdvr.alarm_flag]
        self.mdvr.send_location_information()
        time.sleep(TINY_DELAY)
        self.get_and_assert_gps()
        self.get_and_assert_AlarmInfo(1)
        self.get_and_assert_BusinessAlert(1, range(14))
        self.get_and_assert_DeviceAlert(1, range(8))
        self.get_and_assert_reply()
        self.mdvr.alarm_flag = [0 for i in self.mdvr.alarm_flag]
        self.mdvr.send_location_information()
        time.sleep(TINY_DELAY)
        self.get_and_assert_gps()
        self.get_and_assert_BusinessAlert(2, [])
        self.get_and_assert_DeviceAlert(2, [])
        self.get_and_assert_reply()
        self.assert_clean()

    def test83(self):
        '''1次支持的报警标志位全部为1，1次报警标志位全部为0,再次支持的报警标志位全部为1'''
        self.mdvr.set_gps(mdvr.GPS(longitude=-136.9876, latitude=-39.1234, height=200, speed=30, direction=300))
        self.mdvr.alarm_flag = [1 for i in self.mdvr.alarm_flag]
        self.mdvr.send_location_information()
        time.sleep(TINY_DELAY)
        self.get_and_assert_gps()
        self.get_and_assert_AlarmInfo(1)
        self.get_and_assert_BusinessAlert(1, range(14))
        self.get_and_assert_DeviceAlert(1, range(8))
        self.get_and_assert_reply()
        self.mdvr.alarm_flag = [0 for i in self.mdvr.alarm_flag]
        self.mdvr.send_location_information()
        time.sleep(TINY_DELAY)
        self.get_and_assert_gps()
        self.get_and_assert_BusinessAlert(2, [])
        self.get_and_assert_DeviceAlert(2, [])
        self.get_and_assert_reply()
        self.mdvr.alarm_flag = [1 for i in self.mdvr.alarm_flag]
        self.mdvr.send_location_information()
        time.sleep(TINY_DELAY)
        self.get_and_assert_gps()
        self.get_and_assert_AlarmInfo(3)
        self.get_and_assert_BusinessAlert(3, range(14))
        self.get_and_assert_DeviceAlert(3, range(8))
        self.get_and_assert_reply()
        self.assert_clean()

    def test30(self):
        '''状态标志位全部为1'''
        self.mdvr.set_gps(mdvr.GPS(longitude=-136.9876, latitude=-39.1234, height=200, speed=30, direction=300))
        self.mdvr.status = [1 for i in self.mdvr.status]
        self.mdvr.send_location_information()
        time.sleep(TINY_DELAY)
        self.get_and_assert_gps()
        self.get_and_assert_reply()
        self.assert_clean()

    def test31(self):
        '''多个指令连在一起'''
        self.mdvr.set_gps(mdvr.GPS(longitude=-136.9876, latitude=-39.1234, height=200, speed=30, direction=300))
        alarm_flag = mdvr.int_to_dword(mdvr.bitlist_to_int(self.mdvr.alarm_flag))
        status = mdvr.int_to_dword(mdvr.bitlist_to_int(self.mdvr.status))
        latitude = mdvr.int_to_dword(abs(int(self.mdvr.gps.latitude * 1000000)))
        longitude = mdvr.int_to_dword(abs(int(self.mdvr.gps.longitude * 1000000)))
        height = mdvr.int_to_word(self.mdvr.gps.height)
        speed = mdvr.int_to_word(self.mdvr.gps.speed)
        direction = mdvr.int_to_word(self.mdvr.gps.direction)
        times = mdvr.int_to_bcd(int(mdvr.strftime('%y%m%d%H%M%S')), 6)
        gps_body = b'%s' * 8 % (alarm_flag,
                                status,
                                latitude,
                                longitude,
                                height,
                                speed,
                                direction,
                                times,)
        message = (bytes(mdvr.Message(mdvr.MESSAGE_ID['heart beat'], self.mdvr.phoneNum, b'', 1)) +
                   bytes(mdvr.Message(mdvr.MESSAGE_ID['location information'], self.mdvr.phoneNum, gps_body, 2)) +
                   bytes(mdvr.Message(mdvr.MESSAGE_ID['location information'], self.mdvr.phoneNum, gps_body, 3)))
        self.mdvr.send(message, add_to_waiting_response=False)
        time.sleep(TINY_DELAY)
        self.get_and_assert_gps()
        self.get_and_assert_gps()

        self.get_and_assert_reply()
        # self.get_and_assert_reply()
        # self.get_and_assert_reply()
        self.assert_clean()

    def test32(self):
        '''校验码不正确'''
        self.mdvr.sock.send(binascii.a2b_hex('7e000200000188123456780001727e'))
        self.assertIsNone(self.mdvr.receive_message(3))
        self.assert_clean()

    def test33(self):
        '''发送非协议指令'''
        self.mdvr.sock.send(b'asd;lkjf;sadkjf;sdalkjf;sadlkjf;sdalkjf')
        self.assertIsNone(self.mdvr.receive_message(3))
        self.assert_clean()

    def test35(self):
        '''连接后未鉴权，直接发送其他指令(未换手机号)'''
        self.mdvr.close()
        time.sleep(LONGER_DELAY)
        self.mdvr.connect()
        self.mdvr.send_location_information()
        self.assertIsNone(self.mdvr.receive_message(3), '不应有应答')
        time.sleep(TINY_DELAY)
        self.assertIsNone(self.mq.get_sp_message('GpsInfo'))
        with self.assertRaises(OSError):
            self.mdvr.send_location_information()
        self.assert_no_json_message()

    def test35_2(self):
        '''连接后未鉴权，直接发送其他指令（换手机号）'''
        self.mdvr.close()
        time.sleep(LONGER_DELAY)
        self.mdvr.phoneNum = random.randint(10000000000, 99999999999)
        self.mdvr.connect()
        self.mdvr.send_location_information()
        self.assertIsNone(self.mdvr.receive_message(3))
        time.sleep(TINY_DELAY)
        self.assertIsNone(self.mq.get_sp_message('GpsInfo'))
        with self.assertRaises(OSError):
            self.mdvr.send_location_information()
        self.assert_no_json_message()

    def test36(self):
        '''鉴权失败后发送消息'''
        self.mdvr.close()
        time.sleep(LONGER_DELAY)
        self.mdvr.phoneNum = random.randint(10000000000, 99999999999)
        self.mdvr.connect()
        self.mdvr.send_terminal_authentication()
        time.sleep(TINY_DELAY)
        body = self.mq.get_sp_message('Authenticate')
        if body:
            self.mq.send_message('AuthenticateResponse', self.mdvr.authentication_code,
                                 {'UID': body['UID'],
                                  'SerialNo': 0,
                                  'RegisterNo': body['UID'],
                                  'SIM': body['SIM'],
                                  'IsPassed': 1,
                                  'VehicleId': self.mdvr.plate})
        self.mdvr.receive(LONGER_DELAY)
        self.mdvr.send_location_information()
        self.assertIsNone(self.mdvr.receive_message(3))
        time.sleep(TINY_DELAY)
        self.assertIsNone(self.mq.get_sp_message('GpsInfo'), '不应上报该gps')
        with self.assertRaises(OSError):
            self.mdvr.send_location_information()
        self.assert_no_json_message()

    def test37(self):
        '''消息id不存在'''
        self.mdvr.send_message(b'\x66\x66', b'', add_to_waiting_response=False)
        time.sleep(TINY_DELAY)
        message = self.mdvr.receive_message(LONGER_DELAY)
        self.assertIsNotNone(message, '未收到应答')
        self.assertTrue(mdvr.message_start_end_right(message))
        self.assertTrue(mdvr.check_checksum(mdvr.recover_escape(message[1: -1])), '校验码不正确')
        self.assertEqual(3, message[-3])
        self.assertEqual(b'\x80\x01', message[1:3])
        self.assert_clean()

    def test38(self):
        '''消息体长度不正确'''
        self.mdvr.send(binascii.a2b_hex(
            '7e0200003001881234567800010000000000000000000000000000002a0000000000001606001009200104000000000202000003020000b57e'),
            add_to_waiting_response=False)
        time.sleep(TINY_DELAY)
        self.assertIsNone(self.mdvr.receive_message(3))
        self.assertIsNone(self.mq.get_sp_message('GpsInfo'))
        self.assert_clean()

    def test40(self):
        '''下发需转义的指令'''
        self.mdvr.next_message_num = 124
        self.mdvr.send_heart_beat()
        self.get_and_assert_reply()
        self.assert_clean()

    def test41(self):
        '''接收到已转义的指令'''
        self.mdvr.set_gps(mdvr.GPS(72.777096, 72.777096, 0, 0, 0))
        self.mdvr.send_location_information()
        time.sleep(TINY_DELAY)
        self.get_and_assert_gps()
        self.get_and_assert_reply()
        self.assert_clean()

    def get_and_assert_gps(self):
        # time.sleep(0.1)
        body = self.mq.get_sp_message('GpsInfo')
        # self.assertEqual('GpsInfo', routing_key)
        self.assertIsNotNone(body, '没有上报GPS')
        self.assert_gps(body)

    # def get_and_assert_gps_ex(self):
    #     body = self.mq.get_sp_message('GpsInfo')
    #     self.assert_gps_ex(body)

    # def assert_gps_ex(self, body):
    #     self.assertEqual(self.mdvr.authentication_code, body['UID'])
    #     self.assertEqual(1 if self.mdvr.gps.direction or self.mdvr.gps.height or self.mdvr.gps.latitude or
    #                           self.mdvr.gps.longitude or self.mdvr.gps.speed else 0, int(body['Valid']))
    #     self.assertEqual('%.6f' % float(self.mdvr.gps.longitude), '%.6f' % float(body['Longitude']), '经度不正确或精度不足')
    #     self.assertEqual('%.6f' % float(self.mdvr.gps.latitude), '%.6f' % float(body['Latitude']), '经度不正确或精度不足')
    #     self.assertEqual(self.mdvr.gps.height, int(body['Height']))
    #     self.assertAlmostEqual(self.mdvr.gps.speed / 10, float(body['Speed']))
    #     self.assertEqual(self.mdvr.gps.direction, int(body['Direction']))
    #     self.assertEqual(
    #         (datetime.datetime.now() - datetime.timedelta(seconds=TINY_DELAY)).strftime('%Y-%m-%d-%H-%M-%S'),
    #         body['GpsTime'])
    #     self.assertEqual(mdvr.bitlist_to_int(self.mdvr.alarm_flag), int(body['AlarmFlag']))
    #     self.assertEqual(mdvr.bitlist_to_int(self.mdvr.status), int(body['Status']))
    #     self.assertEqual(self.mdvr.plate, body['VehicleId'])

    def get_and_assert_reply(self):
        # time.sleep(0.1)
        # result, messageid = self.mdvr.receive(10)
        # self.assertEqual(0, result)
        # self.assertEqual(b'\x80\x01', messageid)
        message = self.mdvr.receive_message(LONGER_DELAY)
        self.assertIsNotNone(message, '未收到应答')
        self.assertTrue(mdvr.message_start_end_right(message))
        self.assertTrue(mdvr.check_checksum(mdvr.recover_escape(message[1: -1])), '校验码不正确')
        self.assertEqual(0, message[-3])
        self.assertEqual(b'\x80\x01', message[1:3])

    def assert_gps(self, body):
        self.assertEqual(self.mdvr.authentication_code, body['UID'])
        self.assertEqual('A' if self.mdvr.gps.direction or self.mdvr.gps.height or self.mdvr.gps.latitude or
                              self.mdvr.gps.longitude or self.mdvr.gps.speed else 'N', body['Valid'])
        self.assertEqual('%.6f' % self.mdvr.gps.longitude, body['Longitude'])
        self.assertEqual('%.6f' % self.mdvr.gps.latitude, body['Latitude'])
        self.assertEqual(self.mdvr.gps.height, body['Height'])
        self.assertEqual('%.1f' % (self.mdvr.gps.speed / 10), body['Speed'])
        self.assertEqual(str(self.mdvr.gps.direction), body['Direction'])
        self.assertEqual(
            (datetime.datetime.now() - datetime.timedelta(hours=8, seconds=TINY_DELAY)).strftime('%Y-%m-%d %H:%M:%S'),
            body['GpsTime'])
        self.assertEqual(mdvr.bitlist_to_int(self.mdvr.alarm_flag), body['AlarmFlag'])
        self.assertEqual(mdvr.bitlist_to_int(self.mdvr.status), body['Status'])
        self.assertEqual(self.mdvr.plate, body['VehicleId'])

    def get_and_assert_AlarmInfo(self, serial_no):
        # time.sleep(0.1)
        body = self.mq.get_sp_message('AlarmInfo')
        self.assertEqual(self.mdvr.authentication_code, body['UID'])
        self.assertEqual(serial_no, body['SerialNo'])
        self.assert_gps(body['GpsInfo'])
        self.assertEqual("1,4,00000000;2,2,0000;3,2,001e;", body['AdditionalInfo'])

    def get_and_assert_BusinessAlert(self, serial_no, alert_type_list):
        # time.sleep(0.1)
        alert_types = set(alert_type_list)
        while True:
            body = self.mq.get_sp_message('BusinessAlert')
            if body:
                self.assertEqual(self.mdvr.authentication_code, body['UID'])
                self.assertEqual(serial_no, body['SerialNo'])
                self.assert_gps(body['GpsInfo'])
                self.assertIn(body['AlertType'], alert_types)
                alert_types.remove(int(body['AlertType']))
                self.assertIsInstance(body['AdditionalInfo'], str)
                # print(alert_types)
            else:
                break
        self.assertSetEqual(set(), alert_types)

    def get_and_assert_DeviceAlert(self, serial_no, alert_type_list):
        # time.sleep(0.1)
        alert_types = set(alert_type_list)
        while True:
            body = self.mq.get_sp_message('DeviceAlert')
            if body:
                self.assertEqual(self.mdvr.authentication_code, body['UID'])
                self.assertEqual(serial_no, body['SerialNo'])
                self.assert_gps(body['GpsInfo'])
                self.assertIn(body['AlertType'], alert_types)
                alert_types.remove(int(body['AlertType']))
                self.assertIsInstance(body['AdditionalInfo'], str)
                # print(alert_types)
            else:
                break
        self.assertSetEqual(set(), alert_types)

    def tearDown(self):
        try:
            self.mq.close()
            self.mdvr.close()
        except:
            pass

    def assert_clean(self):
        self.assert_no_receive()
        self.assert_no_json_message()

    def assert_no_receive(self):
        a = self.mdvr.receive_message(1)
        self.assertIsNone(a, '\n' + mdvr.printfuled(a) if a else None)

    def assert_no_json_message(self):
        for key in BINDIND_KEY:
            self.assertIsNone(self.mq.get_sp_message(key))


if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestUp('test35'))
    runner = unittest.TextTestRunner()
    runner.run(suite)
