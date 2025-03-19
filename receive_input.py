import serial
import struct

ser = serial.Serial('COM3', baudrate=9600)

while True:
    val = ser.read(2)
    print(struct.unpack("h", val))