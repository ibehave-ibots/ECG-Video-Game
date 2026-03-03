from collections import deque
import math
import random
import socket
import time
import threading
from typing import cast

import dearpygui.dearpygui as dpg
import numpy as np
import serial
import struct
import pygame
import pywt


######## Parameters ######
CALLIOPE_PORT = 'COM5'
DEQUE_MAX_LEN = 500

class SensorIn:

    def __init__(self, serial_port: str = 'COM5', baudrate: int = 9600, max_len = 500) -> None:
        try:
            self._ser =  serial.Serial(CALLIOPE_PORT, baudrate=9600)
            self._buffer = bytearray()
        except Exception as exc:
            self._ser = None

        self._fmt = "h"
        self._packet_size = struct.calcsize(self._fmt)
        self.data_x: deque[float] = deque(maxlen=max_len)
        self.data_y: deque[int] = deque(maxlen=max_len)

    @property
    def connected(self) -> bool:
        return self._ser is not None
    
    def read(self) -> tuple[list, list] | None:
        if self.connected:
            fmt = self._fmt
            packet_size = self._packet_size
            buffer = self._buffer
            data_x = self.data_x
            data_y = self.data_y
            ser = cast(serial.Serial, self._ser)

            if ser.in_waiting:
                buffer.extend(ser.read(ser.in_waiting))           
            
            while len(buffer) >= packet_size:
                packet, buffer = buffer[:packet_size], buffer[packet_size:]
                data_x.append(time.time())
                data_y.append(struct.unpack(fmt, packet)[0])
                self._buffer = buffer

            return list(data_x), list(data_y)
        else:
            return None



sensor_in = SensorIn(serial_port=CALLIOPE_PORT, baudrate=9600)

##########################


class SensorOut:

    def __init__(self, address: tuple[str, int] = ('localhost', 5005), debug: bool = True) -> None:
        self.address = address
        self.ip, self.port = address
        self.debug = debug

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.connected = False

        self._ongoing = False

    def connect(self):
        try:
            self._socket.bind(self.address)
            self.connected = True
            if self.debug:
                print(f"UDP server started on {SERVER_ADDRESS}.")
        except Exception as exc:
            if self.debug:
                print(f"UDP server failed to connect on {SERVER_ADDRESS}.")


    def send_hearbeat_event(self) -> None:
        self._socket.sendto(b"H", ("<broadcast>", self.port))
        if self.debug:
            print("Heartbeat detected.")

    def send_heartbeat_start_event(self, status: bool) -> None:
        "only send whenever the status goes from False to True"
        if status and not self._ongoing:
            self.send_hearbeat_event()            
        self._ongoing = status


        


            

    
# Create a UDP socket
SERVER_ADDRESS = ("localhost", 5005)  # You can replace 'localhost' with '' for any interface
sensor_out = SensorOut(address=SERVER_ADDRESS)
sensor_out.connect()



from controller import ControllerOut
CONTROLLER_SERVER_ADDRESS = ('localhost', 5006)
controller_out = ControllerOut(address=CONTROLLER_SERVER_ADDRESS)
controller_out.start()

# Start DearPyGUI App


dpg.create_context()



heartbeat_x = deque(maxlen=DEQUE_MAX_LEN)
heartbeat_y = deque(maxlen=DEQUE_MAX_LEN)
threshold = 50

sensor_in = SensorIn(serial_port=CALLIOPE_PORT, baudrate=9600, max_len=DEQUE_MAX_LEN)


def update_plot():
    reading = sensor_in.read()
    if reading is None:
        return
    updated_data_x, updated_data_y = reading
    dpg.configure_item('line', x=updated_data_x, y=updated_data_y)
    if dpg.get_value("auto_fit_checkbox"):
        dpg.fit_axis_data("xaxis")
    ####
    if len(updated_data_y) < 20:
        return
    to_filter = updated_data_y[-20:]
    coeffs = pywt.wavedec(to_filter, 'db4', level=4) 
    heartbeat_x.append(heartbeat_x[-1]+1 if heartbeat_x else 0)
    filtered_point = (np.std(coeffs[-1]) * 0.4)
    heartbeat_y.append(filtered_point.item())
    dpg.configure_item('filtered_line', x=list(heartbeat_x), y=list(heartbeat_y))
    dpg.fit_axis_data("filtered_xaxis")


    global threshold
    
    sensor_out.send_heartbeat_start_event(status= filtered_point >= threshold)
    ####

with dpg.window(label="Raw Heartbeat Signal"):
    with dpg.plot(height=400, width=500):
        dpg.add_plot_axis(dpg.mvXAxis, label="Time", tag="xaxis", time=True, no_tick_labels=True)
        dpg.add_plot_axis(dpg.mvYAxis, label="Amplitude", tag="yaxis")
        dpg.add_line_series([], [], tag='line', parent="yaxis")
    dpg.add_checkbox(label="Auto-fit x-axis limits", tag="auto_fit_checkbox", default_value=True)

# Filtered signal window
def set_threshold(sender):
    global threshold
    threshold = dpg.get_value(sender)



with dpg.window(label="Filtered Heartbeat Signal"):
    with dpg.plot(height=400, width=500, tag='filtered_plot'):
        dpg.add_plot_axis(dpg.mvXAxis, label="Time", tag="filtered_xaxis", time=True, no_tick_labels=True)
        dpg.add_plot_axis(dpg.mvYAxis, label="Filtered Amplitude", tag="filtered_yaxis")
        dpg.add_line_series([], [], tag='filtered_line', parent="filtered_yaxis")
        dpg.add_drag_line(label='Threshold', default_value=threshold, vertical=False, callback=set_threshold)


dpg.create_viewport(width=900, height=600, title='Updating plot data')
dpg.setup_dearpygui()
dpg.show_viewport()
while dpg.is_dearpygui_running():
    update_plot() 
    dpg.render_dearpygui_frame()
dpg.destroy_context()