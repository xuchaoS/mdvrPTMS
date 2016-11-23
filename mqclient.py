#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'shangxc'
import pika
import time
import json
import logging

BINDIND_KEY = ('Register',
               'RegisterResponse',
               'UnRegister',
               'UnRegisterResponse',
               'Authenticate',
               'AuthenticateResponse',
               'OnOffline',
               'AlarmInfo',
               'ManualConfirmAlert',
               'BusinessAlert',
               'DeviceAlert',
               'RoundRegion',
               'DelRoundRegion',
               'SquareRegion',
               'DelSquareRegion',
               'PolygonsRegion',
               'DelPolygonsRegion',
               'RouteInfo',
               'DelRouteRegion',
               'GenenalResponse',
               'QueryAllParam',
               'QueryPartParam',
               'SetTermParam',
               'QueryParaResponse',
               'Test808')

def on_message(channel, merhod_frame, header_frame, body):
    print(time.ctime(), merhod_frame.routing_key, json.loads(body.decode()))
    channel.basic_ack(delivery_tag=merhod_frame.delivery_tag)

class MqClient(object):
    def __init__(self, ip):
        param = pika.ConnectionParameters(host=ip, port=5672)
        self.connection = pika.BlockingConnection(parameters=param)
        self.channel = self.connection.channel()
        self.queue = self.channel.queue_declare(queue='shangxcTest', auto_delete=False)
        for key in BINDIND_KEY:
            self.channel.queue_bind(queue='shangxcTest', exchange='MDVR_EXCHANGE', routing_key='MDVR.%s.*' % key)
        self.channel.queue_bind(queue='shangxcTest', exchange='GPS_EXCHANGE', routing_key='MDVR.GpsInfo.*')
        self.channel.queue_purge('shangxcTest')
        for key in BINDIND_KEY:
            self.channel.queue_declare(queue='shangxcTest_%s' % key, auto_delete=False)
            self.channel.queue_bind(queue='shangxcTest_%s' % key, exchange='MDVR_EXCHANGE', routing_key='MDVR.%s.*' % key)
            self.channel.queue_purge('shangxcTest_%s' % key)
        self.channel.queue_declare(queue='shangxcTest_GpsInfo', auto_delete=False)
        self.channel.queue_bind(queue='shangxcTest_GpsInfo', exchange='GPS_EXCHANGE', routing_key='MDVR.GpsInfo.*')
        self.channel.queue_purge('shangxcTest_GpsInfo')

    def get_message(self):
        method_frame, header_frame, body = self.channel.basic_get(queue='shangxcTest')
        try:
            self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            logging.info('get message: ' + body.decode('gbk'))
            return method_frame.routing_key.split('.')[1], json.loads(body.decode('gbk'))
        except:
            pass

    def get_sp_message(self, routing_key):
        try:
            method_frame, header_frame, body = self.channel.basic_get(queue='shangxcTest_%s' % routing_key)
            self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            logging.info('get sp message: ' + body.decode('gbk'))
            return json.loads(body.decode('gbk'))
        except:
            pass

    def send_message(self, routing_key, uid, message, exchange='MDVR_EXCHANGE'):
        self.channel.basic_publish(exchange, 'MDVR.%s.%s' % (routing_key, uid), json.dumps(message))

    def close(self):
        for key in BINDIND_KEY:
            self.channel.queue_delete(queue='shangxcTest_%s' % key)
        self.channel.queue_delete(queue='shangxcTest_GpsInfo')
        self.channel.close()
        self.connection.close()

RegisterResponse = {'UID': str, 'SerialNo': int, 'ResultType': int, 'RegisterNo': str, 'SIM': str}
message_form = {'RegisterResponse': RegisterResponse}

# def message_generater(messageid):
#     def tmp(message_form[messageid].keys()):
#         dic = {}
#         for i in message_form[messageid]:
#             dic[i] = message_form[messageid][i](kargs[i])
#         return dic
#     return tmp
#
# message_RegisterResponse = message_generater('RegisterResponse')

if __name__ == '__main__':
    # a = MqClient('172.16.50.54')
    message_RegisterResponse = message_generater('RegisterResponse')
    print(message_RegisterResponse(UID='123',SerialNo=1,ResultType=1,RegisterNo=1,SIM=1))
