import socket
import json
import time


# Example messages

# MOCK_SETTINGS = {"color": "BLUE", "brightness": 100, "sensitiivty": 50, "preset": None}

# MOCK_SETTINGS2 = {
#     "color": "RED",
#     "brightness": 75,
#     "sensitiivty": 100,
#     "preset": "running man",
# }

# MOCK_SETTINGS3 = {
#     "color": "PURPLE",
#     "brightness": 50,
#     "sensitiivty": 1,
#     "preset": "circle",
# }


class DisconnectedClientError(Exception):
    pass


class GUIClient:
    def __init__(self):
        # use `ifconfig en0`` or `ip r`` to find target ip
        self.host = ""  # The server's hostname or IP address
        self.port = 0  # The port used by the server
        self.connection = None

    def connect(self, host="", port=0):
        if host:
            self.host = host
        if port:
            self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.settimeout(10)
        self.connection.connect((self.host, self.port))

        if self._isSocketClosed():
            return

        # Loop to receive server name
        while True:
            data = self.connection.recv(1024)
            if data:
                server_name = json.loads(data)
                print(f"Connected to: {server_name}")
                return server_name

    def sendMessage(self, color, brightness, sensitivity):
        if not self._isSocketClosed():
            # TODO: Check each argument for correct syntax
            msg = {"color": color, "brightness": brightness, "sensitivity": sensitivity}
            msg_json = json.dumps(msg).encode("utf-8")
            print(f"Sending {msg_json}")
            self.connection.sendall(msg_json)
            data = self.connection.recv(1024)
            resp = json.loads(data)
            print(f"Received {resp}")

            return resp
        else:
            raise DisconnectedClientError()

    def disconnect(self):
        self.connection.close()

    def _isSocketClosed(self) -> bool:
        try:
            # this will try to read bytes without blocking and also without removing them from buffer (peek only)
            data = self.connection.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
            if len(data) == 0:
                return True
        except BlockingIOError:
            return False  # socket is open and reading from it would block
        except ConnectionResetError:
            return True  # socket was closed for some other reason
        except Exception as e:
            return False
        return False
