#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
import serial
from threading import Lock
import threading
import os


class InnorevController(object):
    '''
    classdocs
    '''

    def __init__(self, port,
                 baudrate=115200,
                 parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE,
                 bytesize=serial.EIGHTBITS,
                 timeout=0.04, parent=None):

        self.master = serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout)
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.timeout = timeout
        self.lock = Lock()
        if True == self.checkconnect(0.5):
            self.read_ALL_input()
            self.read_output()
        else:
            raise Exception('Can not connect')

    def _get_all_input(self):
        self.read_ALL_input()
        time.sleep(0.5)

    def getPort(self):
        return self.port

    def close(self):
        self.master.close()

    def checkconnect(self, time_out=3):
        """
           check the serial port is or not innorev board serial port
            @param slave: default,not used.just adapt style
            @return: bool:success True,failed False
        """
        S_time = time.time()
        # self.WriteSN(1)
        while True:
            if time.time() - S_time < time_out:
                ok, data = self.readDI()
                if ok:
                    return True
            else:
                return False

    def WriteID(self, value, timeout=1):
        """
            @param value: innorev board id
            @param timeout: wait timeout.
            @return: tuple(bool,str)
                    0:success True,failed False
                    1:source data
        """
        with self.lock:
            # self.lock.acquire()
            if self.master.isOpen():
                self.master.flushInput()
                command = b"WriteEEPROM 0x0090 %#.2x\r" % (value)
                n = self.master.write(command)
                data = self.master.readlines()
                self.master.flushOutput()
                if len(data) >= 5 and data[3].strip() == b"OK":
                    # self.lock.release()
                    return True, data[2].strip()
                else:
                    # self.lock.release()
                    return False, data
        # self.lock.release()

    def WriteSN(self, value, timeout=1):
        """
            @param value: innorev board id
            @param timeout: wait timeout.
            @return: tuple(bool,str)
                    0:success True,failed False
                    1:source data
        """
        with self.lock:
            if self.master.isOpen():
                self.master.flushInput()
                command = b"WriteSN %.4d\r" % (value)
                n = self.master.write(command)
                data = self.master.readlines()
                self.master.flushOutput()
                if len(data) >= 4 and data[2].strip() == b"OK":
                    return True, data[1].strip()
                else:
                    return False, data

    def analysisResultDI(self, result, index):
        """
            @param value: innorev board id
            @param timeout: wait timeout.
            @return: tuple(bool,str)
                    0:success True,failed False
                    1:source data
        """
        num = -1
        binary = bin(int(result, 16))
        if len(binary) == 34:
            if index >= 24:
                num = (int(str(result), 16) >> index - 24 + 4 - 1) & 1
            else:
                num = (int(str(result), 16) >> index + 8 - 1) & 1
        else:
            num = (int(result, 16) >> index - 1) & 1
        return num

    def readSingle(self, index, inputType=0):
        """
        @param index 1~20
              inputType 1 output,0 input
        @return num, io status. 0 is on,1 is off
                data,source data
        """
        with self.lock:
            if inputType:
                num = -1
                ok, data = self.readDO()
                while not ok or not data:
                    ok, data = self.readDO()
                return (int(data, 16) >> index - 1) & 1, data
            else:
                ok, data = self.readDI()
                while not ok or not data:
                    ok, data = self.readDI()
                num = self.analysisResultDI(data, index)
                return num, data

    def ReadID(self, timeout=1):
        """
        @param timeout wait for time
        @return tuple(bool, str)
                0:success True,failed False
                1:success it is board id,like "1",failed,it is source data or errormessage
                source data: like "readEEprom 0x0090\n \n0x01\nOK\n >"
        """
        with self.lock:
            if self.master.isOpen():
                self.master.flushInput()
                command = b"readEEprom 0x0090\r"
                # pdb.set_trace()
                n = self.master.write(command)
                data = self.master.readlines()
                self.master.flushOutput()
                if len(data) >= 4 and data[2].strip() == "OK":
                    return True, data[1].strip()
                else:
                    return False, data

    def ReadSN(self, timeout=1):
        """
        @param timeout wait for time
        @return tuple(bool, str)
                0:success True,failed False
                1:success it is board id,like "1",failed,it is source data or errormessage
                source data: like "readEEprom 0x0090\n \n0x01\nOK\n >"
        """
        with self.lock:
            if self.master.isOpen():
                self.master.flushInput()
                command = b"readsn\r"
                # pdb.set_trace()
                n = self.master.write(command)
                data = self.master.readlines()
                self.master.flushOutput()
                if len(data) >= 4 and data[2].strip() == b"OK":
                    return True, data[1].strip()[0:4]
                else:
                    return False, data

    def readDI(self, timeout=1, retry=5):
        """
        @param timeout wait for time
        @return tuple(bool, str)
                0:success True,failed False
                1:success: like "0xfffe",failed,it is source dataor error message
                source data: like "ReadDI\n\nNAK\n>"
        """
        with self.lock:

            if self.master.isOpen():
                self.master.flushInput()
                command = b"ReadDI\r"
                self.master.flushInput()
                self.master.write(command)
                data = self.master.readlines()
                self.master.flushOutput()
                if len(data) >= 5 and data[3].strip() == b"OK":

                    return True, data[2].strip()
                else:

                    return False, data

    def readDO(self, timeout=1):
        """
        @param timeout wait for time
        @return tuple(bool, str)
                0:success True,failed False
                1:success: like "0xfffe",failed,it is source data or error message
                source data: like "ReadDO\n\nNAK\n>" "ReadDO\n\n0xfffe\n>"
        """
        with self.lock:

            if self.master.isOpen():
                command = b"ReadDO\r"
                self.master.flushInput()
                n = self.master.write(command)
                self.master.flushOutput()
                data = self.master.readlines()
                if len(data) >= 5 and data[3].strip() == b"OK":

                    return True, data[2].strip()
                else:

                    return False, data

    def write_output(self, index, status, timeout=1):
        """
        @param index for IO Mapping.the value is 1~16
        @param timeout wait for time
        @return tuple(bool, str)
                0:success True,failed False
                1:success: like "0xfffe",failed,it is source data or error message
                source data: like "ReadDO\n\nNAK\n>" or "ReadDO\n\n0xfffe\n>"
        """
        command = b"WriteDO %#.2x %#.2x\r" % (index, status)
        with self.lock:
            if self.master.isOpen():
                self.master.flushInput()
                self.master.write(command)
                data = self.master.readlines()
                self.master.flushOutput()

                if len(data) >= 4 and data[2].strip() == b"OK":

                    return True, data
                else:

                    return False, data

    def Data_change(self, Data, typ="input"):
        if typ == "input":
            max = 21
        elif typ == "output":
            max = 17
        try:
            io_data = [(int(Data, 16) >> i - 1) & 1 for i in range(1, max)]
        except Exception as e:
            return False
        if typ == "input":
            self.in_put = io_data
        elif typ == "output":
            self.out_put = io_data
        return io_data

    def read_input(self, index=1, time_out=2):
        Stime = time.time()
        while time.time() - Stime < time_out:
            try:
                Data = self.readDI()[1]
                if len(self.Data_change(Data)) == 20:
                    return self.Data_change(Data)[index - 1], Data
                time.sleep(0.1)
            except:
                continue
        return 'False', Data

    def read_ALL_input(self, time_out=2):
        Stime = time.time()
        while time.time() - Stime < time_out:
            try:
                Data = self.readDI()[1]
                if len(self.Data_change(Data)) == 20:
                    return self.Data_change(Data)
                time.sleep(0.1)
            except:
                continue
        return 'False', Data

    def read_output(self, index=1, time_out=1.5):  # 1.5
        Stime = time.time()
        while time.time() - Stime < time_out:
            try:
                Data = self.readDO()[1]
                if len(self.Data_change(Data, typ="output")) == 16:
                    return self.Data_change(Data, typ="output")[index - 1], Data
                time.sleep(0.1)
            except:
                continue
        return 'False', Data


if __name__ == '__main__':
    control = InnorevController("COM3")
    control.write_output(1, 1)
    print(control.read_output(3))
    print(control.out_put)
    # print("write_output",control.write_output(9,1))
    # print("read_ALL_input",control.read_ALL_input())
    # print("read_OUT_input", control.read_output())
    # print(control.WriteSN(1))
    # print(int(control.ReadSN()[-1]))
    # s = time.time()
    # try:
    #     control = InnorevController("COM2")
    # except Exception as e:
    #     print("===============",time.time()-s)
    # print("write_output",control.write_output(9,1))
    # print("read_ALL_input",control.read_ALL_input())
    # print("read_OUT_input", control.read_output())
    # print(control.WriteSN(2))
    # print(int(control.ReadSN()[-1]))
    # print(time.time()-s)
