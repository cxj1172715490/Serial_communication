# coding=utf-8
import serial
import time

data_ser = serial.Serial(port='COM3', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0.5,
                         xonxoff=False, rtscts=False, dsrdtr=False)
# print(data_ser)
data_ser.flushInput()
print(data_ser.in_waiting)

if __name__ == '__main__':
    result = data_ser.write(b'readsn\r\n')
    time.sleep(2)
    str = data_ser.read(1000).decode('utf-8')
    print(str)
    str1=str.split('\r\n')
    print(str1[1])

