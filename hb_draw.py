import time
import pyxel
import numpy as np

screen_width = 150
line = [int(screen_width // 2)] * screen_width
line_filtered = line.copy()
last_x = None
output_buffer = [0] * screen_width
current_time = time.time()


def update():
    if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
        global last_x
        x, y = pyxel.mouse_x, pyxel.mouse_y
        x = x-1  # convert to 0-index
        line[x] = y
        line_filtered[x] = y
        if last_x is not None:
            x0, x1 = (x, last_x) if x < last_x else (last_x, x)
            print(x0, x1)
            for _x in range(x0, x1):
                line[_x] = y
                line_filtered[_x] = y

        last_x = x
    elif last_x is not None:
        running_window_width = 6
        half_width = int(running_window_width / 2)
        for idx in range(half_width - 1, len(line) - half_width):
            line_filtered[idx] = int(sum(line[idx-half_width:idx+half_width]) / (half_width * 2))
        last_x = None

    if pyxel.btnp(pyxel.KEY_SPACE):
        reset_y = int(screen_width // 2)
        for idx in range(len(line)):
            line[idx] = reset_y
            line_filtered[idx] = reset_y
        

            

        
    


def draw():
    pyxel.cls(col=7)

    # Drawing area
    pyxel.rect(x=0, y=30, w=200, h=100, col=5)
    for x, point in enumerate(line_filtered):
        pyxel.pset(x=x, y=point, col=0)

    # Output Area
    curr_out = (time.time() * 75) % screen_width
    pyxel.line(x1=curr_out, x2=curr_out, y1=2, y2=28, col=10)

    for x, point in enumerate(output_buffer):
        pyxel.pset(x=x, y=point+15, col=2)

    

pyxel.init(width=screen_width, height=150, title="Draw an ECG Wave!", quit_key=pyxel.KEY_ESCAPE, fps=60)
pyxel.mouse(True)


pyxel.run(update, draw)
