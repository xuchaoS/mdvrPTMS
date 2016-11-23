#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'shangxc'
from socket import socket, AF_INET, SOCK_STREAM, error, SHUT_RDWR
from threading import Thread
from time import ctime, strftime
import binascii
import logging
import re
from mdvr import Message, int_to_byte, str_to_string, printfuled
import random

HOST = ''
PORT = 9876
ADDR = (HOST, PORT)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
mdvrs = []
replyid = {'0001', '0104', '0107', '0201', '0805', '0802'}
authentication_code = '123459876543'
phone_num = 18812345678
mdvr = None


class Client(Thread):
    def __init__(self, tcpclisock, addr):
        Thread.__init__(self)
        self.tcpCliSock = tcpclisock
        self.addr = addr

    def run(self):
        tmp = Thread(target=self.receive)
        tmp.start()

    def __str__(self):
        return 'IP:%s  PORT:%d' % (str(self.addr[0]),  self.addr[1])

    def receive(self):
        logging.info('new connecct start')
        while True:
            rec = self.tcpCliSock.recv(4096)
            if rec:
                strrec = printfuled(rec)
                logging.info('receive: ' + strrec)
                messageid = strrec[2: 6]
                if messageid in replyid:
                    pass
                elif messageid == '0100':
                    messagebody = rec[11: 13] + int_to_byte(0) + str_to_string(authentication_code)
                    # messagebody = rec[11: 13] + int_to_byte(1)
                    # messagebody = rec[11: 13] + int_to_byte(2)
                    # messagebody = rec[11: 13] + int_to_byte(3)
                    # messagebody = rec[11: 13] + int_to_byte(4)
                    self.send(str(Message(b'\x81\x00', phone_num, messagebody, random.randint(0, 65535))))
                # elif messageid == '0102':
                #     messagebody = rec[11: 13] + rec[1: 3] + int_to_byte(1)
                #     self.send(str(Message(b'\x80\x01', phone_num, messagebody, random.randint(0, 65535))))
                else:
                    messagebody = rec[11: 13] + rec[1: 3] + int_to_byte(0)
                    self.send(str(Message(b'\x80\x01', phone_num, messagebody, random.randint(0, 65535))))
            else:
                self.tcpCliSock.shutdown(SHUT_RDWR)
                self.tcpCliSock.stop()
                logging.warning('connect closed')
                mdvrs.remove(self)
                break

    def send(self, message):
        self.tcpCliSock.send(binascii.a2b_hex(message))
        logging.info('send   : ' + message)


def main():
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(ADDR)
    server.listen(1000)
    try:
        while True:
            tcpCliSock, addr = server.accept()
            tmp = Client(tcpCliSock, addr)
            tmp.start()
            mdvrs.append(tmp)
    except KeyboardInterrupt:
        server.shutdown(SHUT_RDWR)
        server.close()

def starttest():
    Thread(target=main).start()



if __name__ == '__main__':
    Thread(target=main).start()
    # import time
    # time.sleep(10)
    # mdvrs[0].send('7e00020000000000000000000a087e')