#!/usr/local/bin/python3
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
import argparse
import multiprocessing

login_success = 0
login_lock = threading.Lock()
print_delay = 1


def mdvr_by_thread(number, base_num=0, ip='172.16.50.98'):
    num = number + base_num
    m = mdvr.MDVR(19912300000 + num, manufacturer_id='ltest', terminal_id='lt%05d' % num, plate='t%05d' % num,
                  authentication_code='ltestlt%05d' % num, ip=ip)
    global login_success
    m.connect()
    m.send_terminal_authentication()
    # time.sleep(1)
    m.receive()
    # logging.warning('%5d login success' % num)
    with login_lock:
        login_success += 1
    try:
        while True:
            m.send_heart_beat()
            while m.receive(5) == (None, None):
                logging.error('%05d receive timeout heart beat' % num)
            time.sleep(30)
            m.send_location_information()
            while m.receive(5) == (None, None):
                logging.error('%05d receive timeout gps' % num)
            time.sleep(30)
    except Exception as e:
        logging.error('%5d closing %r' % (num, e))
        with login_lock:
            login_success -= 1
        m.close()


def print_login():
    while True:
        time.sleep(print_delay)
        logging.warning('%5d MDVR login success' % login_success)
        # if login_success == count:
        #     logging.warning('all %d MDVR is started')
        #     break


def mdvrs(count, base_num=0, ip='172.16.50.98'):
    a = []
    for i in range(count):
        a.append(threading.Thread(target=mdvr_by_thread, args=(i, base_num, ip)))
        a[-1].start()
        time.sleep(0.01)
    # time.sleep(1)
    logging.warning('%5d threads started' % count)
    global print_delay
    print_delay = 10
    for i in a:
        i.join()


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s: %(message)s')
    # num = 10
    # base = 0
    # ip = '172.16.50.98'
    # if len(sys.argv) > 1:
    #     num = int(sys.argv[1])
    # if len(sys.argv) > 2:
    #     ip = sys.argv[2]
    # if len(sys.argv) > 3:
    #     base = int(sys.argv[3])
    # mdvrs(num, base, ip)
    ap = argparse.ArgumentParser(description='create multi MDVR for performance testing')
    ap.add_argument('-d', dest='ip', default='172.16.50.98', type=str, help='destination IP, default=172.16.50.98')
    ap.add_argument('-c', dest='num', default=10, type=int, help='total of MDVR, default=10')
    ap.add_argument('-b', dest='base', default=0, type=int, help='start number of MDVR, default=0')
    ap.add_argument('--print', action='store_true', dest='print_login', help='print runing MDVR number per second')
    args = ap.parse_args()
    # print(args)
    if args.print_login:
        p = threading.Thread(target=print_login)
        p.setDaemon(True)
        p.start()
    count = args.num
    if count > 10000:
        for i in range(count // 10000):
            multiprocessing.Process(target=lambda base=args.base + i * 10000: mdvrs(10000, base, args.ip)).start()
        last = count % 10000
        if last != 0:
            multiprocessing.Process(target=lambda base=args.base + count - last: mdvrs(last, base, args.ip)).start()

            # mdvrs(args.num, args.base, args.ip)
