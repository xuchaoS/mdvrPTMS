#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'shangxc'
import mdvr
import mqclient
import time
import random
import binascii
import threading
import logging
import sys

logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s',
                    filename='baseMultiMDVR.log', filemode='w')


def mdvr_by_thread(num):
    m = mdvr.MDVR(19912300000 + num, manufacturer_id='ltest', terminal_id='lt%05d' % num, plate='t%05d' % num,
                  authentication_code='ltestlt%05d' % num, ip='172.16.50.98')

    m.connect()
    m.send_terminal_authentication()
    time.sleep(1)
    m.receive()
    print(num)
    try:
        while True:
            m.send_location_information()
            time.sleep(1)
            while not m.receive(4):
                logging.error('receive timeout')
            time.sleep(30)
    except KeyboardInterrupt:
        m.close()


needmq = True


def mq():
    q = mqclient.MqClient('172.16.50.54')
    body = None
    while needmq or not body:
        body = q.get_sp_message('Authenticate')
        if body:
            q.send_message('AuthenticateResponse', int(body['SIM']),
                           {'UID': body['UID'],
                            'SerialNo': 0,
                            'RegisterNo': body['UID'],
                            'SIM': body['SIM'],
                            'IsPassed': 0})
    q.close()


def mdvrs(count):
    global needmq
    a = []
    for i in range(count):
        a.append(threading.Thread(target=mdvr_by_thread, args=(i,)))
        a[-1].start()
    time.sleep(10)
    needmq = False
    print('%d threads started' % count)
    for i in a:
        i.join()


if __name__ == '__main__':
    num = 10
    if len(sys.argv) > 1:
        num = int(sys.argv[1])
    mdvrs(num)
