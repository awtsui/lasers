import socket
import json
import os
from dotenv import load_dotenv

load_dotenv()

print("Server Name: ", os.environ.get("SERVER_NAME"))

# TODO: Require SERVER_NAME in .env
# use ifconfig en0 to find target ip
HOST = "127.0.0.1"
print("Hostname: ", HOST)
PORT = 5000
print("Port: ", PORT)


def handle_client_msg(conn, msg):
    print(f"Handling {msg}")
    if msg:
        conn.sendall(b"200")


def send_msg(conn, msg):
    print(f"Sending {msg}")
    conn.sendall(msg)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen()
    while True:
        conn, addr = sock.accept()
        try:
            print(f"Connected by {addr}")
            send_msg(conn, json.dumps(os.environ["SERVER_NAME"]).encode("utf-8"))
            while True:
                data = conn.recv(1024)
                if data:
                    handle_client_msg(conn, data)
                else:
                    break
        finally:
            print("Closing current connection")
            conn.close()
