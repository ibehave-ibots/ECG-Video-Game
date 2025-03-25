from dataclasses import dataclass
from math import sin
import random
from statistics import mean
import time
import pyxel
import numpy as np



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
        self.line_filtered[x] = y
        last_x = self.last_x
        if last_x is not None:
            x0, x1 = (x, last_x) if x < last_x else (last_x, x)
            for _x in range(x0, x1):
                self.line[_x] = y
                self.line_filtered[_x] = y
        self.last_x = x

    def stop_recording(self) -> None:
        self.last_x = None

    # def update_filtered_line(self) -> None:
    #     running_window_width = 6
    #     half_width = int(running_window_width / 2)
    #     for idx in range(half_width - 1, len(line) - half_width):
    #         line_filtered[idx] = int(sum(line[idx-half_width:idx+half_width]) / (half_width * 2))
    #     self.last_x = None




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

    if pyxel.btnp(pyxel.KEY_SPACE):
        line_draw_tool.reset()
        
    


def draw():
    pyxel.cls(col=7)

    # Drawing area
    pyxel.rect(x=0, y=30, w=200, h=100, col=5)
    for x, point in enumerate(line_draw_tool.line):
        pyxel.pset(x=x, y=point, col=0)

    

pyxel.init(width=screen_width, height=150, title="Draw an ECG Wave!", quit_key=pyxel.KEY_ESCAPE, fps=60)
pyxel.mouse(True)


pyxel.run(update, draw)
