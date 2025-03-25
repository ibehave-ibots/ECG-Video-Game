from dataclasses import dataclass
from math import sin
import random
from statistics import mean
import time
import pyxel
import numpy as np
from scipy.signal import savgol_filter
from scipy.interpolate import CubicSpline


class LineDrawTool:

    def __init__(self, x_min: int, x_max: int, default_y: int):
        self.x_min = x_min
        self.x_max = x_max
        self.last_x = None
        self.default_y = default_y
        self.reset()

    def reset(self):
        self.line = [self.default_y] * (self.x_max - self.x_min)
        self.line_filtered = self.line.copy()

    def start_recording(self, x: int, y: int) -> None:
        self.line[x] = y
        last_x = self.last_x
        if last_x is not None:
            x0, x1 = (x, last_x) if x < last_x else (last_x, x)
            for _x in range(x0, x1):
                self.line[_x] = y
        self.last_x = x

    def stop_recording(self) -> None:
        self.last_x = None

    def update_filtered_line(self) -> None:
        self.line_filtered = savgol_filter(self.line, window_length=9, polyorder=1).tolist()

    def get_upsampled(self, spacing: float = .1) -> np.array:
        line = self.line_filtered
        interp = CubicSpline(x = np.arange(len(line)), y=line)
        return interp(np.arange(0, len(line), spacing))


screen_width = 150
line_draw_tool = LineDrawTool(x_min=0, x_max=screen_width, default_y=int(screen_width // 2))


def update():
    if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
        global last_x
        x, y = pyxel.mouse_x, pyxel.mouse_y
        if x > screen_width:
            x = screen_width
        elif x < 0:
            x = 0
        x = x-1  # convert to 0-index
        line_draw_tool.start_recording(x=x, y=y)
    else:
        line_draw_tool.stop_recording()

    line_draw_tool.update_filtered_line()

    if pyxel.btnp(pyxel.KEY_SPACE):
        line_draw_tool.reset()
        
    


def draw():
    pyxel.cls(col=7)

    # Drawing area
    pyxel.rect(x=0, y=30, w=200, h=100, col=5)
    for x, point in enumerate(line_draw_tool.line_filtered):
        pyxel.pset(x=x, y=point, col=0)

    new_line = line_draw_tool.get_upsampled(spacing=3).tolist() * 3
    for x, point in enumerate(new_line[:]):
        pyxel.pset(x=x, y=(point-75)/3 + 15, col=15)

    

pyxel.init(width=screen_width, height=150, title="Draw an ECG Wave!", quit_key=pyxel.KEY_ESCAPE, fps=60)
pyxel.mouse(True)


pyxel.run(update, draw)
