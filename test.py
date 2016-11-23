#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'shangxc'
from socket import socket, AF_INET, SOCK_STREAM, error, SHUT_RDWR
import timeit
import json
from mdvr import *
import binascii
import random

JSN = r'{"UID":"0123456789A","SerialNo":34,"RegisterNo":"0123456789A","SIM":"13552174502","IsPassed":0}'


def chufa():
    value = 65535
    return bytes((value // 256,)) + bytes((value % 256,))


def weiyi():
    value = 65535
    return bytes((value >> 8,)) + bytes((value & 255,))


import threading, sys, time


def th(i):
    print(i)
    time.sleep(7)


def main():
    a = 1
    b = 2
    sss = a + b
    time.sleep(1)
    print(sss)


def gen_mes(messageid, messagebody, phone=18812345678):
    if isinstance(messageid, str):
        messageid = binascii.a2b_hex(messageid)
    if isinstance(messagebody, str):
        messagebody = binascii.a2b_hex(messagebody)
    return str(Message(messageid,
                       phone,
                       messagebody,
                       # random.randint(0, 65535),
                       65535))


if __name__ == '__main__':
    # a = json.loads(JSN)
    # b = json.dumps(a)
    # print(b, type(b))
    # for i in range(100):
    #     threading.Thread(target=lambda: th(i)).start()
    # time.sleep(0.01)
    # import cProfile
    # cProfile.run('main()')
    print(gen_mes('8103', '01000000010400000001'))
    print(gen_mes('8103', '01000000010400000064'))
    print(gen_mes('8103', '01000000130c3137322e31362e35302e3938'))
    print(gen_mes('8103', '01000000130b3137322e31362e392e3234'))
    print(gen_mes('8103', '01000000200400000000'))
    print(gen_mes('8103', '01000000200400000001'))
    print(gen_mes('8103', '01000000200400000002'))
    print(gen_mes('8103', '01000000290400000001'))
    print(gen_mes('8103', '01000000290400000064'))
    print(gen_mes('8103', '010000002c0400000001'))
    print(gen_mes('8103', '010000002c0400000064'))
    print(gen_mes('8103', '010000005004ffffffff'))
    print(gen_mes('8103', '01000000500400000000'))
    print(gen_mes('8103', '01000000500460f80886'))
    print(gen_mes('8103', '01000000550400000001'))
    print(gen_mes('8103', '01000000550400000064'))
    print(gen_mes('8103', '01000000560400000001'))
    print(gen_mes('8103', '01000000560400000064'))
    print(gen_mes('8103', '010000005b020001'))
    print(gen_mes('8103', '010000005b020064'))
    print(gen_mes('8103', '02000000010400000001000000200400000001'))
    print(gen_mes('8106', '020000000100000020'))
    print(gen_mes('8105', '03'))
    print(gen_mes('8105', '04'))
    print(gen_mes('8105', '05'))
    print(gen_mes('8105', '06'))
    print(gen_mes('8105', '07'))
    print(gen_mes('8107', ''))
    print(gen_mes('8201', ''))
    a = {'UID': '123459876543', 'SerialNo': 0, 'ResultType': 0, 'RegisterNo': '123459876543', 'SIM': '18812345678'}
    print(json.dumps(a).replace('"', '\\"'))
    print(gen_mes('8604',
                  int_to_dword(888) + b'\x00\x04' + int_to_word(3) + int_to_dword(78100000) + int_to_dword(136100000)
                  + int_to_dword(78200000) + int_to_dword(136200000) + int_to_dword(78500000) + int_to_dword(
                      136000000)))
    print(gen_mes('8604',
                  int_to_dword(888) + b'\x00\x04' + int_to_word(3) + int_to_dword(78101000) + int_to_dword(136101000)
                  + int_to_dword(78201000) + int_to_dword(136200100) + int_to_dword(78501000) + int_to_dword(
                      136000100)))
    print(gen_mes('8605', int_to_byte(0)))
    print(gen_mes('8605', int_to_byte(1) + int_to_dword(888)))
    print(gen_mes('8202', int_to_word(1) + int_to_dword(10)))
    print(gen_mes('8202', int_to_word(10) + int_to_dword(100)))
    print(gen_mes('8202', int_to_word(0)))
    print(gen_mes('8300', int_to_byte(bitlist_to_int([1, 0, 1, 1, 1, 0, 0, 0])) + str_to_string('AAA1111')))
    print(gen_mes('8300', int_to_byte(bitlist_to_int([0, 0, 1, 1, 1, 0, 0, 0])) + str_to_string('啊啊啊')))
    print(gen_mes('8301', int_to_byte(2) + int_to_byte(1) + int_to_byte(22) + int_to_byte(3) + str_to_string('222')))
    print(gen_mes('8600', int_to_byte(1) + int_to_byte(1) + int_to_dword(1) + b'\x00\x08' +
                  int_to_dword(78100000) + int_to_dword(36100000) + int_to_dword(10000)))
    print(gen_mes('8600', int_to_byte(1) + int_to_byte(1) + int_to_dword(1) + b'\x00\x08' +
                  int_to_dword(78101000) + int_to_dword(36110000) + int_to_dword(10000)))
    print(gen_mes('8601', '00'))
    print(gen_mes('8601', int_to_byte(1) + int_to_dword(1)))
    print(gen_mes('8602', int_to_byte(1) + int_to_byte(1) + int_to_dword(1684) + b'\x00\x08' +
                  int_to_dword(39926035) + int_to_dword(136822854) + int_to_dword(39839886) + int_to_dword(136986653)))
    print(gen_mes('8603', '00'))
    print(gen_mes('8603', int_to_byte(1) + int_to_dword(1684)))
    print(gen_mes(b'\x86\x06', int_to_dword(1998) + int_to_word(8) + int_to_word(2) +
                  int_to_dword(1) + int_to_dword(2) + int_to_dword(78000000) + int_to_dword(136000000) + int_to_byte(
        10) +
                  int_to_byte(0) +
                  int_to_dword(3) + int_to_dword(4) + int_to_dword(76000000) + int_to_dword(138000000) + int_to_byte(
        10) +
                  int_to_byte(0)))
    print(gen_mes(b'\x86\x06', int_to_dword(1998) + int_to_word(8) + int_to_word(2) +
                  int_to_dword(1) + int_to_dword(2) + int_to_dword(78001000) + int_to_dword(136001000) + int_to_byte(
        10) +
                  int_to_byte(0) +
                  int_to_dword(3) + int_to_dword(4) + int_to_dword(76001000) + int_to_dword(138001000) + int_to_byte(
        10) +
                  int_to_byte(0)))
    print(gen_mes('8607', '00'))
    print(gen_mes('8607', int_to_byte(1) + int_to_dword(1998)))
    print(gen_mes('8801', int_to_byte(1) + int_to_word(1) + int_to_word(0) + int_to_byte(0) + b'\x03' + int_to_byte(1) +
                  int_to_byte(127) + int_to_byte(127) + int_to_byte(127) + int_to_byte(127)))
    print(gen_mes('8801', int_to_byte(1) + b'\xff\xff' + int_to_word(3) + int_to_byte(0) + b'\x08' + int_to_byte(1) +
                  int_to_byte(127) + int_to_byte(127) + int_to_byte(127) + int_to_byte(127)))
    print(gen_mes('8802', int_to_byte(0) + int_to_byte(1) + int_to_byte(
        0) + b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'))
    print(gen_mes('8802', int_to_byte(1) + int_to_byte(1) + int_to_byte(
        0) + b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'))
    print(gen_mes('8802', int_to_byte(2) + int_to_byte(0) + int_to_byte(
        0) + b'\x16\x06\x22\x00\x00\x00\x16\x06\x22\x23\x59\x59'))
    # f = open('dataau.txt', 'rb')
    # t = open('2.mp4', 'wb')
    # tmp = []
    # for eachline in f:
    #     for i in range(0, len(eachline[:-4]),2):
    #         t.write(binascii.a2b_hex(eachline[i:i+2]))
    j = {'MessageID': 33027, 'SIM': '18812345678', 'MessageBody': '01000000010400000064'}
    print(json.dumps(j))
    print(gen_mes('8106', '0100000001'))
    print(gen_mes('8106', '0100000013'))
    print(gen_mes('8106', '0100000020'))
    print(gen_mes('8106', '0100000029'))
    print(gen_mes('8106', '010000002c'))
    print(gen_mes('8106', '0100000050'))
    print(gen_mes('8106', '0100000055'))
    print(gen_mes('8106', '0100000056'))
    print(gen_mes('8106', '010000005b'))
    print(gen_mes('8103', '010000005004cfefde1c'))
    print(gen_mes('8103', '010000005b020005'))
    print(gen_mes('8103', '02000000010400000065000000200400000001'))
    print(gen_mes('8104', ''))
    print(gen_mes('8804', '0100050000', 18812345678))
    print(gen_mes('8804', '0100050003', 18812345678))
    print(gen_mes('8202', int_to_word(1) + int_to_dword(100)))
    import collections

    k = {'StreamType': 1,
         'FileType': 0,
         'Channel': [0, 1, 2, 3],
         'StartTime': '2016-08-09 00:00:00',
         'EndTime': '2016-08-09 23:59:59',
         'UID': '123456789012'}
    kk = collections.OrderedDict(StreamName='99999AA12311-LOAD-0',
                                 RecordId='0-194-0',
                                 OffSetFlag=0,
                                 StartTime='',
                                 EndTime='',
                                 OffSet=0,
                                 UID='99999AA12311', )
    print(json.dumps(kk))

    param_list = [{'ParaId': 0x20,
                   'ParaLen': 4,
                   'ParaValue': 0},
                  {'ParaId': 0x29,
                   'ParaLen': 4,
                   'ParaValue': 30}
                  ]
    v = {'UID': '999990LYJ021',
         'SerialNo': 65535,
         'ParamCount': len(param_list),
         'ParamList': param_list
         }
    print(v)
    v = json.dumps(v)
    print(v)
    c = {"MessageID": 34817,
         "SIM": "13552178888",
         "MessageBody": "01000a0000008017f7f7f7f"
         }
    print(gen_mes('8300', int_to_byte(bitlist_to_int([1, 0, 1, 1, 0, 0, 0, 0])) + str_to_string('你好，这是个测试'), phone=13552178888))
