import struct
from random import randint
from calliopemini import uart
from calliopemini import *
import time



uart.init(baudrate=9600)
while True:
    display.clear()    
    val = pin_A1_RX.read_analog()
    uart.write(struct.pack("h", val))
    time.sleep(0.000001)
        
    

