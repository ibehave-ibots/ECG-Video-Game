import pyxel
import socket

LISTEN_ADDRESS = ("", 5005)  # Match the server port

def create_udp_socket():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setblocking(False)
    client_socket.bind(LISTEN_ADDRESS)  # Bind so we can receive packets on this port
    print(f"UDP client listening on {LISTEN_ADDRESS}.")
    return client_socket
client_socket = create_udp_socket()


pyxel.init(160, 80, title="iBOT Wants a Heart", fps=60, quit_key=pyxel.KEY_ESCAPE)

# Art Assets
pyxel.load('assets.pyxres')
heart_img = dict(img=0, u=16, v=0, w=8, h=8, colkey=0)
ground_img = dict(img=0, u=24, v=0, w=8, h=8, colkey=0)
robot_img = dict(img=0, u=0, v=0, w=16, h=16, colkey=0)

# Game State
game = dict(x=0, y_pos = 0, y_vel = 0, gravity = 0.2, strength = 4, score = 0, hearts=[])

def add_heart(hearts: list[dict]):
    hearts.append(dict(x=game['x'] + 140, y=20))



def update():
    game['x'] += 1
    if game['y_pos'] == 0 and (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)):
        game['y_vel'] = 4
        print('jump')
    if game['y_pos'] >= 0:
        game['y_vel'] -= game['gravity']
        game['y_pos'] += game['y_vel']
    if game['y_pos'] < 0:
        game['y_pos'] = 0
        game['y_vel'] = 0

    heart_button_pressed = pyxel.btnp(pyxel.KEY_H) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y)
    heart_signal_received = False
    try:
        data, addr = client_socket.recvfrom(1024)  # 1 KB buffer
        heart_signal_received = True
        print(f"Client: received {data} from {addr}")
    except BlockingIOError:
        pass  # No data available right now

    if heart_button_pressed or heart_signal_received:
        add_heart(hearts=game['hearts'])

    if game['hearts'] and game['y_pos'] > 30 and -10 < (game['hearts'][0]['x'] - game['x']) < 10:
        print('score!')
        game['score'] += 1
        game['hearts'] = game['hearts'][1:]

def draw():
    pyxel.cls(6)
    x_offset = game['x'] % 8
    for x in range(0, 168, 8):
        pyxel.blt(x=x-x_offset, y=80-8, **ground_img)

    for heart_obj in game['hearts']:
        pyxel.blt(x=16 + (heart_obj['x'] - game['x']), y=30, **heart_img)


    pyxel.blt(x=16, y=58 - round(game['y_pos']), **robot_img)
    pyxel.text(x=4, y=10, s=f"Heartbeats Collected: {game['score']}", col=1)    
    


pyxel.run(update, draw)