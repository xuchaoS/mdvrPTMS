#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
__author__ = 'shangxc'
import sys
import pika
import time
import json
import logging
import argparse

quiet = False

class MqClient(object):
    def __init__(self, ip):
        param = pika.ConnectionParameters(host=ip, port=5672)
        self.connection = pika.BlockingConnection(parameters=param)
        self.channel = self.connection.channel()
        self.sender_channel = self.connection.channel()

        self.channel.queue_declare(queue='pTest')
        self.channel.queue_bind(queue='pTest', exchange='MDVR_EXCHANGE', routing_key='MDVR.Authenticate.*')
        self.channel.queue_bind(queue='pTest', exchange='MDVR_EXCHANGE', routing_key='MDVR.OnOffline.*')
        self.channel.queue_bind(queue='pTest', exchange='GPS_EXCHANGE', routing_key='MDVR.GpsInfo.*')
        self.channel.queue_purge('pTest')

        self.channel.queue_declare(queue='pTest_Authenticate')
        self.channel.queue_bind(queue='pTest_Authenticate', exchange='MDVR_EXCHANGE', routing_key='MDVR.Authenticate.*')
        self.channel.queue_purge('pTest_Authenticate')
        self.channel.basic_consume(self.on_message, 'pTest_Authenticate')

        self.channel.queue_declare(queue='pTest_Register')
        self.channel.queue_bind(queue='pTest_Register', exchange='MDVR_EXCHANGE', routing_key='MDVR.Register.*')
        self.channel.queue_purge('pTest_Register')
        self.channel.basic_consume(self.on_message_reg, 'pTest_Register')

        self.channel.queue_declare(queue='pTest_OnOffline')
        self.channel.queue_bind(queue='pTest_OnOffline', exchange='MDVR_EXCHANGE', routing_key='MDVR.OnOffline.*')
        self.channel.queue_purge('pTest_OnOffline')

        self.channel.queue_declare(queue='pTest_GpsInfo')
        self.channel.queue_bind(queue='pTest_GpsInfo', exchange='GPS_EXCHANGE', routing_key='MDVR.GpsInfo.*')
        self.channel.queue_purge('pTest_GpsInfo')

    def send_message(self, routing_key, uid, message, exchange='MDVR_EXCHANGE'):
        self.sender_channel.basic_publish(exchange, 'MDVR.%s.%s' % (routing_key, uid), json.dumps(message))

    def start(self):
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.stop()

    def on_message(self, channel, merhod_frame, header_frame, body):
        body = json.loads(body.decode())
        if not quiet:
            print(time.ctime(), merhod_frame.routing_key, body)
        self.send_message('AuthenticateResponse', body['UID'],
                          {'UID': body['UID'],
                           'SerialNo': int(body['SerialNo']),
                           'RegisterNo': body['UID'],
                           'SIM': body['SIM'],
                           'IsPassed': 0,
                           'VehicleId': body['UID'][-7:]
                           }
                          )
        channel.basic_ack(delivery_tag=merhod_frame.delivery_tag)

    def on_message_reg(self, channel, merhod_frame, header_frame, body):
        body = json.loads(body.decode())
        if not quiet:
            print(time.ctime(), merhod_frame.routing_key, body)
        self.send_message('RegisterResponse', body['UID'],
                          {'UID': body['UID'],
                           'SerialNo': int(body['SerialNo']),
                           'RegisterNo': body['UID'],
                           'SIM': body['SIM'],
                           'ResultType': 0,
                           'VehicleId': body['VehicleId']
                           }
                          )
        channel.basic_ack(delivery_tag=merhod_frame.delivery_tag)

    def stop(self):
        self.channel.stop_consuming()
        self.channel.queue_delete(queue='pTest_Authenticate')
        self.channel.queue_delete(queue='OnOffline')
        self.channel.queue_delete(queue='pTest_GpsInfo')
        self.channel.stop()
        self.connection.close()


if __name__ == '__main__':
    # ip = '172.16.50.54'
    # if len(sys.argv) > 1:
    #     ip = sys.argv[1]
    # a = MqClient(ip)
    # a.start()
    ap = argparse.ArgumentParser(description='create multi MDVR for performance testing')
    ap.add_argument('-d', dest='ip', default='192.168.204.131', type=str, help='rabbitMQ IP, default=172.16.50.54')
    ap.add_argument('-q', action='store_true', dest='quiet', help='be quiet when running')
    args = ap.parse_args()
    quiet = args.quiet
    a = MqClient(args.ip)
    a.start()
