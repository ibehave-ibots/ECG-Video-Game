import pyxel


pyxel.init(160, 80, title="iBOT Wants a Heart", fps=60, quit_key=pyxel.KEY_ESCAPE)

pyxel.load('assets.pyxres')

heart = dict(img=0, u=16, v=0, w=8, h=8, colkey=0)
ground = dict(img=0, u=24, v=0, w=8, h=8, colkey=0)
robot = dict(img=0, u=0, v=0, w=16, h=16, colkey=0)

game = dict(
    x = 0,
    y_pos = 0,
    y_vel = 0,
    gravity = 0.2,
    strength = 4,
    score = 0,
)

hearts = []
def make_heart():
    global hearts
    global game
    heart = dict(x=game['x'] + 100, y=20)
    hearts.append(heart)



def update():
    game['x'] += 1
    if game['y_pos'] == 0 and pyxel.btnp(pyxel.KEY_SPACE):
        game['y_vel'] = 4
        print('jump')
    if game['y_pos'] >= 0:
        game['y_vel'] -= game['gravity']
        game['y_pos'] += game['y_vel']
    if game['y_pos'] < 0:
        game['y_pos'] = 0
        game['y_vel'] = 0

    if pyxel.btnp(pyxel.KEY_H):
        make_heart()

    global hearts
    if hearts and game['y_pos'] > 30 and -10 < (hearts[0]['x'] - game['x']) < 10:
        print('score!')
        game['score'] += 1
        hearts = hearts[1:]

def draw():
    pyxel.cls(6)
    x_offset = game['x'] % 8
    for x in range(0, 168, 8):
        pyxel.blt(x=x-x_offset, y=80-8, **ground)

    for heart_obj in hearts:
        pyxel.blt(x=16 + (heart_obj['x'] - game['x']), y=30, **heart)


    pyxel.blt(x=16, y=58 - round(game['y_pos']), **robot)
    
    


pyxel.run(update, draw)