import socket
import time

def udp_server():
    SERVER_ADDRESS = ("localhost", 5005)  # You can replace 'localhost' with '' for any interface

    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    

    # Bind, though for sending only it is sometimes optional on localhost
    server_socket.bind(SERVER_ADDRESS)

    print(f"UDP server started on {SERVER_ADDRESS}. Sending 'H' every 2 seconds...")
    
    while True:
        # In UDP, you need an address to send to. 
        # If you want to broadcast, use ('<broadcast>', 5005) with SO_BROADCAST.
        # For a local test, you can just send to the server's own address & port.
        server_socket.sendto(b"H", ("<broadcast>", 5005))
        # server_socket.sendto(b"H", SERVER_ADDRESS)
        print("Server: sent 'H'")
        time.sleep(2)

if __name__ == "__main__":
    udp_server()
