import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import socket
import struct
import threading
import time

import pygame



buttons = ['A', 'B', '', 'Y', 'X', '', '', '', '', '', '', '', '', '', '']



class ControllerOut:

    def __init__(self, address: tuple[str, int] = ('localhost', 5006)) -> None:
        self.address = address
        self.ip, self.port = address
        self.state = None

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._socket.bind(address)
        print(f"Controller UDP server started on {address}.")
        
    
    def start(self):
        def controller_loop(sock, port):
            pygame.init()
            pygame.joystick.init()

            if pygame.joystick.get_count() == 0:
                raise RuntimeError("No controller found")
            else:
                print("controller found!")

            js = pygame.joystick.Joystick(0)
            js.init()

            shared_state = {}
            shared_state["axes"] = [js.get_axis(i) for i in range(js.get_numaxes())]
            shared_state["buttons"] = [js.get_button(i) for i in range(js.get_numbuttons())]
            while True:
                pygame.event.pump() 
                new_state = {}
                new_state["axes"] = [js.get_axis(i) for i in range(js.get_numaxes())]
                new_state["buttons"] = [js.get_button(i) for i in range(js.get_numbuttons())]
                new_state["buttons_pressed"] = [int(curr_pressed and not was_pressed) for curr_pressed, was_pressed in zip(new_state['buttons'], shared_state['buttons'])]
                new_state["buttons_released"] = [int(not curr_pressed and was_pressed) for curr_pressed, was_pressed in zip(new_state['buttons'], shared_state['buttons'])]
                shared_state.update(new_state)
                if any(shared_state['buttons_pressed']):
                    button_name = buttons[shared_state['buttons_pressed'].index(1)]
                    if button_name:
                        sock.sendto(button_name.encode('ascii'), ("<broadcast>", 5006))
                        print(button_name)
                    
                time.sleep(0.01)  # ~100 Hz

        
        thread = threading.Thread(target=controller_loop, args=(self._socket, self.address[1]), daemon=True)
        thread.start()

    
    



def send_controller_state():
    fmt = "h"
    packet_size = struct.calcsize(fmt)
    buffer = bytearray()
    if any(shared['buttons_pressed']):
        ...
    





if __name__ == '__main__':

    controller = ControllerOut()
    controller.start()
    while True:
        time.sleep(.05)