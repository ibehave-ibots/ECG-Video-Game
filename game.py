import pyxel


pyxel.init(160, 80, title="iBOT Wants a Heart", fps=60, quit_key=pyxel.KEY_ESCAPE)

pyxel.load('assets.pyxres')

heart = dict(img=0, u=16, v=0, w=8, h=8, colkey=0)
ground = dict(img=0, u=24, v=0, w=8, h=8, colkey=0)
robot = dict(img=0, u=0, v=0, w=16, h=16, colkey=0)

player = dict(x=0)


def update():
    player['x'] += 1

def draw():
    pyxel.cls(6)
    for x in range(0, 160, 8):
        pyxel.blt(x=x, y=80-8, **ground)

    pyxel.blt(x=120, y=40, **heart)

    pyxel.blt(x=16, y=58, **robot)
    


pyxel.run(update, draw)