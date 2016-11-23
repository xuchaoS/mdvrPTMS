#!/usr/bin/python
# -*- coding:utf-8 -*-
import mdvr
import math
import itertools
import random
import time
import logging
import threading

__author__ = 'shangxc'


def start(phone_num, authentication_code, ip='172.16.50.98', longitude=116.298011, latitude=39.964678, point_count=50,
          radius=1, interval=15, alarm_interval=0, port=9876):
    gps_list = ((longitude + radius * math.sin(i * 2 * math.pi / point_count),
                 latitude + radius * math.cos(i * 2 * math.pi / point_count)) for i in range(point_count))
    alarm_flag_list = [[1 if j == i else 0 for j in range(32)] for i in range(32)]
    # alarm_flag_list = [[0 for j in range(32)] for i in range(5)]
    # alarm_flag_list[0][0] = 1
    # alarm_flag_list[1][1] = 1
    # alarm_flag_list[2][20] = 1
    # alarm_flag_list[3][21] = 1
    # alarm_flag_list[4][23] = 1
    gps_cycle = itertools.cycle(gps_list)
    alarm_flag_cycle = itertools.cycle(alarm_flag_list)
    m = mdvr.MDVR(phone_num=phone_num, authentication_code=authentication_code, ip=ip, port=port)
    m.connect()
    m.send_terminal_authentication()
    m.receive()
    m.receive_loop()
    for gps, alarm_flag in zip(gps_cycle, alarm_flag_cycle):
        try:
            m.set_gps(mdvr.GPS(*gps, height=random.randint(0, 200), speed=random.randint(0, 200),
                               direction=random.randint(0, 360)))
            m.alarm_flag = alarm_flag[:]
            if alarm_interval != 0:
                m.alarm_flag[0] = 1 if (m.next_message_num - 1) % alarm_interval == 0 else 0
            # print(m.alarm_flag)
            m.send_location_information()
            time.sleep(interval)
        except KeyboardInterrupt:
            m.close()
            break


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s ')
    phone_num = 18812345676  # 电话号码（多个设备为加1递增）
    # authentication_code = 'RMING9876543'  # 鉴权码
    authentication_codes = ['99999BC00005']  # 鉴权码列表
    data_access_ip = '172.16.50.98'  # 数据接入IP
    data_access_port = 9876  # 端口
    longitude = 116.298011  # 中心经纬度
    latitude = 39.964678
    longitude_offset = 0.2  # 中心经纬度偏移(多个设备之间)
    latitude_offset = 0.2
    point_count = 50  # 点总数
    radius = 10  # 半径，单位为经纬度的度数
    interval = 1  # 上传GPS的时间间隔
    alarm_interval = 0  # 一键报警间隔，单位为上传GPS的个数：如1为每个GPS都有报警
                        # 2为每两个GPS有1个报警，即间隔1个GPS，以此类推，默认0（不增加报警，与32等效）

    for i, authentication_code in enumerate(authentication_codes):
        threading.Thread(
            target=start,
            kwargs=dict(phone_num=phone_num + i, authentication_code=authentication_code, ip=data_access_ip,
                        longitude=longitude + longitude_offset * i, latitude=latitude + latitude_offset * i,
                        point_count=point_count, radius=radius, interval=interval, alarm_interval=alarm_interval,
                        port=data_access_port)
        ).start()
        # start(phone_num=phone_num, authentication_code=authentication_code, ip=data_access_ip, longitude=longitude,
        #       latitude=latitude, point_count=point_count, radius=radius, interval=interval)
