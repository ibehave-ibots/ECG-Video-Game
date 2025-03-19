import serial
import struct
import time

fmt = "h"
packet_size = struct.calcsize(fmt)

buffer = bytearray()

ser = serial.Serial('COM3', baudrate=9600)




while True:
    time.sleep(0.1)
    if ser.in_waiting:
        buffer.extend(ser.read(ser.in_waiting))
    
    while len(buffer) >= packet_size:
        packet, buffer = buffer[:packet_size], buffer[packet_size:]
        print(struct.unpack(fmt, packet)[0])