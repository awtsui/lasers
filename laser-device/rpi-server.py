import socket
import json

# use ifconfig en0 to find target ip
SERVER_NAME = "RPi_1"
HOST = socket.gethostname()
print("Hostname: ", HOST)
PORT = 5000


def handle_client_msg(conn, msg):
    print(f"Handling {msg}")
    if msg:
        conn.sendall(b"200")


def send_msg(conn, msg):
    print(f"Sending {msg}")
    conn.sendall(msg)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind((HOST, PORT))
    sock.listen()
    while True:
        conn, addr = sock.accept()
        try:
            print(f"Connected by {addr}")
            send_msg(conn, json.dumps(SERVER_NAME).encode("utf-8"))
            while True:
                data = conn.recv(1024)
                if data:
                    handle_client_msg(conn, data)
                else:
                    break
        finally:
            print("Closing current connection")
            conn.close()
