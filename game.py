import random
import pyxel
import socket

LISTEN_ADDRESS = ("", 5005)  # Match the server port

def create_udp_socket():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setblocking(False)
    client_socket.bind(LISTEN_ADDRESS)  # Bind so we can receive packets on this port
    print(f"UDP client listening on {LISTEN_ADDRESS}.")
    return client_socket

def check_for_heartbeat_from_server(socket: socket.socket) -> bool:
    try:
        data, addr = socket.recvfrom(1024)  # 1 KB buffer
        print(f"Client: received {data} from {addr}")
        return True
    except BlockingIOError:
        return False
        


def add_heart(hearts: list[dict]):
    hearts.append(dict(x=game['x'] + 140, y=0, big=False))


client_socket = create_udp_socket()

SCREEN_WIDTH = 160
SCREEN_HEIGHT = 80
ROTATE_SCREEN = False
pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="iBOT Wants a Heart", fps=60, quit_key=pyxel.KEY_ESCAPE)

# Art Assets
pyxel.load('assets.pyxres')
heart_img = dict(img=0, u=16, v=0, w=8, h=8, colkey=0)
bigheart_img = dict(img=0, u=16, v=8, w=8, h=8, colkey=0)
ground_img = dict(img=0, u=24, v=0, w=8, h=8, colkey=0)
robot_img = dict(img=0, u=0, v=0, w=16, h=16, colkey=0, rotate=0)
cloud_img = dict(img=0, u=32, v=0, w=16, h=16, colkey=0)

# Game State
game = dict(x=0, y_pos = 0, y_vel = 0, gravity = 0.2, strength = 4, score = 0, hearts=[], clouds=[])


def update():
    global ROTATE_SCREEN
    rotate_button_pressed = pyxel.btnp(pyxel.KEY_R)
    if rotate_button_pressed:
        ROTATE_SCREEN = not ROTATE_SCREEN

    game['x'] += 1
    if game['y_pos'] == 0 and (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)):
        game['y_vel'] = 4
    if game['y_pos'] >= 0:
        game['y_vel'] -= game['gravity']
        game['y_pos'] += game['y_vel']
    if game['y_pos'] < 0:
        game['y_pos'] = 0
        game['y_vel'] = 0

    heart_button_pressed = pyxel.btnp(pyxel.KEY_H) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y)
    heart_signal_received = check_for_heartbeat_from_server(socket=client_socket)

    if heart_button_pressed or heart_signal_received:
        add_heart(hearts=game['hearts'])

    if game['hearts'] and game['y_pos'] > 30:
        for heart in game['hearts']:
            if heart['big']:
                continue
            rel_heart_pos = game['hearts'][0]['x'] - game['x']
            if -10 < rel_heart_pos < 10:
                game['score'] += 1
                game['hearts'] = game['hearts'][1:]

    for heart in game['hearts']:
        if heart['x'] < game['x'] - 25:
            game['hearts'].remove(heart)

    if random.random() < .004:
        game['clouds'].append(dict(x=160, y=random.randint(15, 30)))

    
    
    for cloud in game['clouds']:
        cloud['x'] -= 0.2

    # If two hearts are too close together, they should join like bubbles and float up out of reach.
    if len(game['hearts']) > 1:
        for heart1, heart2 in zip(game['hearts'][:-1], game['hearts'][1:]):
            if heart1['big'] or heart2['big']:
                continue
            if abs(heart2['x'] - heart1['x']) < 23:
                heart1['x'] += 1
                heart2['y'] -= 1
            if abs(heart2['x'] - heart1['x']) < 5:
                game['hearts'].remove(heart1)
                heart2['big'] = True

    for heart in game['hearts']:
        if heart['big']:
            heart['y'] += 0.3
            heart['x'] += 0.1


def blit(**kwargs):
    if ROTATE_SCREEN:
        assert 'x' in kwargs
        assert 'y' in kwargs
        kwargs = kwargs.copy()

        kwargs['rotate'] = 180
        kwargs['x'] = SCREEN_WIDTH - kwargs['x'] - kwargs['w']
        kwargs['y'] = SCREEN_HEIGHT - kwargs['y'] - kwargs['h']

    pyxel.blt(**kwargs)

def text(**kwargs):
    ...  # don't show text, since we can't rotate it.


def draw():
    pyxel.cls(6)

    # Move Ground
    x_offset = game['x'] % 8
    for x in range(0, 168, 8):
        blit(x=x-x_offset, y=80-8, **ground_img)
    
    # Move Clouds
    for cloud in game['clouds']:
        blit(**(cloud_img | cloud))

    
    # Move Hearts
    for heart_obj in game['hearts']:
        x = 16 + (heart_obj['x'] - game['x'])
        if heart_obj['big']:
            blit(x=x, y=30-heart_obj['y'], **bigheart_img)
        else:
            blit(x=x, y=30, **heart_img)


    blit(x=16, y=58 - round(game['y_pos']), **robot_img)
    text(x=4, y=10, s=f"Heartbeats Collected: {game['score']}", col=1)    


pyxel.run(update, draw)