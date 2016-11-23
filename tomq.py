#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'shangxc'
import mqclient

def send_PolygonsRegion():
    mq = mqclient.MqClient('172.16.10.191')
    mq.send_message('PolygonsRegion', '123459876543', {'UID': ['123459876543'],
                                                    'SerialNo': 55,
                                                    'RegionID': 12,
                                                    'RegionProperty': [1, 3, 5, 6, 8],
                                                    'MaxSpeed': 50,
                                                    'OverSpeedDuration': 3,
                                                    'PointCount': 3,
                                                    'PointsList': [{'Longitude': 136.1234, 'Latitude': 49.9876},
                                                                   {'Longitude': 136.1235, 'Latitude': 49.9876},
                                                                   {'Longitude': 136.1234, 'Latitude': 49.9875},]})
    mq.close()

def send_DelPolygonsRegion(RegionList):
    mq = mqclient.MqClient('172.16.10.191')
    rl = list(RegionList)
    mq.send_message('DelPolygonsRegion', '123459876543', {'UID': '123459876543',
                                                       'SerialNo': 65534,
                                                       'RegionCount': len(rl),
                                                       # 'RegionList': rl
                                                       })
    mq.close()

def send_RouteInfo():
    mq = mqclient.MqClient('172.16.10.191')
    mq.send_message('RouteInfo', '123459876543', {'UID': ['123459876543'],
                                                  'SerialNo': 65534,
                                                  'RouteId': 12,
                                                  'RouteAttribute': [],
                                                  'PointCount': 2,
                                                  'PointsList': [{'InflexionId': 1,
                                                                  'RoadId': 1,
                                                                  'Latitude': 136.123456,
                                                                  'Longitude': 39.987654,
                                                                  'RoadWidth': 55,
                                                                  'RoadAttribute': [2, 4],
                                                                  'MaxRoute': 100,
                                                                  'MinRoute': 10,
                                                                  'MaxSpeed': 50,
                                                                  'OverSpeedDuration': 3},
                                                                 {'InflexionId': 2,
                                                                  'RoadId': 2,
                                                                  'Latitude': 133.123456,
                                                                  'Longitude': 40.987654,
                                                                  'RoadWidth': 66,
                                                                  'RoadAttribute': [2, 4],
                                                                  'MaxRoute': 100,
                                                                  'MinRoute': 10,
                                                                  'MaxSpeed': 50,
                                                                  'OverSpeedDuration': 3}]})
    mq.close()

def send_DelRouteRegion(RouteList):
    mq = mqclient.MqClient('172.16.10.191')
    rl = list(RouteList)
    mq.send_message('DelRouteRegion', '123459876543', {'UID': '123459876543',
                                                       'SerialNo': 65534,
                                                       'RouteCount': len(rl),
                                                       'RouteList': rl
                                                       })
    mq.close()

def send_QueryAllParam():
    mq = mqclient.MqClient('172.16.10.191')
    mq.send_message('QueryAllParam', '123459876543', {'UID': '123459876543',
                                                       'SerialNo': 65534,
                                                       })
    mq.close()

def send_QueryPartParam(ParamList):
    pl = list(ParamList)
    mq = mqclient.MqClient('172.16.10.191')
    mq.send_message('QueryPartParam', '123459876543', {'UID': '123459876543',
                                                       'SerialNo': 65534,
                                                    'ParamCount': len(pl),
                                                    'ParamList': pl
                                                       })
    mq.close()

def send_SetTermParam(ParamList):
    pl = list(ParamList)
    mq = mqclient.MqClient('172.16.10.191')
    mq.send_message('SetTermParam', '123459876543', {'UID': '123459876543',
                                                       'SerialNo': 65534,
                                                    'ParamCount': len(pl),
                                                    'ParamList': pl
                                                       })
    mq.close()

def send_Test808(MessageID, MessageBody):
    md = int(MessageID, 16)
    mq = mqclient.MqClient('172.16.10.191')
    mq.send_message('Test808', '123459876543', {'MessageID': md,
                                                       'SIM': '018812345678',
                                                    'MessageBody': MessageBody
                                                       })
    mq.close()

if __name__ == '__main__':
    # send_QueryPartParam([0x1, 0x13, 0x20, 0x29, 0x2c, 0x50, 0x55, 0x56, 0x5b])
    # send_SetTermParam([{'ParaId': 0x1, 'ParaLen': 4, 'ParaValue': '100'}])
    # send_Test808('8104', '')
    send_PolygonsRegion()
    
