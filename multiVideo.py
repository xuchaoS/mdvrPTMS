#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
__author__ = 'shangxc'
import mdvr
import time
import threading
import logging
import argparse

login_success = 0
login_lock = threading.Lock()
print_delay = 1


def mdvr_by_thread(number, base_num=0, ip='172.16.50.98'):
    num = number + base_num
    m = mdvr.MDVR(19912300000 + num, manufacturer_id='99999', terminal_id='PRO%04d' % num, plate='PRO-%04d' % num,
                  authentication_code='99999PRO%04d' % num, ip=ip, gps=mdvr.GPS(116.123456, 39.987654, 12, 34, 56))
    global login_success
    m.connect()
    m.send_terminal_authentication()
    m.receive()
    with login_lock:
        login_success += 1
    t = threading.Thread(target=receive_loop, args=(m,))
    t.setDaemon(True)
    t.start()
    try:
        while True:
            m.send_location_information()
            time.sleep(30)
    except Exception as e:
        logging.error('%5d closing %r' % (num, e))
        with login_lock:
            login_success -= 1
        m.close()


def receive_loop(m):
    while True:
        m.receive()


def print_login():
    while True:
        time.sleep(print_delay)
        logging.warning('%5d MDVR login success' % login_success)


def mdvrs(count, base_num=0, ip='172.16.50.98'):
    a = []
    for i in range(count):
        a.append(threading.Thread(target=mdvr_by_thread, args=(i, base_num, ip)))
        a[-1].start()
        time.sleep(0.01)
    logging.warning('%5d threads started' % count)
    global print_delay
    print_delay = 10


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s')

    ap = argparse.ArgumentParser(description='create multi MDVR for performance testing')
    ap.add_argument('-d', dest='ip', default='172.16.50.98', type=str, help='destination IP, default=172.16.50.98')
    ap.add_argument('-c', dest='num', default=1, type=int, help='total of MDVR, default=10')
    ap.add_argument('-b', dest='base', default=1, type=int, help='start number of MDVR, default=0')
    ap.add_argument('--print', action='store_true', dest='print_login', help='print runing MDVR number per second')
    args = ap.parse_args()
    if args.print_login:
        p = threading.Thread(target=print_login)
        p.setDaemon(True)
        p.start()
    mdvrs(args.num, args.base, args.ip)
