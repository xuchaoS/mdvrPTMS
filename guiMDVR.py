#!/usr/bin/python
# -*- coding:utf-8 -*-
from tkinter import *
from tkinter.messagebox import showerror, showinfo
from tkinter.filedialog import asksaveasfile, askopenfile
import mdvr
import threading
import time
import logging
import random
import pickle
from uuid import uuid1
import traceback

try:
    import cx_Oracle

    oracle_exist = True
except ImportError:
    oracle_exist = False

__author__ = 'shangxc'


class InputWithTips(object):
    def __init__(self, master=None, tips='', length=10, types=StringVar, row=0, minnum=0, maxnum=0):
        self.length = length
        self.maxnum = maxnum
        self.minnum = minnum
        self._tmp = ''
        self._var = types()
        Label(master, text=' ' + tips + ' : ').grid(row=row, column=0, sticky=E)
        self.entry = Entry(master, width=length + 2, justify=CENTER, textvariable=self._var)
        self.entry.grid(row=row, column=1, sticky=W)
        self.entry.bind('<KeyPress>', self._record)
        self.entry.bind('<KeyRelease>', self._len_limit)

    def _len_limit(self, ev=None):
        if isinstance(self._var, StringVar):
            if len(self._var.get()) > self.length:
                self._var.set(self._tmp)
        else:
            try:
                if self._var.get() > self.maxnum:
                    self._var.set(self.maxnum)
                elif self._var.get() < self.minnum:
                    self._var.set(self.minnum)
                else:
                    self._var.set(self._var.get())
            except TclError:
                if ev.widget.get() == '':
                    self._var.set(0)
                else:
                    self._var.set(self._tmp)

    def _record(self, ev=None):
        try:
            tmp = self._var.get()
        except TclError:
            pass
        else:
            if isinstance(self._var, StringVar):
                self._tmp = tmp if len(tmp) <= self.length else self._tmp
            else:
                self._tmp = tmp if tmp <= self.maxnum or tmp >= self.minnum else self._tmp

    @property
    def value(self):
        return self._var.get()

    @value.setter
    def value(self, value):
        self._var.set(value)


class Backup:
    def save(self, f):
        a = {}
        for i, j in self.__dict__.items():
            if isinstance(j, InputWithTips):
                a[i] = j.value
        pickle.dump(a, f)

    def load(self, f):
        a = pickle.load(f)
        for i, j in self.__dict__.items():
            if isinstance(j, InputWithTips):
                j.value = a[i]


class MdvrInfo(Frame, Backup):
    def __init__(self, master=None):
        super().__init__(master=master, bd=3, relief='ridge')
        self.ip = InputWithTips(self, '数据接入IP', length=15, types=StringVar, row=0)
        self.port = InputWithTips(self, '数据接入端口号', length=5, types=IntVar, row=1, maxnum=65535)
        self.phone_num = InputWithTips(self, '电话号码', length=12, types=IntVar, row=2, maxnum=999999999999)
        self.plate = InputWithTips(self, '车辆标识(车牌号)', length=20, types=StringVar, row=3)
        self.authentication_code = InputWithTips(self, '鉴权码', length=20, types=StringVar, row=4)
        self.province_id = InputWithTips(self, '省域ID', length=5, types=IntVar, row=5, maxnum=65535)
        self.city_id = InputWithTips(self, '市县域ID', length=5, types=IntVar, row=6, maxnum=65535)
        self.manufacturer_id = InputWithTips(self, '制造商ID', length=5, types=StringVar, row=7)
        self.terminal_type = InputWithTips(self, '终端型号', length=20, types=StringVar, row=8)
        self.terminal_id = InputWithTips(self, '终端ID', length=7, types=StringVar, row=9)
        self.plate_color = InputWithTips(self, '车牌颜色', length=3, types=IntVar, row=10, maxnum=255)


class GpsInfo(Frame, Backup):
    def __init__(self, master=None):
        super().__init__(master=master, bd=3, relief='ridge')
        self.longitude = InputWithTips(self, '经度', length=11, types=DoubleVar, row=0, maxnum=179.999999,
                                       minnum=-179.999999)
        self.latitude = InputWithTips(self, '纬度', length=10, types=DoubleVar, row=1, maxnum=89.999999,
                                      minnum=-89.999999)
        self.height = InputWithTips(self, '高度', length=5, types=IntVar, row=2, maxnum=65535)
        self.speed = InputWithTips(self, '速度', length=6, types=DoubleVar, row=3, maxnum=6553.5)
        self.direction = InputWithTips(self, '方向', length=3, types=IntVar, row=4, maxnum=65535)
        # Checkbutton(text='紧急报警', onvalue=1).pack()


class DatabaseInfo(Frame, Backup):
    def __init__(self, master=None):
        super().__init__(master=master, bd=3, relief='ridge')
        self.ip = InputWithTips(self, '数据库IP', length=15, types=StringVar, row=0)
        self.instance_name = InputWithTips(self, '实例名', length=15, types=StringVar, row=1)
        self.user_name = InputWithTips(self, '用户名', length=15, types=StringVar, row=2)
        self.password = InputWithTips(self, '密码', length=15, types=StringVar, row=3)
        self.password.entry.config(show='*')
        self.camera_count = InputWithTips(self, '摄像头数量', length=2, types=IntVar, row=4, maxnum=8)


class AlarmFlag(Frame):
    def __init__(self, master=None):
        super().__init__(master=master, bd=3, relief='ridge')
        self.alarm_flag = []
        for i in range(13):
            self.alarm_flag.append(IntVar())
        Checkbutton(master=self, variable=self.alarm_flag[0], text='紧急报警', onvalue=1 + 0, offvalue=0).pack(anchor=W)
        Checkbutton(master=self, variable=self.alarm_flag[1], text='超速报警', onvalue=1 + 1, offvalue=0).pack(anchor=W)
        Checkbutton(master=self, variable=self.alarm_flag[2], text='进出区域', onvalue=1 + 20, offvalue=0).pack(anchor=W)
        Checkbutton(master=self, variable=self.alarm_flag[3], text='进出路线', onvalue=1 + 21, offvalue=0).pack(anchor=W)
        Checkbutton(master=self, variable=self.alarm_flag[4], text='路线偏离', onvalue=1 + 23, offvalue=0).pack(anchor=W)
        self.otherAlert = BooleanVar()
        Checkbutton(master=self, variable=self.otherAlert, text='不支持的告警', onvalue=True, offvalue=False).pack(anchor=W)
        Checkbutton(master=self, variable=self.alarm_flag[5], text='GNSS模块发生故障', onvalue=1 + 4, offvalue=0).pack(
            anchor=W)
        Checkbutton(master=self, variable=self.alarm_flag[6], text='GNSS天线未接或被剪掉', onvalue=1 + 5, offvalue=0).pack(
            anchor=W)
        Checkbutton(master=self, variable=self.alarm_flag[7], text='GNSS天线短路', onvalue=1 + 6, offvalue=0).pack(anchor=W)
        Checkbutton(master=self, variable=self.alarm_flag[8], text='终端主电源欠压', onvalue=1 + 7, offvalue=0).pack(anchor=W)
        Checkbutton(master=self, variable=self.alarm_flag[9], text='终端主电源掉电', onvalue=1 + 8, offvalue=0).pack(anchor=W)
        Checkbutton(master=self, variable=self.alarm_flag[10], text='终端LED或显示器故障', onvalue=1 + 9, offvalue=0).pack(
            anchor=W)
        Checkbutton(master=self, variable=self.alarm_flag[11], text='TTS模块故障', onvalue=1 + 10, offvalue=0).pack(
            anchor=W)
        Checkbutton(master=self, variable=self.alarm_flag[12], text='摄像头故障', onvalue=1 + 11, offvalue=0).pack(anchor=W)

    def get_list(self):
        result = [0 for _ in range(32)]
        for i in self.alarm_flag:
            if i.get() != 0:
                result[i.get() - 1] = 1
        if self.otherAlert.get():
            result[2] = 1
            result[13] = 1
            result[14] = 1
            result[26] = 1
            result[29] = 1
            result[30] = 1
            result[3] = 1
            result[22] = 1
            result[27] = 1
            result[28] = 1
        return result


def tc(func):
    def t(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:

            showerror('ERROR', '操作失败\n%s' % traceback.format_exc())

    return t


class GuiMdvr(object):
    def __init__(self):
        left = Frame()
        middle = Frame()
        right = Frame()
        self.mdvr_info = MdvrInfo(left)
        self.mdvr_info.pack(padx=10, pady=10)
        self.gps_info = GpsInfo(left)
        self.gps_info.pack(padx=10, pady=10)
        self.alarm_flag = AlarmFlag(middle)
        self.alarm_flag.pack(padx=10, pady=10)
        Button(right, text='连接', command=self._on_connect).pack()
        Button(right, text='注册', command=self._on_regiser).pack()
        Button(right, text='鉴权', command=self._on_auth).pack()
        # Button(right, text='设置GPS', command=self._on_set_gps).pack()
        Button(right, text='发送GPS', command=self._on_send_gps).pack()
        Button(right, text='停止', command=self._on_stop).pack()
        Label(right).pack()
        Button(right, text='导出配置', command=self._on_save).pack()
        Button(right, text='导入配置', command=self._on_load).pack()
        if oracle_exist:
            self.database_info = DatabaseInfo(right)
            self.database_info.pack(padx=10, pady=10)
        Button(right, text='插入报警视频', command=self._insert_alarm_video_to_database).pack()
        left.pack(side=LEFT, anchor=N)
        middle.pack(side=LEFT, anchor=N)
        right.pack(side=TOP, padx=10, pady=10, anchor=N)
        self.mdvr_info.ip.value = '172.16.50.98'
        self.mdvr_info.port.value = 9876
        self.mdvr_info.phone_num.value = random.randint(10000000000, 99999999999)
        self.mdvr_info.plate.value = 'TS-TS1001'
        self.mdvr_info.authentication_code.value = '99999act0001'
        self.mdvr_info.manufacturer_id.value = '99999'
        self.mdvr_info.terminal_id.value = 'BC01001'
        if oracle_exist:
            self.database_info.ip.value = '172.16.80.20'
            self.database_info.instance_name.value = 'PTMS'
            self.database_info.user_name.value = 'ptms'
            self.database_info.password.value = 'oracle'
            self.database_info.camera_count.value = 4

    def _on_connect(self):
        self.m = mdvr.MDVR(phone_num=self.mdvr_info.phone_num.value,
                           province_id=self.mdvr_info.province_id.value,
                           city_id=self.mdvr_info.city_id.value,
                           manufacturer_id=self.mdvr_info.manufacturer_id.value,
                           terminal_type=self.mdvr_info.terminal_type.value,
                           terminal_id=self.mdvr_info.terminal_id.value,
                           plate_color=self.mdvr_info.plate_color.value,
                           plate=self.mdvr_info.plate.value,
                           authentication_code=self.mdvr_info.authentication_code.value,
                           ip=self.mdvr_info.ip.value,
                           port=self.mdvr_info.port.value,
                           gps=mdvr.GPS(longitude=self.gps_info.longitude.value,
                                        latitude=self.gps_info.latitude.value,
                                        height=self.gps_info.height.value,
                                        speed=int(10 * self.gps_info.speed.value),
                                        direction=self.gps_info.direction.value,
                                        ),
                           )
        if self.m.connect() == -1:
            showerror('ERROR', 'Connect fail!!! ')

    @tc
    def _on_auth(self):
        self.m.send_terminal_authentication()
        if self.m.receive()[0] == 0:
            r = threading.Thread(target=self._receive_loop)
            r.setDaemon(True)
            r.start()
            h = threading.Thread(target=self._heart_beat_loop)
            h.setDaemon(True)
            h.start()
        else:
            showerror('', '鉴权失败')

    @tc
    def _on_save(self):
        f = asksaveasfile('wb', filetypes=[('模拟器参数配置文件', '*.sxc'), ('全部', '*')], defaultextension='sxc')
        if f:
            self.mdvr_info.save(f)
            self.gps_info.save(f)
            if oracle_exist:
                self.database_info.save(f)
            f.close()

    @tc
    def _on_load(self):
        f = askopenfile('rb', filetypes=[('模拟器参数配置文件', '*.sxc'), ('全部', '*')])
        if f:
            self.mdvr_info.load(f)
            self.gps_info.load(f)
            if oracle_exist:
                self.database_info.load(f)
            f.close()

    def _receive_loop(self):
        while True:
            try:
                self.m.receive()
            except OSError:
                break
        logging.info('receive loop closed')

    def _heart_beat_loop(self):
        while True:
            time.sleep(60)
            try:
                self.m.send_heart_beat()
            except OSError:
                break
        logging.info('heart beat loop closed')

    def _on_set_gps(self):
        self.m.set_gps(mdvr.GPS(longitude=self.gps_info.longitude.value,
                                latitude=self.gps_info.latitude.value,
                                height=self.gps_info.height.value,
                                speed=int(10 * self.gps_info.speed.value),
                                direction=self.gps_info.direction.value,
                                )
                       )

    @tc
    def _on_send_gps(self):
        self.m.set_gps(mdvr.GPS(longitude=self.gps_info.longitude.value,
                                latitude=self.gps_info.latitude.value,
                                height=self.gps_info.height.value,
                                speed=int(10 * self.gps_info.speed.value),
                                direction=self.gps_info.direction.value,
                                )
                       )
        self.m.alarm_flag = self.alarm_flag.get_list()
        self.m.send_location_information()

    @tc
    def _on_stop(self):
        self.m.close()

    @tc
    def _on_regiser(self):
        # print(self.m.plate)
        self.m.send_register()
        if self.m.receive()[0] == 0:
            # if self.heart_beated is False:
            #     h = threading.Thread(target=self._heart_beat_loop)
            #     h.setDaemon(True)
            #     h.start()
            #     self.heart_beated = True
            pass
        else:
            showerror('', '注册失败')

    @tc
    def _insert_alarm_video_to_database(self):
        conn = cx_Oracle.connect('%s/%s@%s/%s' % (
            self.database_info.user_name.value, self.database_info.password.value, self.database_info.ip.value,
            self.database_info.instance_name.value)
                                 )
        cursor = conn.cursor()
        cursor.execute('''select video_url, video_size from MDI_ALARM_VIDEO''')
        video_url = cursor.fetchone()[0]
        for i in range(self.database_info.camera_count.value):
            cursor.execute('''insert into MDI_ALARM_VIDEO
            (uuid, mdvr_core_sn, channel_id, stream_id, start_time, end_time, video_url, video_size)
  values('%s', '%s', %d, 2, to_date('%s','yyyymmddhh24miss'), to_date('%s','yyyymmddhh24miss'), '%s', 2000000)''' % (
                uuid1(), self.m.authentication_code, i, time.strftime('%Y%m%d%H%M%S'), time.strftime('%Y%m%d%H%M%S'),
                video_url))
        conn.commit()
        conn.close()
        showinfo(message='插入%d路报警视频成功' % self.database_info.camera_count.value)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s ')
    GuiMdvr()
    mainloop()
