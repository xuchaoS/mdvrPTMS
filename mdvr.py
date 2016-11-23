#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'shangxc'
from socket import socket, AF_INET, SOCK_STREAM, error, SHUT_RDWR, timeout as timeoutError
from threading import Thread, Lock
from time import ctime, strftime, sleep, time
import re
from uuid import uuid1
import traceback
from os import mkdir, path
from datetime import datetime
import logging
import binascii
import functools
import operator
import multiprocessing
import decimal
import operator
import json
import itertools

MESSAGE_START = b'\x7e'
MESSAGE_END = b'\x7e'
MESSAGE_ID = {'terminal common reply': b'\x00\x01',
              'platform common reply': b'\x80\x01',
              'heart beat': b'\x00\x02',
              'request message afresh': b'\x80\x03',
              'terminal register': b'\x01\x00',
              'terminal register reply': b'\x81\x00',
              'terminal logout': b'\x00\x03',
              'terminal authentication': b'\x01\x02',
              'location information': b'\x02\x00',
              'set polygons region': b'\x86\x04',
              'del polygons region': b'\x86\x05',
              'set route info': b'\x86\x06',
              'del route info': b'\x86\x07',
              'set terminal param': b'\x81\x03',
              'N9M penetrate down': b'\x95\x10',
              'N9M penetrate up': b'\x15\x10',
              'text message down': b'\x83\x00',
              }

MESSAGE_FORMAT = {'terminal common reply': b'\x00\x01',
                  'platform common reply': b'\x80\x01',
                  'heart beat': b'\x00\x02',
                  'request message afresh': b'\x80\x03',
                  'terminal register': {'id': b'\x01\x00', 'message body': b'%s' * 7},
                  'terminal register reply': b'\x81\x00',
                  'terminal logout': b'\x00\x03',
                  'terminal authentication': b'\x01\x02',
                  }

mdvr_list = {}
error_count = 0


def int_to_word(value):
    if isinstance(value, int) and value <= 65535:
        return bytes((value >> 8,)) + bytes((value & 255,))


def int_to_byte(value):
    if isinstance(value, int) and value <= 255:
        return bytes((value,))


def str_to_byte(value):
    if isinstance(value, str):
        return value.encode('ascii')


def str_to_string(value):
    if isinstance(value, str):
        return value.encode('GBK')


def string_to_str(value):
    if isinstance(value, bytes):
        return value.decode('GBK')


def printfuled(message):
    return str(binascii.b2a_hex(message))[2: -1]


def bitlist_to_int(alist, is_low_to_up=True):
    if is_low_to_up:
        alist = reversed(alist)
    return functools.reduce(lambda a, b: (a << 1) | b, alist)


def __bitlist_to_int(a, b):
    return (a << 1) | b


def int_to_dword(value):
    if isinstance(value, int) and value <= 4294967295:
        return int_to_word(value >> 16) + int_to_word(value & 65535)


def dword_to_int(value):
    assert isinstance(value, bytes)
    assert len(value) == 4
    return (value[0] << 24) | (value[1] << 16) | (value[2] << 8) | value[3]


def int_to_bcd(value, n):
    if isinstance(value, int):
        return binascii.a2b_hex(('%0' + str(2 * n) + 'd') % value)


def bcd_to_time_str(value):
    assert isinstance(value, bytes)
    assert len(value) == 6
    time_with_out_line = printfuled(value)
    return datetime.strptime(time_with_out_line, '%y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')


def word_to_int(value):
    assert isinstance(value, bytes)
    assert len(value) == 2
    return (value[0] << 8) | value[1]


def byte_to_int(value):
    return value[0]


class GPS(object):
    def __init__(self, longitude=0.0, latitude=0.0, height=0, speed=0, direction=0):
        # self.longitude = float(longitude)
        # self.latitude = float(latitude)
        # self.height = int(height)
        # self.speed = int(speed)
        # self.direction = int(direction)
        self.longitude = decimal.Decimal(str(longitude))
        self.latitude = decimal.Decimal(str(latitude))
        self.height = int(height)
        self.speed = int(speed)
        self.direction = int(direction)

    def get(self):
        return {'longitude': self.longitude,
                'latitude': self.latitude,
                'height': self.height,
                'speed': self.speed,
                'direction': self.direction}


def _read_video_file(file_name):
    result = []
    with open(file_name, 'rb') as f:
        result.append(f.read(12))
        result.append(f.read(512))
        while True:
            data = f.read(1024)
            if data == b'':
                break
            else:
                result.append(data)
    print('length of video data list is %d' % len(result))
    return result


class MDVR(object):
    try:
        live_video_data_list = _read_video_file('./videoFile/video20m.h264')
    except FileNotFoundError:
        live_video_data_list = _read_video_file('../videoFile/video20m.h264')

    def __init__(self, phone_num, province_id=0, city_id=0, manufacturer_id='12345', terminal_type='ATM0101',
                 terminal_id='9876', plate_color=0, plate='京A0001', authentication_code='', gps=GPS(),
                 mileage=0, oil=0, ip='127.0.0.1', port=9876):
        super(MDVR, self).__init__()
        self._buffer = b''
        self.phoneNum = int(phone_num)
        self.province_id = int(province_id)
        self.city_id = int(city_id)
        self.manufacturer_id = str(manufacturer_id.rjust(5))
        self.terminal_type = str(terminal_type)
        self.terminal_id = str(terminal_id)
        self.plate_color = int(plate_color)
        self.plate = str(plate)
        self.ip = str(ip)
        self.port = int(port)
        self.connected = False
        self.last_receive = ''
        self.next_message_num = 0
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.waiting_response = {}
        self.authentication_code = str(authentication_code)
        self.alarm_flag = [0 for i in range(32)]
        self.status = [0 for i in range(32)]
        self.gps = gps
        self.set_gps(gps)
        self.mileage = int(mileage)
        self.oil = int(oil)
        self.polygons_regions = {}
        self.routes = {}
        self.live_videos = {}

    def set_gps(self, gps=GPS()):
        self.gps = gps
        if self.gps.longitude >= 0:
            self.status[3] = 0
        else:
            self.status[3] = 1
        if self.gps.latitude >= 0:
            self.status[2] = 0
        else:
            self.status[2] = 1
        if gps.direction or gps.height or gps.latitude or gps.longitude or gps.speed:
            self.status[1] = 1
        else:
            self.status[1] = 0

    def connect(self):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((self.ip, self.port))
            self.connected = True
            logging.info('%012d start connect', self.phoneNum)
        except error:
            logging.error('Connect fail!!!')
            return -1

    def close(self):
        try:
            self.live_videos = {}
            self.connected = False
            self.sock.shutdown(SHUT_RDWR)
            self.sock.close()
        except Exception:
            pass
        logging.info('%012d close connect' % self.phoneNum)

    def send_heart_beat(self):
        message_body = b''
        self.send_message(MESSAGE_ID['heart beat'], message_body, 'heart beat')

    def send_register(self):
        message_body = b'%s' * 7 % (int_to_word(self.province_id),
                                    int_to_word(self.city_id),
                                    str_to_byte(self.manufacturer_id),
                                    str_to_byte(self.terminal_type).ljust(20, b'\x00'),
                                    str_to_byte(self.terminal_id).ljust(7, b'\x00'),
                                    int_to_byte(self.plate_color),
                                    str_to_string(self.plate))
        self.send_message(MESSAGE_ID['terminal register'], message_body, 'terminal register')

    def send_logout(self):
        message_body = b''
        self.send_message(MESSAGE_ID['terminal logout'], message_body, 'terminal logout')

    def send_terminal_authentication(self):
        assert self.authentication_code != ''
        message_body = str_to_string(self.authentication_code)
        self.send_message(MESSAGE_ID['terminal authentication'], message_body, 'terminal authentication')

    def send_location_information(self):
        alarm_flag = int_to_dword(bitlist_to_int(self.alarm_flag))
        status = int_to_dword(bitlist_to_int(self.status))
        latitude = int_to_dword(abs(int(self.gps.latitude * 1000000)))
        longitude = int_to_dword(abs(int(self.gps.longitude * 1000000)))
        height = int_to_word(self.gps.height)
        speed = int_to_word(self.gps.speed)
        direction = int_to_word(self.gps.direction)
        time = int_to_bcd(int(strftime('%y%m%d%H%M%S')), 6)
        message_body_base = b'%s' * 8 % (alarm_flag,
                                         status,
                                         latitude,
                                         longitude,
                                         height,
                                         speed,
                                         direction,
                                         time,)
        message_body_addition = b'\x01\x04%s\x02\x02%s\x03\x02%s' % (int_to_dword(self.mileage),
                                                                     int_to_word(self.oil),
                                                                     int_to_word(
                                                                         self.gps.speed))  # +b'\xe0\x53'+b'0'*83
        message_body = message_body_base + message_body_addition
        self.send_message(MESSAGE_ID['location information'], message_body, 'location information')

    def send_message(self, message_id, message_body, log_tips='bytes', add_to_waiting_response=True):
        # message = self.generate_message(message_id, message_body)
        # self.send(message, log_tips)
        message = Message(message_id, self.phoneNum, message_body, self.next_message_num)
        self.send(message, log_tips, add_to_waiting_response)
        if self.next_message_num < 65535:
            self.next_message_num += 1
        else:
            self.next_message_num = 0

    def send(self, message, log_tips='bytes', add_to_waiting_response=True):
        bytes_message = bytes(message)
        self.sock.send(bytes_message)
        logging.info('%012d send %-20s : %s' % (self.phoneNum, log_tips, str(binascii.b2a_hex(bytes_message))))
        if isinstance(message, Message) and add_to_waiting_response:
            self.waiting_response[message.message_num] = message

    def receive_message(self, timeout=None):
        if timeout is None:
            rec = self.sock.recv(4096)
        else:
            self.sock.settimeout(timeout)
            try:
                rec = self.sock.recv(4096)
            except timeoutError:
                logging.warning('no message to recv')
                return None
            finally:
                self.sock.settimeout(None)
        if rec:
            logging.info('receive : %s' % printfuled(rec))
            return rec
        else:
            logging.info('%12d receive none bytes closing connect' % self.phoneNum)
            self.close()

    def receive(self, timeout=None):
        if timeout is None:
            rec = self.sock.recv(4096)
        else:
            self.sock.settimeout(timeout)
            try:
                rec = self.sock.recv(4096)
            except timeoutError:
                logging.warning('no message to recv')
                return None, None
            finally:
                self.sock.settimeout(None)
        result = None
        message_id = None
        if rec:
            logging.info('receive : %s' % printfuled(rec))
            if self._buffer:
                self._buffer += rec
            else:
                if rec.startswith(Message.MESSAGE_START):
                    self._buffer += rec
                else:
                    logging.warning('this message is not start with %s, ignore it' % printfuled(Message.MESSAGE_START))
            while self._buffer:
                index = self._buffer.find(Message.MESSAGE_END, 1)
                if index == -1:
                    break
                else:
                    rec = self._buffer[: index + 1]
                    self._buffer = self._buffer[index + 1:]
                    # if message_start_end_right(rec):
                    message_head_body_checksum = recover_escape(rec[1:-1])
                    if check_checksum(message_head_body_checksum):
                        message_body_property = ((message_head_body_checksum[2] << 8) | message_head_body_checksum[3])
                        is_separate = message_body_property & 0b0010000000000000
                        is_rsa = message_body_property & 0b0000010000000000
                        message_body_len = message_body_property & 0b0000001111111111
                        if (not is_separate) and (not is_rsa):
                            message_head = message_head_body_checksum[:12]
                            message_body = message_head_body_checksum[12: -1]
                            message_id = message_head[: 2]
                            message_num = word_to_int(message_head[10: 12])
                            if len(message_body) == message_body_len:
                                if message_id == MESSAGE_ID['terminal register reply']:
                                    result = self._receive_terminal_register_reply(message_body)
                                elif message_id == MESSAGE_ID['platform common reply']:
                                    result = self._receive_plat_common_reply(message_body)
                                elif message_id == MESSAGE_ID['set polygons region']:
                                    self._receive_set_polygons_region(message_body, message_num)
                                elif message_id == MESSAGE_ID['del polygons region']:
                                    self._receive_del_polygons_region(message_body, message_num)
                                elif message_id == MESSAGE_ID['set route info']:
                                    self._receive_set_route_info(message_body, message_num)
                                elif message_id == MESSAGE_ID['del route info']:
                                    self._receive_del_route_info(message_body, message_num)
                                elif message_id == MESSAGE_ID['set terminal param']:
                                    self._receive_set_param(message_body, message_num)
                                elif message_id == MESSAGE_ID['N9M penetrate down']:
                                    self._receive_penetrate_message(message_body, message_num)
                                elif message_id == MESSAGE_ID['text message down']:
                                    self._receive_text_message_down(message_body, message_num)
                                else:
                                    logging.warning('reply id %s is not support' % printfuled(message_id))
                                    self._send_terminal_common_reply(message_num, message_id, 3)
                            else:
                                logging.warning('message len in message head is not correct')
                        else:
                            logging.warning('separate or rsa is not support')
                    else:
                        logging.warning('checksum is not correct: %s' % printfuled(rec))
                        # else:
                        #     logging.warning('message is not start or end with 0x7e')
        else:
            logging.info('%12d receive none bytes closing connect' % self.phoneNum)
            self.close()
        return result, message_id

    def receive_loop(self):
        t = Thread(target=self._receive_loop)
        t.setDaemon(True)
        t.start()

    def _receive_loop(self):
        while self.connected:
            try:
                self.receive()
            except Exception as e:
                logging.error('%s' % e)

    def _receive_terminal_register_reply(self, message_body):
        message_reply_num = (message_body[0] << 8) | message_body[1]
        try:
            self.waiting_response.pop(message_reply_num)
        except KeyError as e:
            logging.warning('reply num is not correct: %d' % message_reply_num)
        else:
            result = message_body[2]
            if result == 0:
                self.authentication_code = string_to_str(message_body[3:])
                logging.info('register successful, authentication_code is %s' % repr(self.authentication_code))
            elif result == 1:
                logging.warning('this car is registered')
            elif result == 2:
                logging.warning('this car is not in database')
            elif result == 3:
                logging.warning('this terminal is registered')
            elif result == 4:
                logging.warning('this terminal is not in database')
            else:
                logging.warning('this result num is not support: %d' % result)
        return result

    def _receive_plat_common_reply(self, message_body):
        message_reply_num = (message_body[0] << 8) | message_body[1]
        result = None
        try:
            original_message = self.waiting_response.pop(message_reply_num)
        except KeyError as e:
            logging.warning('reply num is not correct: %d' % message_reply_num)
        else:
            if original_message.message_id == message_body[2:4]:
                result = message_body[4]
                logging.info('reply %s : result num is %d' % (original_message, result))
                if original_message.message_id == MESSAGE_ID['location information'] and result == 0:
                    self.alarm_flag[0] = 0
                    self.alarm_flag[3] = 0
                    self.alarm_flag[20] = 0
                    self.alarm_flag[21] = 0
                    self.alarm_flag[22] = 0
                    self.alarm_flag[27] = 0
                    self.alarm_flag[28] = 0
                    self.alarm_flag[31] = 0
            else:
                logging.warning('message id in reply message is not correct')
        return result

    def _receive_set_polygons_region(self, message_body, message_num):
        index = 0
        region_id = dword_to_int(message_body[index: index + 4])
        cur_region = {}
        self.polygons_regions[region_id] = cur_region
        index += 4
        region_property = word_to_int(message_body[index: index + 2])
        cur_region['region_property'] = region_property
        index += 2
        if region_property & 0b1:  # 根据时间
            start_time = bcd_to_time_str(message_body[index: index + 6])
            cur_region['start_time'] = start_time
            index += 6
            stop_time = bcd_to_time_str(message_body[index: index + 6])
            cur_region['stop_time'] = stop_time
            index += 6
        if region_property & 0b10:  # 限速
            max_speed = word_to_int(message_body[index: index + 2])
            cur_region['max_speed'] = max_speed
            index += 2
            over_speed_time = byte_to_int(message_body[index: index + 1])
            cur_region['over_speed_time'] = over_speed_time
            index += 1
        # TODO not finished
        logging.info('set polygons region success: ID: %d' % region_id)
        self._send_terminal_common_reply(message_num, MESSAGE_ID['set polygons region'], 0)

    def _receive_del_polygons_region(self, message_body, message_num):
        region_count = message_body[0]
        index = 1
        region_id_list = []
        for _ in range(region_count):
            region_id_list.append(dword_to_int(message_body[index: index + 4]))
            index += 4
        for i in region_id_list:
            try:
                self.polygons_regions.pop(i)
            except:
                logging.warning('not exist region id: %d' % i)
        logging.info('del polygons region success: count: %d, IDs: %s' % (region_count, region_id_list))
        self._send_terminal_common_reply(message_num, MESSAGE_ID['del polygons region'], 0)

    def _receive_set_route_info(self, message_body, message_num):
        index = 0
        route_id = dword_to_int(message_body[index: index + 4])
        index += 4
        cur_route = {}
        self.routes[route_id] = cur_route
        # TODO not finished
        logging.info('set route info success: ID: %d' % route_id)
        self._send_terminal_common_reply(message_num, MESSAGE_ID['set route info'], 0)

    def _receive_del_route_info(self, message_body, message_num):
        route_count = message_body[0]
        index = 1
        route_id_list = []
        for _ in range(route_count):
            route_id_list.append(dword_to_int(message_body[index: index + 4]))
            index += 4
        for i in route_id_list:
            try:
                self.routes.pop(i)
            except:
                logging.warning('not exist route id: %d' % i)
        logging.info('del route info success: count: %d, IDs: %s' % (route_count, route_id_list))
        self._send_terminal_common_reply(message_num, MESSAGE_ID['del route info'], 0)

    def _receive_set_param(self, message_body, message_num):
        param_count = message_body[0]
        index = 1
        params = {}
        for i in range(param_count):
            # print(printfuled(message_body))
            # print(printfuled(message_body[index: index + 4]))
            param_id = dword_to_int(message_body[index: index + 4])
            index += 4
            param_len = message_body[index]
            index += 1
            if param_len == 1:
                param_value = message_body[index]
            elif param_len == 2:
                param_value = word_to_int(message_body[index: index + 2])
            elif param_len == 4:
                param_value = dword_to_int(message_body[index: index + 4])
            else:
                param_value = string_to_str(message_body[index: index + param_len])
            index += param_len
            params[param_id] = param_value
        logging.info('set params success: count: %d' % param_count)
        for param_id, param_value in params.items():
            logging.info('set param success: id: 0x%x, value: %s' % (param_id, param_value))
        self._send_terminal_common_reply(message_num, MESSAGE_ID['set terminal param'], 0)

    def _receive_penetrate_message(self, message_body, message_num):
        payload = json.loads(message_body[13:].decode())
        module = payload['MODULE']
        if module == 'MEDIASTREAMMODEL':
            operation = payload['OPERATION']
            if operation == 'REQUESTALIVEVIDEO':
                self._handle_request_live_video(payload['PARAMETER'])
            elif operation == 'CONTROLSTREAM':
                self._handle_control_stream(payload['PARAMETER'])
            else:
                logging.warning('OPERATION %s is not support' % operation)
        elif module == 'CONFIGMODEL':
            operation = payload['OPERATION']
            if operation == 'SET':
                session = payload['SESSION']
                # 未做报警
                self._send_terminal_common_reply(message_num, MESSAGE_ID['N9M penetrate down'], 0)
                reply = {"MODULE": "CONFIGMODEL",
                         "OPERATION": "SET",
                         "RESPONSE": {"ERRORCAUSE": "",
                                      "ERRORCODE": 0},
                         "SESSION": session}
                self._send_penetrate_message(reply)
            else:
                logging.warning('OPERATION %s is not support' % operation)
        else:
            logging.warning('MODULE %s is not support' % module)

    def _receive_text_message_down(self, message_body, message_num):
        flag = message_body[0]
        flag_text = []
        if flag & 0b1:
            flag_text.append('0: urgency')
        if flag & 0b100:
            flag_text.append('2: monitor display')
        if flag & 0b1000:
            flag_text.append('3: TTS read')
        if flag & 0b10000:
            flag_text.append('4: ad display')
        if flag & 0b100000:
            flag_text.append('5: center navigation')
        else:
            flag_text.append('5: CAN fault code')
        flag_text = ', '.join(flag_text)
        text = string_to_str(message_body[1:])
        logging.info('reveive text message: flag: %s; text :%s' % (flag_text, text))
        self._send_terminal_common_reply(message_num, MESSAGE_ID['text message down'], 0)

    def _handle_request_live_video(self, parameter):
        # import pprint
        # pprint.pprint(parameter)
        video_ip_port_str = parameter['IPANDPORT']
        video_ip_port = video_ip_port_str.split(':')
        video_ip = video_ip_port[0]
        video_port = int(video_ip_port[1])
        stream_name = parameter['STREAMNAME']
        serial = parameter['SERIAL']
        if stream_name in self.live_videos:
            logging.warning('repeat live video request, channel: %s' % stream_name)
        else:
            payload = {"MODULE": "MEDIASTREAMMODEL",
                       "OPERATION": "REQUESTALIVEVIDEO",
                       "RESPONSE":
                           {"ERRORCAUSE": "SUCCESS",
                            "ERRORCODE": 0,
                            "SERIAL": serial,
                            "SSRC": 0,
                            "STREAMNAME": stream_name,
                            "STREAMTYPE": 0
                            },
                       "SESSION": str(uuid1())
                       }
            self._send_penetrate_message(payload)
            try:
                sock = socket(AF_INET, SOCK_STREAM)
                sock.connect((video_ip, video_port))
                payload = {"MODULE": "CERTIFICATE",
                           "OPERATION": "CREATESTREAM",
                           "PARAMETER": {"DEVTYPE": "",
                                         "DSNO": "00610009B1",
                                         "IPANDPORT": video_ip_port_str,
                                         "STREAMNAME": stream_name,
                                         "VISION": "1.0.4"},
                           "SESSION": str(uuid1())}
                self._send_n9m_message(payload, sock)
                self._receive_n9m(sock)
                self.live_videos[stream_name] = sock
                logging.info('%s start connect' % stream_name)
                payload = {"MODULE": "MEDIASTREAMMODEL",
                           "OPERATION": "MEDIATASKSTART",
                           "PARAMETER":
                               {"IPANDPORT": video_ip_port_str,
                                "PT": 2,
                                "SSRC": 0,
                                "STREAMNAME": stream_name
                                },
                           "SESSION": str(uuid1())
                           }
                self._send_penetrate_message(payload)
            except TimeoutError:
                logging.error('video access not reply\n%s' % traceback.format_exc())
            except error:
                logging.error('Connect fail!!! %s,\n%s' % (video_ip_port, traceback.format_exc()))
            else:
                t = Thread(target=self._send_live_video, args=(stream_name,))
                t.setDaemon(True)
                t.start()

    def _handle_control_stream(self, parameter):
        cmd = parameter['CMD']
        if cmd == 0:
            self.live_videos.pop(parameter['STREAMNAME'], None)
        else:
            logging.warning('CMD %d is not support' % cmd)

    def _send_live_video(self, stream_name):
        # sock.send(b'\x08\x02\x00\x00\x00\x00\x02\x00\x52\x00\x00\x00')
        logging.info('starting send video......')
        sock = self.live_videos[stream_name]
        sock.send(self.live_video_data_list[0])
        sock.send(self.live_video_data_list[1])

        for video_data in itertools.cycle(self.live_video_data_list[2:]):
            if stream_name in self.live_videos:
                try:
                    # if i % 250 == 0 :
                    #     logging.error(printfuled(video_data))
                    sock.send(video_data)
                except error as e:
                    self.live_videos.pop(stream_name)
                    logging.error('connection of video server stop unnormal')
                    break
            else:
                sock.shutdown(SHUT_RDWR)
                sock.close()
                break
            sleep(0.04)
        logging.info('send video stopped......')

    def _receive_n9m(self, sock):
        self.sock.settimeout(10)
        try:
            rec = sock.recv(4096)
        except TimeoutError:
            logging.warning('not receive N9M message, please check video access service')
            raise
        else:
            logging.info('reveive n9m: %s' % rec[12:].decode())
        finally:
            self.sock.settimeout(None)

    def _send_n9m_message(self, payload, sock):
        payload = json.dumps(payload)
        payload_len = len(payload)
        n9m_head = b'\x08' + b'\x00' * 3 + int_to_dword(payload_len) + b'\x52' + b'\x00' * 3
        n9m_message = n9m_head + str_to_byte(payload)
        sock.send(n9m_message)
        logging.info('send n9m: %s' % payload)

    def _send_penetrate_message(self, payload):
        payload = json.dumps(payload)
        payload_len = len(payload)
        n9m_head = b'\x00' * 4 + int_to_dword(payload_len) + b'\x52' + b'\x00' * 3
        n9m_message = b'\x00' + n9m_head + str_to_byte(payload)
        self.send_message(MESSAGE_ID['N9M penetrate up'], n9m_message, add_to_waiting_response=False)

    def _send_terminal_common_reply(self, reply_num, reply_id, result):
        message_body = b'%s' * 3 % (int_to_word(reply_num),
                                    reply_id,
                                    int_to_byte(result))
        self.send_message(MESSAGE_ID['terminal common reply'], message_body, 'terminal common reply', False)

    def test(self):
        global error_count
        try:
            self.connect()
            self.send_terminal_authentication()
            for i in range(10):
                sleep(10)
                self.send_heart_beat()
            self.close()
        except:
            print(error_count)


def message_start_end_right(message):
    assert isinstance(message, bytes)
    if message.startswith(MESSAGE_END) and message.endswith(MESSAGE_END):
        return True
    else:
        return False


def recover_escape(message):
    result = message
    result = result.replace(b'\x7d\x02', b'\x7e')
    result = result.replace(b'\x7d\x01', b'\x7d')
    return result


def check_checksum(message):
    message_head_body = message[:-1]
    checksum = message[-1]
    if checksum == functools.reduce(operator.xor, message_head_body):
        return True
    else:
        return False


class Message(object):
    ID_TERMINAL_COMMON_REPLY = b'\x00\x01'
    ID_PLATFORM_COMMON_REPLY = b'\x80\x01'
    ID_HEART_BEAT = b'\x00\x02'
    ID_REQUEST_MESSAGE_AFRESH = b'\x80\x03'
    ID_TERMINAL_REGISTER = b'\x01\x00'
    ID_TERMINAL_REGISTER_REPLY = b'\x81\x00'
    ID_TERMINAL_LOGOUT = b'\x00\x03'
    ID_TERMINAL_AUTHENTICATION = b'\x01\x02'
    MESSAGE_START = b'\x7e'
    MESSAGE_END = b'\x7e'

    def __init__(self, message_id, phone_num, message_body, message_num, is_separate=False, is_rsa=False):
        self.message_id = message_id
        self.phone_num = phone_num
        self.message_body = message_body
        self.message_num = message_num
        self.checksum = b''
        self.message_head = b''
        self.message = b''
        self.is_separate = is_separate
        self.is_rsa = is_rsa
        self.generate_message_head()
        self.generate_checksum()
        self.generate_message()

    def generate_message_head(self):
        self.message_head = self.message_id
        message_body_property = len(self.message_body)
        if self.is_separate:
            message_body_property += (1 << 13)
        if self.is_rsa:
            message_body_property += (1 << 10)
        self.message_head += int_to_word(message_body_property)
        self.message_head += int_to_bcd(self.phone_num, 6)
        self.message_head += int_to_word(self.message_num)
        if self.is_separate:
            pass

    def generate_checksum(self):
        self.checksum = bytes((functools.reduce(operator.xor, self.message_head + self.message_body),))

    @staticmethod
    def make_message_escaped(message):
        assert isinstance(message, bytes)
        if b'\x7d' in message:
            message = message.replace(b'\x7d', b'\x7d\x01')
        if b'\x7e' in message:
            message = message.replace(b'\x7e', b'\x7d\x02')
        return message

    def generate_message(self):
        self.message = self.MESSAGE_START + self.make_message_escaped(
            self.message_head + self.message_body + self.checksum) + self.MESSAGE_END

    def __bytes__(self):
        return self.message

    def __str__(self):
        return printfuled(self.message)


class ChecksumError(Exception):
    def __init__(self):
        super(ChecksumError, self).__init__()
        self.message = 'checksum is invalid!!!'

    def __str__(self):
        return self.message


class BYTE(object):
    def __init__(self, value):
        self.value = None
        if value:
            if isinstance(value, int) and value <= 255:
                self.value = bytes((value,))
            elif isinstance(value, str) and len(value) <= 1:
                self.value = bytes(value, 'utf-8')
            elif isinstance(value, bytes) and len(value) <= 1:
                self.value = value
        else:
            self.value = b'\x00'

    def __str__(self):
        return str(self.value)


class WORD(object):
    def __init__(self, value):
        self.value = None
        if isinstance(value, int) and value <= 65535:
            self.value = BYTE(value // 255).value + BYTE(value % 255).value
        elif isinstance(value, str) and len(value) <= 2:
            if len(value) == 1:
                pass


def multiMDVR(total, thread_per_process=100, ip='127.0.0.1'):
    processes = []
    for i in range(0, total, thread_per_process):
        if total - i < thread_per_process:
            processes.append(multiprocessing.Process(target=multi_thread, args=(i, total - i, ip)))
        else:
            processes.append(multiprocessing.Process(target=multi_thread, args=(i, thread_per_process, ip)))
        processes[-1].start()
    return processes


def multi_thread(start_num, total, ip='127.0.0.1'):
    for i in range(total):
        Thread(target=MDVR(phone_num=start_num + i, ip=ip, authentication_code='%012d' % (start_num + i)).test).start()
        sleep(0.01)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s ' + ' ' * 10 + ' %(pathname)s: %(lineno)s')
    # gps = GPS(136.1234, 66.6543, 321, 123, 300)
    # a = MDVR(13488834791, ip='127.0.0.1', gps=gps)
    # print(BYTE('o').value)
    # print(BYTE(b'0').value)
    # print(BYTE(55).value)
    # a.connect()
    # print('au', a.authentication_code)
    # a.send_register()
    # print('wr', a.waiting_response)
    # # a.receive()
    # print('au', repr(a.authentication_code))
    # sleep(1)
    # a.send_location_information()
    # # a.send_heart_beat()
    # # a.send_logout()
    # a.close()
    # print(a.waiting_response)
    # for i in range(10):
    #     mdvr = []
    #     for i in range(100):
    #         mdvr.append(MDVR(100000+i, ip='127.0.0.1', gps=gps, authentication_code='1000%04d' % i))
    #     thread = []
    #     for i in range(100):
    #         thread.append(multiprocessing.Process(target=mdvr[i].test))
    #     for i in range(100):
    #         thread[i].start()
    #     for i in range(100):
    #         thread[i].join()
    # import time
    # a = time.time()
    # b = multiMDVR(1)
    # for i in b:
    #     i.join()
    # print(time.time()-a)
    gps = GPS(116.1299, 39.7599, 321, 123, 300)
    # a = MDVR(18812345678, authentication_code='99999BC00002', ip='172.16.50.98', manufacturer_id="99999",
    #          terminal_id='BC00002', plate='TS-TS0002', gps=gps)

    # a = MDVR(1234567890, authentication_code='99999act0001', ip='172.16.50.98')
    # a.connect()
    # # a.send_register()
    # a.send_terminal_authentication()
    # a.receive()
    # # for i in range(10):
    # #     # a.alarm_flag[0] = 1
    # #     a.send_location_information()
    # #     a.receive()
    # #     sleep(60)
    # a.receive()
    # while True:
    #     a.receive(60)
    #     a.send_heart_beat()
    #     a.receive()


    # a.send_register()
    # a.receive()
    # a.send_register()
    # a.receive()
    #
    # a.send_terminal_authentication()
    # a.receive()
    # sleep(10)
    # for i in range(10000):
    #     t = time()
    #     # a.send_location_information()
    #     a.send_heart_beat()
    #     if not a.receive_message(4):
    #         logging.error(time() - t)
    # a.status = [1 for i in a.status]
    # a.send_location_information()
    # for i in range(1000):
    #     a.alarm_flag = [1 for i in a.alarm_flag]
    #     a.send_location_information()
    #     a.receive()
    #     sleep(1)
    # a.alarm_flag[0] = 1
    # for i in range(10):
    #     sleep(1)
    #     a.send_heart_beat()
    #     sleep(1)
    #     a.send_location_information()
    # sleep(5)
    # a.send_heart_beat()
    # a.receive()
    # a.sock.send(b'7e00020000018812345678000d8e7e')
    # for i in range(100):
    #     a.send_location_information()
    #     a.receive()
    #     sleep(1)
    # sleep(5)
    # a.sock.send(binascii.a2b_hex('7e000200000188123456780001827e7e0200001c0188123456780002000000000000000e0254f9c8082a43d000c8001e012c160629155636f27e7e000200000188123456780003807e7e0200001c0188123456780002000000000000000e0254f9c8082a43d000c8001e012c160629155636f27e'))
    # sleep(5)
    # print(a.status)
    # a.receive()
    # for i in range(10):
    #     a.receive()
    # sleep(10)
    # a.close()
