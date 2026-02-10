import dearpygui.dearpygui as dpg
import math
import time
import numpy as np
import pywt
import random
from collections import deque

import serial
import struct
import socket


######## Parameters ######
CALLIOPE_PORT = 'COM5'

##########################

# Create a UDP socket
SERVER_ADDRESS = ("localhost", 5005)  # You can replace 'localhost' with '' for any interface
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server_socket.bind(SERVER_ADDRESS)
print(f"UDP server started on {SERVER_ADDRESS}.")


fmt = "h"
packet_size = struct.calcsize(fmt)
buffer = bytearray()
ser = serial.Serial(CALLIOPE_PORT, baudrate=9600)


dpg.create_context()

DEQUE_MAX_LEN = 500
data_x = deque(maxlen=DEQUE_MAX_LEN)
data_y = deque(maxlen=DEQUE_MAX_LEN)
heartbeat_x = deque(maxlen=DEQUE_MAX_LEN)
heartbeat_y = deque(maxlen=DEQUE_MAX_LEN)
event_x = deque(maxlen=DEQUE_MAX_LEN)
event_y = deque(maxlen=DEQUE_MAX_LEN)
threshold = 50
is_beating = False

def generate_data():
    global buffer
    if ser.in_waiting:
        buffer.extend(ser.read(ser.in_waiting))
    
    while len(buffer) >= packet_size:
        packet, buffer = buffer[:packet_size], buffer[packet_size:]
        data_x.append(time.time())
        data_y.append(struct.unpack(fmt, packet)[0])
    return list(data_x), list(data_y)

def update_plot():
    updated_data_x, updated_data_y = generate_data()
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
    global is_beating
    if filtered_point >= threshold:
        if not is_beating:
            print('Heartbeat detected')
            server_socket.sendto(b"H", ("<broadcast>", 5005))
            is_beating = True
    else:
        if is_beating:
            print('End of Heartbeat.')
            is_beating = False
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