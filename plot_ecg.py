import dearpygui.dearpygui as dpg
import math
import time
import numpy as np
import pywt
import random
from collections import deque

import serial
import struct


fmt = "h"
packet_size = struct.calcsize(fmt)
buffer = bytearray()
ser = serial.Serial('COM3', baudrate=9600)


dpg.create_context()

DEQUE_MAX_LEN = 200
data_x = deque(maxlen=DEQUE_MAX_LEN)
data_y = deque(maxlen=DEQUE_MAX_LEN)
heartbeat_x = deque(maxlen=DEQUE_MAX_LEN)
heartbeat_y = deque(maxlen=DEQUE_MAX_LEN)
event_x = deque(maxlen=DEQUE_MAX_LEN)
event_y = deque(maxlen=DEQUE_MAX_LEN)
thresohld = 50

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
    detail_coeffs = coeffs[-1]
    heartbeat_x.append(heartbeat_x[-1]+1 if heartbeat_x else 0)
    heartbeat_y.append((np.std(detail_coeffs) * 0.4).item())
    dpg.configure_item('filtered_line', x=list(heartbeat_x), y=list(heartbeat_y))
    dpg.fit_axis_data("filtered_xaxis")
    ####

with dpg.window():
    with dpg.plot(height=400, width=500):
        dpg.add_plot_axis(dpg.mvXAxis, label="Time", tag="xaxis", time=True, no_tick_labels=True)
        dpg.add_plot_axis(dpg.mvYAxis, label="Amplitude", tag="yaxis")
        dpg.add_line_series([], [], tag='line', parent="yaxis")
        # dpg.set_axis_limits("yaxis", -1.5, 1.5)
    dpg.add_checkbox(label="Auto-fit x-axis limits", tag="auto_fit_checkbox", default_value=True)

# Filtered signal window
def set_threshold(sender):
    global thresohld
    thresohld = dpg.get_value(sender)



with dpg.window(label="Filtered Heartbeat Signal"):
    with dpg.plot(height=400, width=500, tag='filtered_plot'):
        dpg.add_plot_axis(dpg.mvXAxis, label="Time", tag="filtered_xaxis", time=True, no_tick_labels=True)
        dpg.add_plot_axis(dpg.mvYAxis, label="Filtered Amplitude", tag="filtered_yaxis")
        dpg.add_line_series([], [], tag='filtered_line', parent="filtered_yaxis")#, color=(0, 255, 0, 255))
        # dpg.add_inf_line_series([], tag='event_det', parent='filtered_yaxis')
        dpg.add_drag_line(label='Threshold', default_value=thresohld, vertical=False, callback=set_threshold)


dpg.create_viewport(width=900, height=600, title='Updating plot data')
dpg.setup_dearpygui()
dpg.show_viewport()
while dpg.is_dearpygui_running():
    update_plot() # updating the plot directly from the running loop
    dpg.render_dearpygui_frame()
dpg.destroy_context()