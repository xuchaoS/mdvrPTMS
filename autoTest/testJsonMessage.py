#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'shangxc'
import sys

sys.path.append('..')
import unittest
import time
import random
import logging
import json
import binascii
import decimal
import datetime
import mdvr
# import mqclient
from autoTest import mqclient
from config import *
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s ')


def time_str_to_bcd(value):
    a = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    a += datetime.timedelta(hours=8)
    b = a.strftime('%y%m%d%H%M%S')
    return binascii.a2b_hex(b)


# @unittest.skipIf(__name__ != '__main__', 'not get ready')
class TestJsonMessage(unittest.TestCase):
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

    def test42(self):
        '''设置多边形区域（区域属性6、8）'''
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             'RegionID': 255,
                             'RegionProperty': [6, 8],
                             'PointCount': 3,
                             'PointsList': [{'Longitude': '136.123465', 'Latitude': '49.987612'},
                                            {'Longitude': '136.123542', 'Latitude': '49.987634'},
                                            {'Longitude': '136.123461', 'Latitude': '49.987556'},
                                            ]
                             }
        self.mq.send_message('PolygonsRegion', '123459876543', self.json_message)
        # self.assertEqual(self.gen_PolygonsRegion(), self.mdvr.receive_message(LONGER_DELAY))
        self.receive_and_assert_message(self.gen_PolygonsRegion())

    def test43(self):
        '''设置多边形区域（区域属性0、1、2、3、4、5、7、9）'''
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             'RegionID': 255,
                             'RegionProperty': [0, 1, 2, 3, 4, 5, 7, 9],
                             'StartTime': '2016-07-06 00:00:00',
                             'EndTime': '2017-12-31 23:59:59',
                             'MaxSpeed': 80,
                             'OverSpeedDuration': 3,
                             'PointCount': 3,
                             'PointsList': [{'Longitude': '136.123498', 'Latitude': '49.987698'},
                                            {'Longitude': '136.123565', 'Latitude': '49.987645'},
                                            {'Longitude': '136.123445', 'Latitude': '49.987534'},
                                            ]
                             }
        self.mq.send_message('PolygonsRegion', '123459876543', self.json_message)
        # self.assertEqual(self.gen_PolygonsRegion(), self.mdvr.receive_message(LONGER_DELAY))
        self.receive_and_assert_message(self.gen_PolygonsRegion())

    @unittest.skip
    def test78(self):
        '''设置多边形区域（经纬度为负数）'''
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             'RegionID': 255,
                             'RegionProperty': [0, 1, 2, 3, 4, 5, 7, 9],
                             'StartTime': '2016-07-06 00:00:00',
                             'EndTime': '2017-12-31 23:59:59',
                             'MaxSpeed': 80,
                             'OverSpeedDuration': 3,
                             'PointCount': 3,
                             'PointsList': [{'Longitude': '-136.123491', 'Latitude': '-49.987650'},
                                            {'Longitude': '-136.123565', 'Latitude': '-49.987646'},
                                            {'Longitude': '-136.123434', 'Latitude': '-49.987527'},
                                            ]
                             }
        self.mq.send_message('PolygonsRegion', '123459876543', self.json_message)
        # self.assertEqual(self.gen_PolygonsRegion(), self.mdvr.receive_message(LONGER_DELAY))
        self.receive_and_assert_message(self.gen_PolygonsRegion())

    # def test44(self):
    #     '''设置多边形区域（单个UID）'''
    #     self.json_message = {'UID': '123459876543',
    #                          'SerialNo': 65535,
    #                          'RegionID': 255,
    #                          'RegionProperty': [2, 3, 4, 5, 7, 9],
    #                          'PointCount': 3,
    #                          'PointsList': [{'Longitude': -136.1234, 'Latitude': -49.9876},
    #                                         {'Longitude': -136.1235, 'Latitude': -49.9876},
    #                                         {'Longitude': -136.1234, 'Latitude': -49.9875},
    #                                         ]
    #                          }
    #     self.mq.send_message('PolygonsRegion', '123459876543', self.json_message)
    #     # self.assertEqual(self.gen_PolygonsRegion(), self.mdvr.receive_message(LONGER_DELAY))
    #     self.receive_and_assert_message(self.gen_PolygonsRegion())

    # def test45(self):
    #     '''设置多边形区域（多个UID）'''
    #     self.mdvr2 = mdvr.MDVR(18812345677, ip=ACCESSIP, manufacturer_id='12345', terminal_id='9876544',
    #                            plate='BJ0001', authentication_code='123459876544', terminal_type='abcdef78901234567890',
    #                            plate_color=1)
    #     self.mdvr2.connect()
    #     self.mdvr2.send_terminal_authentication()
    #     time.sleep(TINY_DELAY)
    #     body = self.mq.get_sp_message('Authenticate')
    #     if body:
    #         self.mq.send_message('AuthenticateResponse', self.mdvr2.authentication_code,
    #                              {'UID': body['UID'],
    #                               'SerialNo': 0,
    #                               'RegisterNo': body['UID'],
    #                               'SIM': body['SIM'],
    #                               'IsPassed': 0})
    #     self.mdvr2.receive(LONGER_DELAY)
    #     self.json_message = {'UID': ['123459876543'
    #                                  '123459876544'
    #                                  ],
    #                          'SerialNo': 65535,
    #                          'RegionID': 255,
    #                          'RegionProperty': [2, 3, 4, 5, 7, 9],
    #                          'PointCount': 3,
    #                          'PointsList': [{'Longitude': -136.1234, 'Latitude': -49.9876},
    #                                         {'Longitude': -136.1235, 'Latitude': -49.9876},
    #                                         {'Longitude': -136.1234, 'Latitude': -49.9875},
    #                                         ]
    #                          }
    #     self.mq.send_message('PolygonsRegion', '123459876543', self.json_message)
    #     # self.assertEqual(self.gen_PolygonsRegion(), self.mdvr.receive_message(LONGER_DELAY))
    #     self.receive_and_assert_message(self.gen_PolygonsRegion())
    #     self.assertEqual(self.gen_PolygonsRegion(self.mdvr2.phoneNum), self.mdvr2.receive_message(LONGER_DELAY))

    def test46(self):
        '''删除多边形区域（区域总数小于125）'''
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             'RegionCount': 3,
                             'RegionList': [1, 2, 3]
                             }
        self.mq.send_message('DelPolygonsRegion', '123459876543', self.json_message)
        # self.assertEqual(self.gen_DelPolygonsRegion(), self.mdvr.receive_message(LONGER_DELAY))
        self.receive_and_assert_message(self.gen_DelPolygonsRegion())

    def test48(self):
        '''删除多边形区域（区域总数为0）'''
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             'RegionCount': 0,
                             }
        self.mq.send_message('DelPolygonsRegion', '123459876543', self.json_message)
        # self.assertEqual(self.gen_DelPolygonsRegion(), self.mdvr.receive_message(LONGER_DELAY))
        self.receive_and_assert_message(self.gen_DelPolygonsRegion())

    def test49(self):
        '''设置路线（区域属性无）'''
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             'RouteId': 255,
                             'RouteAttribute': [],
                             'PointCount': 2,
                             'PointsList': [{'InflexionId': 1,
                                             'RoadId': 1,
                                             'Latitude': '39.987654',
                                             'Longitude': '136.123456',
                                             'RoadWidth': 55,
                                             'RoadAttribute': [2, 4],
                                             },
                                            {'InflexionId': 2,
                                             'RoadId': 2,
                                             'Latitude': '40.987654',
                                             'Longitude': '133.123456',
                                             'RoadWidth': 66,
                                             'RoadAttribute': [2, 4],
                                             }]}
        self.mq.send_message('RouteInfo', '123459876543', self.json_message)
        self.receive_and_assert_message(self.gen_RouteInfo())

    def test50(self):
        '''设置路线（区域属性0、2、3、4、5）'''
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             'RouteId': 255,
                             'RouteAttribute': [0, 2, 3, 4, 5],
                             'StartTime': '2016-07-06 00:00:00',
                             'EndTime': '2017-12-31 23:59:59',
                             'PointCount': 2,
                             'PointsList': [{'InflexionId': 255,
                                             'RoadId': 255,
                                             'Latitude': '39.987654',
                                             'Longitude': '136.123456',
                                             'RoadWidth': 55,
                                             'RoadAttribute': [2, 4],
                                             'MaxRoute': 100,
                                             'MinRoute': 10,
                                             'MaxSpeed': 50,
                                             'OverSpeedDuration': 3},
                                            {'InflexionId': 2,
                                             'RoadId': 2,
                                             'Latitude': '40.987654',
                                             'Longitude': '133.123456',
                                             'RoadWidth': 66,
                                             'RoadAttribute': [2, 4],
                                             'MaxRoute': 100,
                                             'MinRoute': 10,
                                             'MaxSpeed': 50,
                                             'OverSpeedDuration': 3}]}
        self.mq.send_message('RouteInfo', '123459876543', self.json_message)
        self.receive_and_assert_message(self.gen_RouteInfo())

    def test51(self):
        '''设置路线（路线属性2、4）'''
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             'RouteId': 255,
                             'RouteAttribute': [0, 2, 3, 4, 5],
                             'StartTime': '2016-07-06 00:00:00',
                             'EndTime': '2017-12-31 23:59:59',
                             'PointCount': 2,
                             'PointsList': [{'InflexionId': 255,
                                             'RoadId': 255,
                                             'Latitude': '39.987654',
                                             'Longitude': '136.123456',
                                             'RoadWidth': 55,
                                             'RoadAttribute': [2, 4],},
                                            {'InflexionId': 2,
                                             'RoadId': 2,
                                             'Latitude': '40.987654',
                                             'Longitude': '133.123456',
                                             'RoadWidth': 66,
                                             'RoadAttribute': [2, 4],}]}
        self.mq.send_message('RouteInfo', '123459876543', self.json_message)
        self.receive_and_assert_message(self.gen_RouteInfo())

    def test52(self):
        '''设置路线（路线属性0、1、3、5）'''
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             'RouteId': 255,
                             'RouteAttribute': [0, 2, 3, 4, 5],
                             'StartTime': '2016-07-06 00:00:00',
                             'EndTime': '2017-12-31 23:59:59',
                             'PointCount': 2,
                             'PointsList': [{'InflexionId': 255,
                                             'RoadId': 255,
                                             'Latitude': '39.987654',
                                             'Longitude': '136.123456',
                                             'RoadWidth': 55,
                                             'RoadAttribute': [0, 1, 3, 5],
                                             'MaxRoute': 100,
                                             'MinRoute': 10,
                                             'MaxSpeed': 50,
                                             'OverSpeedDuration': 3},
                                            {'InflexionId': 2,
                                             'RoadId': 2,
                                             'Latitude': '40.987654',
                                             'Longitude': '133.123456',
                                             'RoadWidth': 66,
                                             'RoadAttribute': [0, 1, 3, 5],
                                             'MaxRoute': 100,
                                             'MinRoute': 10,
                                             'MaxSpeed': 50,
                                             'OverSpeedDuration': 3}]}
        self.mq.send_message('RouteInfo', '123459876543', self.json_message)
        self.receive_and_assert_message(self.gen_RouteInfo())

    def test53(self):
        '''设置路线（各路段的路线属性不同）'''
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             'RouteId': 255,
                             'RouteAttribute': [0, 2, 3, 4, 5],
                             'StartTime': '2016-07-06 00:00:00',
                             'EndTime': '2017-12-31 23:59:59',
                             'PointCount': 2,
                             'PointsList': [{'InflexionId': 255,
                                             'RoadId': 255,
                                             'Latitude': '39.987654',
                                             'Longitude': '136.123456',
                                             'RoadWidth': 55,
                                             'RoadAttribute': [2, 4],
                                             'MaxRoute': 100,
                                             'MinRoute': 10,
                                             'MaxSpeed': 50,
                                             'OverSpeedDuration': 3},
                                            {'InflexionId': 2,
                                             'RoadId': 2,
                                             'Latitude': '40.987654',
                                             'Longitude': '133.123456',
                                             'RoadWidth': 66,
                                             'RoadAttribute': [0, 1, 3, 5],
                                             'MaxRoute': 101,
                                             'MinRoute': 12,
                                             'MaxSpeed': 53,
                                             'OverSpeedDuration': 4}]}
        self.mq.send_message('RouteInfo', '123459876543', self.json_message)
        self.receive_and_assert_message(self.gen_RouteInfo())

    @unittest.skip
    def test77(self):
        '''设置路线（经纬度为负数）'''
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             'RouteId': 255,
                             'RouteAttribute': [0, 2, 3, 4, 5],
                             'StartTime': '2016-07-06 00:00:00',
                             'EndTime': '2017-12-31 23:59:59',
                             'PointCount': 2,
                             'PointsList': [{'InflexionId': 255,
                                             'RoadId': 255,
                                             'Latitude': '39.987654',
                                             'Longitude': '136.123456',
                                             'RoadWidth': 55,
                                             'RoadAttribute': [2, 4],
                                             'MaxRoute': 100,
                                             'MinRoute': 10,
                                             'MaxSpeed': 50,
                                             'OverSpeedDuration': 3},
                                            {'InflexionId': 2,
                                             'RoadId': 2,
                                             'Latitude': '-40.987654',
                                             'Longitude': '-133.123456',
                                             'RoadWidth': 66,
                                             'RoadAttribute': [0, 1, 3, 5],
                                             'MaxRoute': 101,
                                             'MinRoute': 12,
                                             'MaxSpeed': 53,
                                             'OverSpeedDuration': 4}]}
        self.mq.send_message('RouteInfo', '123459876543', self.json_message)
        self.receive_and_assert_message(self.gen_RouteInfo())

    def test54(self):
        '''删除路线（路线数小于125）'''
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             'RouteCount': 3,
                             'RouteList': [1, 2, 3]
                             }
        self.mq.send_message('DelRouteRegion', '123459876543', self.json_message)
        self.receive_and_assert_message(self.gen_DelRouteRegion())

    def test56(self):
        '''删除路线（路线数为0）'''
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             'RouteCount': 0,
                             }
        self.mq.send_message('DelRouteRegion', '123459876543', self.json_message)
        self.receive_and_assert_message(self.gen_DelRouteRegion())

    def test57(self):
        '''终端通用答复（结果0）'''
        self.send_and_assert_GenenalResponse(65535, '8604', 0)

    def test58(self):
        '''终端通用答复（结果1）'''
        self.send_and_assert_GenenalResponse(255, '8605', 1)

    def test59(self):
        '''终端通用答复（结果2）'''
        self.send_and_assert_GenenalResponse(random.randint(0, 65535), '8606', 2)

    def test60(self):
        '''终端通用答复（结果3）'''
        self.send_and_assert_GenenalResponse(random.randint(0, 65535), '8607', 3)

    def test61(self):
        '''终端通用答复（结果范围外）'''
        self.send_and_assert_GenenalResponse(random.randint(0, 65535), '8607', 253)

    def test62(self):
        '''查询全部终端参数'''
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             }
        self.mq.send_message('QueryAllParam', '123459876543', self.json_message)
        self.receive_and_assert_message(self.gen_QueryAllParam())

    def test63(self):
        '''查询指定终端参数（单个参数）'''
        param_ids = [0x01, 0x13, 0x20, 0x29, 0x2c, 0x50, 0x55, 0x56, 0x5b, 0x84]
        for param_id in param_ids:
            self.json_message = {'UID': '123459876543',
                                 'SerialNo': 65535,
                                 'ParamCount': 1,
                                 'ParamList': [param_id]
                                 }
            self.mq.send_message('QueryPartParam', '123459876543', self.json_message)
            self.receive_and_assert_message(self.gen_QueryPartParam())

    def test64(self):
        '''查询指定终端参数（多个参数）'''
        param_ids = [0x01, 0x13, 0x20, 0x29, 0x2c, 0x50, 0x55, 0x56, 0x5b, 0x84]
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             'ParamCount': len(param_ids),
                             'ParamList': param_ids
                             }
        self.mq.send_message('QueryPartParam', '123459876543', self.json_message)
        self.receive_and_assert_message(self.gen_QueryPartParam())

    def test65_66_67_68(self):
        '''设置终端参数（单个参数）'''
        params = [[0x01, 4, '100'],
                  [0x13, 3, '172.16.50.98'],
                  [0x20, 4, '2'],
                  [0x29, 4, '200'],
                  [0x2c, 4, '500'],
                  [0x50, 4, '1626867846'],
                  [0x55, 4, '80'],
                  [0x56, 4, '3'],
                  [0x5b, 2, '90'],
                  [0x84, 1, '1']]
        for param in params:
            # with self.subTest('test %s' % param):
            self.json_message = {'UID': '123459876543',
                                 'SerialNo': 65535,
                                 'ParamCount': 1,
                                 'ParamList': [{'ParaId': param[0],
                                                'ParaLen': param[1],
                                                'ParaValue': param[2]}]
                                 }
            self.mq.send_message('SetTermParam', '123459876543', self.json_message)
            self.receive_and_assert_message(self.gen_SetTermParam())

    def test69(self):
        '''设置终端参数（多个参数）'''
        params = [[0x01, 4, '100'],
                  [0x13, 3, '172.16.50.98'],
                  [0x20, 4, '2'],
                  [0x29, 4, '200'],
                  [0x2c, 4, '500'],
                  [0x50, 4, '1626867846'],
                  [0x55, 4, '80'],
                  [0x56, 4, '3'],
                  [0x5b, 2, '90'],
                  [0x84, 1, '1']]
        param_list = []
        for param in params:
            param_list.append({'ParaId': param[0],
                               'ParaLen': param[1],
                               'ParaValue': param[2]})
        self.json_message = {'UID': '123459876543',
                             'SerialNo': 65535,
                             'ParamCount': len(param_list),
                             'ParamList': param_list
                             }
        self.mq.send_message('SetTermParam', '123459876543', self.json_message)
        self.receive_and_assert_message(self.gen_SetTermParam())

    def test70_71_72_73(self):
        '''查询终端参数应答（单个参数）'''
        params = [  # [0x01, 4, 100],
            [0x13, 3, '172.16.50.98'],
            [0x20, 4, 2],
            [0x29, 4, 200],
            [0x2c, 4, 500],
            [0x50, 4, 1626867846],
            [0x55, 4, 80],
            [0x56, 4, 3],
            [0x5b, 2, 9],
            [0x84, 1, 1]]
        for param in params:
            # with self.subTest('test %s' % param):
            self.send_and_assert_qpr(65535, [param])

    def test74(self):
        '''查询终端参数应答（多个参数）'''
        params = [[0x01, 4, 100],
                  [0x13, 3, '172.16.50.98'],
                  [0x20, 4, 2],
                  [0x29, 4, 200],
                  [0x2c, 4, 500],
                  [0x50, 4, 1626867846],
                  [0x55, 4, 80],
                  [0x56, 4, 3],
                  [0x5b, 2, 9],
                  [0x84, 1, 1]]
        self.send_and_assert_qpr(65535, params)

    def test75(self):
        '''查询终端参数应答（全部参数）（未验证）'''
        messages = [
            '7e01040369018812345678026fffff71000000010400000064000000020400000000000000030400000000000000040400000000000000050400000000000000060400000000000000070400000000000000100000000011000000001200000000130b3137322e31362e392e3234000000140000000015000000001600000000170000000018040000269400000019040000184e0000001a000000001b04000000000000001c04000000000000001d0000000020040000000100000021040000000000000022040000001e00000027040000012c00000028040000000a00000029040000001e0000002c04000001f40000002d04000001f40000002e04000007d00000002f04000000c80000003004000000280000003102006400000040000000004100000000420000000043000000004400000000450400000002000000460400000078000000470400000e1000000048000000004900000000500460f8088600000051040000000000000052040000000000000053040000000000000054040000000000000055040000006400000056040000000a00000057040000384000000058040000e1000000005904000004b00000005a0400008ca00000005b0200640000005c0207080000005d020a040000005e02001e0000006404000a000000000065040000000000000070040000000300000071040000002300000072040000001900000073040000001f00000074040000001f0000008004000000000000008102869f0000008202869f0000008306424a303030310000008401010000009001010000009101010000009201010000009304000000010000009401000000009504000000050000010004000000000000010204000000000000010102000000000103020000000001100800000000000000000000011108000000000000000000000112080000000000000000000001130800000000000000000000f0c904000000000000f0ca04000000000000f0ae000000f0af000000f0b001000000f0b101000000f0b201000000f0b301000000f0b401000000f0b501000000f0b601000000f0b701000000f0b801000000f0b901000000f0ba01000000f0bb0200000000f0bc0200000000f0bd0200000000f0be0200000000f0bf01000000f0c00200000000f0c10200000000f0c201000000f0c30200000000f0c401000000f0c50200000000f0c601000000f0c701000000f0c80100e37e',
            # 正常
            '7e010402af0188123456781573ffff54000000010400000064000000020400000000000000030400000000000000040400000000000000050400000000000000060400000000000000070400000000000000100000000011000000001200000000130b3137322e31362e392e3234000000140000000015000000001600000000170000000018040000269400000019040000184e0000001a000000001b04000000000000001c04000000000000001d0000000020040000000100000021040000000000000022040000001e00000027040000012c00000028040000000a00000029040000001e0000002c04000001f40000002d04000001f40000002e04000007d00000002f04000000c80000003004000000280000003102006400000040000000004100000000420000000043000000004400000000450400000002000000460400000078000000470400000e1000000048000000004900000000500460f8088600000051040000000000000052040000000000000053040000000000000054040000000000000055040000006400000056040000000a00000057040000384000000058040000e1000000005904000004b00000005a0400008ca00000005b0200640000005c0207080000005d020a040000005e02001e0000006404000a000000000065040000000000000070040000000300000071040000002300000072040000001900000073040000001f00000074040000001f0000008004000000000000008102869f0000008202869f0000008306424a30303031000000840101000000900101000000910101000000920101000000930400000001000000940100000000950400000005000001000400000000000001020400000000000001010200000000010302000000000110080000000000000000000001110800000000000000000000011208000000000000000000000113080000000000000000317e',
            # 转义
            '7e010402b0018812345678150cffff54000000010400000064000000020400000000000000030400000000000000040400000000000000050400000000000000060400000000000000070400000000000000100000000011000000001200000000130b3137322e31362e392e3234000000140000000015000000001600000000170000000018040000269400000019040000184e0000001a000000001b04000000000000001c04000000000000001d0000000020040000000100000021040000000000000022040000001e00000027040000012c00000028040000000a00000029040000001e0000002c04000001f40000002d04000001f40000002e04000007d00000002f04000000c80000003004000000280000003102006400000040000000004100000000420000000043000000004400000000450400000002000000460400000078000000470400000e1000000048000000004900000000500460f8088600000051040000000000000052040000000000000053040000000000000054040000000000000055040000006400000056040000000a00000057040000384000000058040000e1000000005904000004b00000005a0400008ca00000005b0200640000005c0207080000005d020a040000005e02001e0000006404000a000000000065040000000000000070040000000300000071040000002300000072040000001900000073040000001f00000074040000001f0000008004000000000000008102869f0000008202869f0000008307424a303030317d020000008401010000009001010000009101010000009201010000009304000000010000009401000000009504000000050000010004000000000000010204000000000000010102000000000103020000000001100800000000000000000000011108000000000000000000000112080000000000000000000001130800000000000000002e7e',
            # 中文
            '7e010402b00188123456781578ffff54000000010400000064000000020400000000000000030400000000000000040400000000000000050400000000000000060400000000000000070400000000000000100000000011000000001200000000130b3137322e31362e392e3234000000140000000015000000001600000000170000000018040000269400000019040000184e0000001a000000001b04000000000000001c04000000000000001d0000000020040000000100000021040000000000000022040000001e00000027040000012c00000028040000000a00000029040000001e0000002c04000001f40000002d04000001f40000002e04000007d00000002f04000000c80000003004000000280000003102006400000040000000004100000000420000000043000000004400000000450400000002000000460400000078000000470400000e1000000048000000004900000000500460f8088600000051040000000000000052040000000000000053040000000000000054040000000000000055040000006400000056040000000a00000057040000384000000058040000e1000000005904000004b00000005a0400008ca00000005b0200640000005c0207080000005d020a040000005e02001e0000006404000a000000000065040000000000000070040000000300000071040000002300000072040000001900000073040000001f00000074040000001f0000008004000000000000008102869f0000008202869f0000008307bea94a30303031000000840101000000900101000000910101000000920101000000930400000001000000940100000000950400000005000001000400000000000001020400000000000001010200000000010302000000000110080000000000000000000001110800000000000000000000011208000000000000000000000113080000000000000000717e'
        ]
        log_name = 'test75_%s.log' % time.strftime('%Y%m%d-%H%M%S')
        for message in messages:
            self.mdvr.send(binascii.a2b_hex(message))
            time.sleep(TINY_DELAY)
            body = self.mq.get_sp_message('QueryParaResponse')
            self.assertIsNotNone(body)
            self.assertEqual(self.mdvr.authentication_code, body['UID'])
            self.assertEqual(int(message[22:26], 16), body['SerialNo'])
            self.assertEqual(int(message[26:30], 16), body['ResponseSerialNo'])
            self.assertEqual(int(message[30:32], 16), body['ParamCount'])
            self.assertIsInstance(body['ParamList'], list)
            with open(log_name, 'a', encoding='utf-8') as f:
                print(time.ctime(), ':', file=f)
                for param in body['ParamList']:
                    print(param, file=f)
        self.fail('请手动检查{}以确定结果是否正确'.format(log_name))

    def test76(self):
        '''透传指令（没有消息体）'''
        # words = '0123456789abcdef'
        messageid = 0x8104
        messagebody = ''
        self.json_message = {'MessageID': messageid,
                             'SIM': '18812345678',
                             'MessageBody': messagebody
                             }
        self.mq.send_message('Test808', '123459876543', self.json_message)
        self.get_and_assert_Test808(messageid, messagebody)

    def test79(self):
        '''透传指令（随机消息体）'''
        words = '0123456789abcdef'
        for i in range(10):
            # with self.subTest(i=i):
            messageid = random.randint(0x8000, 0x9000)
            messagebody = ''.join([random.choice(words) for i in range(random.randint(0, 100) * 2)])
            self.json_message = {'MessageID': messageid,
                                 'SIM': '18812345678',
                                 'MessageBody': messagebody
                                 }
            self.mq.send_message('Test808', '123459876543', self.json_message)
            self.get_and_assert_Test808(messageid, messagebody)

    def test80(self):
        '''透传指令（消息体需转义）'''
        messageid = random.randint(0x8000, 0x9000)
        messagebody = '7e7d'
        self.json_message = {'MessageID': messageid,
                             'SIM': '18812345678',
                             'MessageBody': messagebody
                             }

        self.mq.send_message('Test808', '123459876543', self.json_message)

        message = self.mdvr.receive_message(LONGER_DELAY)
        self.assertIsNotNone(message, '未收到应答')
        self.assertTrue(mdvr.message_start_end_right(message))
        self.assertTrue(mdvr.check_checksum(mdvr.recover_escape(message[1: -1])), '校验码不正确')
        message_head_body = mdvr.recover_escape(message[1: -1])[:-1]
        message_head = message_head_body[: 12]
        message_body = message[13: -2]
        self.assertEqual(mdvr.int_to_word(messageid), message_head[:2])
        mb = mdvr.Message.make_message_escaped(binascii.a2b_hex(messagebody))
        self.assertEqual(mb, message_body,
                         '\n  expect is: %s\nactually is: %s' %
                         (mdvr.printfuled(mb), mdvr.printfuled(message_body)))

    def tearDown(self):
        try:
            self.mq.close()
            self.mdvr.close()
        except:
            pass

    def get_and_assert_Test808(self, messageid, messagebody):
        message = self.mdvr.receive_message(LONGER_DELAY)
        self.assertIsNotNone(message, '未收到应答')
        self.assertTrue(mdvr.message_start_end_right(message))
        self.assertTrue(mdvr.check_checksum(mdvr.recover_escape(message[1: -1])), '校验码不正确')
        message_head_body = mdvr.recover_escape(message[1: -1])[:-1]
        message_head = message_head_body[: 12]
        message_body = message_head_body[12:]
        self.assertEqual(mdvr.int_to_word(messageid), message_head[:2])
        self.assertEqual(binascii.a2b_hex(messagebody), message_body,
                         '\n  expect is: %s\nactually is: %s' % (messagebody, mdvr.printfuled(message_body)))

    def send_and_assert_GenenalResponse(self, rsn, messageid, result):
        if isinstance(messageid, str):
            message_id = binascii.a2b_hex(messageid)
        else:
            message_id = messageid
        messagebody = mdvr.int_to_word(rsn) + message_id + mdvr.int_to_byte(result)
        self.mdvr.send_message(b'\x00\x01', messagebody, add_to_waiting_response=False)
        time.sleep(TINY_DELAY)
        body = self.mq.get_sp_message('GenenalResponse')
        self.assertIsNotNone(body)
        self.assertEqual(self.mdvr.authentication_code, body['UID'])
        self.assertEqual(self.mdvr.next_message_num - 1, body['SerialNo'])
        self.assertEqual(rsn, body['ResponseSerialNo'])
        self.assertEqual((message_id[0] << 8) + message_id[1], body['MessageID'])
        self.assertEqual(result, body['Result'])

    def send_and_assert_qpr(self, rsn, params):
        int_to_which = {1: mdvr.int_to_byte,
                        2: mdvr.int_to_word,
                        4: mdvr.int_to_dword}
        param_list = b''
        for each_para in params:
            param_list += mdvr.int_to_dword(each_para[0])
            if each_para[1] == 3:
                paravalue = mdvr.str_to_string(each_para[2])
                param_list += (mdvr.int_to_byte(len(paravalue)) + paravalue)
            else:
                param_list += mdvr.int_to_byte(each_para[1])
                param_list += int_to_which[each_para[1]](int(each_para[2]))
        messagebody = mdvr.int_to_word(rsn) + mdvr.int_to_byte(len(params)) + param_list
        self.mdvr.send_message(b'\x01\x04', messagebody, add_to_waiting_response=False)
        time.sleep(TINY_DELAY)
        body = self.mq.get_sp_message('QueryParaResponse')
        self.assertIsNotNone(body)
        self.assertEqual(self.mdvr.authentication_code, body['UID'])
        self.assertEqual(self.mdvr.next_message_num - 1, body['SerialNo'])
        self.assertEqual(rsn, body['ResponseSerialNo'])
        self.assertEqual(len(params), body['ParamCount'])
        self.assertIsInstance(body['ParamList'], list)
        p = list(params)
        for each_p in body['ParamList']:
            para_id = int(each_p['ParaId'])
            para_len = int(each_p['ParaLen'])
            if para_len == 3:
                para_value = each_p['ParaValue']
            else:
                para_value = int(each_p['ParaValue'])
            self.assertIn([para_id, para_len, para_value], p)
            p.remove([para_id, para_len, para_value])
        self.assertListEqual([], p)

    def receive_and_assert_message(self, expect):
        expect = expect
        actual = self.mdvr.receive_message(LONGER_DELAY)
        self.assertIsNotNone(actual)
        self.assertEqual(expect, actual,
                         '\n  expect is: %s\nactually is: %s' % (mdvr.printfuled(expect), mdvr.printfuled(actual)))

    def gen_PolygonsRegion(self, phone=None):
        if not phone:
            phone = self.mdvr.phoneNum
        else:
            phone = phone
        region_property = 0
        region_property_map = {0: 1, 1: 1 << 1, 2: 1 << 2, 3: 1 << 3, 4: 1 << 4, 6: 0, 8: 0, 5: 1 << 5, 7: 1 << 6,
                               9: 1 << 7}
        for i in self.json_message['RegionProperty']:
            region_property |= region_property_map[i]
        start_time = b''
        end_time = b''
        if 0 in self.json_message['RegionProperty']:
            start_time = time_str_to_bcd(self.json_message['StartTime'])
            end_time = time_str_to_bcd(self.json_message['EndTime'])
        max_speed = b''
        over_speed_duration = b''
        if 1 in self.json_message['RegionProperty']:
            max_speed = mdvr.int_to_word(self.json_message['MaxSpeed'])
            over_speed_duration = mdvr.int_to_byte(self.json_message['OverSpeedDuration'])
        points = b''
        for eachpoint in self.json_message['PointsList']:
            points += mdvr.int_to_dword(int(abs(decimal.Decimal(str(eachpoint['Latitude']))) * 1000000))
            points += mdvr.int_to_dword(int(abs(decimal.Decimal(str(eachpoint['Longitude']))) * 1000000))
        messagebody = mdvr.int_to_dword(self.json_message['RegionID']) + mdvr.int_to_word(
            region_property) + start_time + end_time + max_speed + over_speed_duration + mdvr.int_to_word(
            self.json_message['PointCount']) + points
        message = mdvr.Message(b'\x86\x04', phone, messagebody, self.json_message['SerialNo'])
        return bytes(message)

    def gen_DelPolygonsRegion(self):
        regins = b''
        if self.json_message['RegionCount']:
            for i in self.json_message['RegionList']:
                regins += mdvr.int_to_dword(i)
        messagebody = mdvr.int_to_byte(self.json_message['RegionCount']) + regins
        message = mdvr.Message(b'\x86\x05', self.mdvr.phoneNum, messagebody, self.json_message['SerialNo'])
        return bytes(message)

    def gen_RouteInfo(self):
        route_attribute = 0
        route_attribute_map = {0: 1, 2: 1 << 2, 3: 1 << 3, 4: 1 << 4, 5: 1 << 5}
        for i in self.json_message['RouteAttribute']:
            route_attribute |= route_attribute_map[i]
        start_time = b''
        end_time = b''
        if 0 in self.json_message['RouteAttribute']:
            start_time = time_str_to_bcd(self.json_message['StartTime'])
            end_time = time_str_to_bcd(self.json_message['EndTime'])
        turning_points = b''
        road_attribute_map = {0: 1, 1: 1 << 1, 2: 0, 3: 1 << 2, 4: 0, 5: 1 << 3}
        for eachpoint in self.json_message['PointsList']:
            road_attribute = 0
            for i in eachpoint['RoadAttribute']:
                road_attribute |= road_attribute_map[i]
            max_route = b''
            min_route = b''
            if 0 in eachpoint['RoadAttribute']:
                max_route = mdvr.int_to_word(eachpoint['MaxRoute'])
                min_route = mdvr.int_to_word(eachpoint['MinRoute'])
            max_speed = b''
            over_speed_duration = b''
            if 1 in eachpoint['RoadAttribute']:
                max_speed = mdvr.int_to_word(eachpoint['MaxSpeed'])
                over_speed_duration = mdvr.int_to_byte(eachpoint['OverSpeedDuration'])
            turning_points += (mdvr.int_to_dword(eachpoint['InflexionId']) +
                               mdvr.int_to_dword(eachpoint['RoadId']) +
                               mdvr.int_to_dword(int(abs(decimal.Decimal(str(eachpoint['Latitude']))) * 1000000)) +
                               mdvr.int_to_dword(int(abs(decimal.Decimal(str(eachpoint['Longitude']))) * 1000000)) +
                               mdvr.int_to_byte(eachpoint['RoadWidth']) +
                               mdvr.int_to_byte(road_attribute) +
                               max_route + min_route + max_speed + over_speed_duration)
        messagebody = mdvr.int_to_dword(self.json_message['RouteId']) + \
                      mdvr.int_to_word(route_attribute) + \
                      start_time + end_time + \
                      mdvr.int_to_word(self.json_message['PointCount']) + \
                      turning_points
        message = mdvr.Message(b'\x86\x06', self.mdvr.phoneNum, messagebody, self.json_message['SerialNo'])
        return bytes(message)

    def gen_DelRouteRegion(self):
        routes = b''
        if self.json_message['RouteCount']:
            for i in self.json_message['RouteList']:
                routes += mdvr.int_to_dword(i)
        messagebody = mdvr.int_to_byte(self.json_message['RouteCount']) + routes
        message = mdvr.Message(b'\x86\x07', self.mdvr.phoneNum, messagebody, self.json_message['SerialNo'])
        return bytes(message)

    def gen_QueryAllParam(self):
        message = mdvr.Message(b'\x81\x04', self.mdvr.phoneNum, b'', self.json_message['SerialNo'])
        return bytes(message)

    def gen_QueryPartParam(self):
        para_list = b''
        for paraid in self.json_message['ParamList']:
            para_list += mdvr.int_to_dword(paraid)
        messagebody = mdvr.int_to_byte(self.json_message['ParamCount']) + para_list
        message = mdvr.Message(b'\x81\x06', self.mdvr.phoneNum, messagebody, self.json_message['SerialNo'])
        return bytes(message)

    def gen_SetTermParam(self):
        int_to_which = {1: mdvr.int_to_byte,
                        2: mdvr.int_to_word,
                        4: mdvr.int_to_dword}
        para_list = b''
        for each_para in self.json_message['ParamList']:
            para_list += mdvr.int_to_dword(each_para['ParaId'])
            if each_para['ParaLen'] == 3:
                paravalue = mdvr.str_to_string(each_para['ParaValue'])
                para_list += (mdvr.int_to_byte(len(paravalue)) + paravalue)
            else:
                para_list += mdvr.int_to_byte(each_para['ParaLen'])
                para_list += int_to_which[each_para['ParaLen']](int(each_para['ParaValue']))
        messagebody = mdvr.int_to_byte(self.json_message['ParamCount']) + para_list
        message = mdvr.Message(b'\x81\x03', self.mdvr.phoneNum, messagebody, self.json_message['SerialNo'])
        return bytes(message)


if __name__ == '__main__':
    unittest.main()
