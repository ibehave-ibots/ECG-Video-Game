from collections import deque
from dataclasses import dataclass
from math import sin
import random
import socket
from statistics import mean
import struct
import time
from typing import Callable, Sequence
import pyxel
import numpy as np
from scipy.signal import savgol_filter
from scipy.interpolate import CubicSpline

"""
Code snippets:
self.line_filtered = savgol_filter(self.line, window_length=9, polyorder=1).tolist()

curr_point, to_send = daq.send(line_draw_tool.get_upsampled(spacing=.01))
print(to_send)
packet = struct.pack('H'*len(to_send), *to_send)
server_socket.sendto(packet, ("<broadcast>", PORT))
"""


    

# def daq_simulator(data: list, samprate=100):
#     last_t = time.time()
#     last_x = 0
#     while True:
#         curr_t = time.time()
#         n_samps = int(round((curr_t - last_t) * samprate / .01))
#         to_x = last_x + n_samps
#         data_to_send = (data * 2)[last_x:to_x]
#         last_x = len(data) - to_x if to_x >= len(data) else to_x
#         last_t = curr_t
#         data = yield to_x, data_to_send
            

# # Create a UDP socket
# def create_udp_server(ip: str, port: int) -> socket.socket:
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#     server_socket.bind((ip, port))
#     print(f"UDP server started on {(ip, port)}.")
#     return server_socket


# PORT = 5006
# # daq = daq_simulator(line_draw_tool.get_upsampled(spacing=.1), samprate=5)
# # next(daq)
# server_socket = create_udp_server(ip='localhost', port=PORT)


def generate_hb_fun(drawn_points: dict[int, int], baseline: int) -> Callable:
    if len(drawn_points) > 2:
        # Make data converge to baseline
        points = drawn_points.copy()
        for x in (-40, -30, -23, -17, -11, -8, -5, -4, -3, -2, -1, 151, 152, 153, 154, 155, 158, 161, 167, 173, 180, 190):
            points[x] = baseline

        x, y = zip(*list(sorted(points.items())))
        interp_fun = CubicSpline(x=x, y=y)
        return interp_fun
    else:
        return lambda x: [baseline] * len(x)
        

def get_sample(t, fun, samprate=100) -> float:
    x = ((t * 100) % (150 * 2)) - 75
    return fun([x])


drawn_points = {}
baseline_y = 100
last_x = None
hb_fun = generate_hb_fun(drawn_points=drawn_points, baseline=baseline_y)
outputted_data = deque([], maxlen=150)

def update():
    global last_x
    if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
        mouse_x = pyxel.mouse_x
        drawn_points[mouse_x] = pyxel.mouse_y
        if last_x is not None and abs(mouse_x - last_x) >= 2:
            for x in range(min(mouse_x, last_x) + 1, max(mouse_x, last_x)):
                if x in drawn_points:
                    del drawn_points[x]
        last_x = mouse_x
    else:
        last_x = None

        

    if pyxel.btnp(pyxel.KEY_SPACE):  # reset
        drawn_points.clear()

    global hb_fun
    hb_fun = generate_hb_fun(drawn_points=drawn_points, baseline=baseline_y)
            
    ys = get_sample(t=time.time(), fun=hb_fun)
    outputted_data.extend(ys)
    
    



def draw():
    pyxel.cls(col=7)

    # Drawing area
    pyxel.rect(x=0, y=30, w=200, h=100, col=5)
    pyxel.line(x1=0, x2=150, y1=baseline_y, y2=baseline_y, col=3)

    # Draw generated line
    hb_points = hb_fun(x=list(range(150)))
    for x, y in enumerate(hb_points, start=1):
        pyxel.pset(x=x, y=y, col=12)

    # Draw inputted-points
    for x, y in drawn_points.items():
        pyxel.pset(x=x, y=y, col=0)


    # Draw Full outputted-line
    for x, y in enumerate(outputted_data, start=1):
        pyxel.pset(x=x, y=y - 20, col=2)

    




    
    

pyxel.init(width=150, height=150, title="Draw an ECG Wave!", quit_key=pyxel.KEY_ESCAPE, fps=60)
pyxel.mouse(True)


pyxel.run(update, draw)
