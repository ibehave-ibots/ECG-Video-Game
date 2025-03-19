import socket
import time

def udp_client():
    # LISTEN_ADDRESS = ("localhost", 5005)  # Match the server port
    LISTEN_ADDRESS = ("", 5005)  # Match the server port

    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set non-blocking mode
    client_socket.setblocking(False)

    # Bind so we can receive packets on this port
    client_socket.bind(LISTEN_ADDRESS)
    print(f"UDP client listening on {LISTEN_ADDRESS} (non-blocking).")

    while True:
        try:
            data, addr = client_socket.recvfrom(1024)  # 1 KB buffer
            print(f"Client: received {data} from {addr}")
        except BlockingIOError:
            # No data available right now
            pass

        # Do other processing or just sleep briefly before checking again
        time.sleep(0.1)

if __name__ == "__main__":
    udp_client()
