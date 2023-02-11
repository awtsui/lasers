import socket
import json
import time

# use ifconfig en0 to find target ip
HOST = "192.168.0.253"  # The server's hostname or IP address
PORT = 5000  # The port used by the server

MOCK_SETTINGS = {"color": "BLUE", "brightness": 100, "sensitiivty": 50, "preset": None}

MOCK_SETTINGS2 = {
    "color": "RED",
    "brightness": 75,
    "sensitiivty": 100,
    "preset": "running man",
}

MOCK_SETTINGS3 = {
    "color": "PURPLE",
    "brightness": 50,
    "sensitiivty": 1,
    "preset": "circle",
}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))

    # Loop to receive server name
    while True:
        data = sock.recv(1024)
        if data:
            print(f"Connected to: {json.loads(data)}")
            break

    # Sending client settings whenever updates are made
    msg = json.dumps(MOCK_SETTINGS).encode("utf-8")
    print(f"Sending {msg}")
    sock.sendall(msg)
    data = sock.recv(1024)
    print(f"Received {json.loads(data)}")
    time.sleep(2)

    msg = json.dumps(MOCK_SETTINGS2).encode("utf-8")
    print(f"Sending {msg}")
    sock.sendall(msg)
    data = sock.recv(1024)
    print(f"Received {json.loads(data)}")
    time.sleep(2)

    msg = json.dumps(MOCK_SETTINGS3).encode("utf-8")
    print(f"Sending {msg}")
    sock.sendall(msg)
    data = sock.recv(1024)
    print(f"Received {json.loads(data)}")
