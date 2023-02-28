import socket
import json
import time
import re
from enum import Enum
import tqdm
import os

# Example messages

# MOCK_SETTINGS = {"color": "BLUE", "brightness": 100, "sensitiivty": 50, "preset": None}

# example_msg = {
#     "id": self.msg_id,
#     "data": {
#         "color": color,
#         "brightness": brightness,
#         "sensitivity": sensitivity,
#     },
# }


class InvalidMessageEnum(Enum):
    INVALID_COLOR = "INVALID_COLOR"
    INVALID_BRIGHTNESS = "INVALID_BRIGHTNESS"
    INVALID_SENSITIVITY = "INVALID_SENSITIVITY"


class DisconnectedClientError(Exception):
    pass


class InvalidMessageError(Exception):
    def __init__(self, error_enum: InvalidMessageEnum):
        super().__init__(error_enum)


class GUIClient:
    def __init__(self):
        # use `ifconfig en0`` or `ip r`` to find target ip
        self.host = ""  # The server's hostname or IP address
        self.port = 0  # The port used by the server
        self.connection = None
        self.msg_id = 0
        self.SEPARATOR = "<SEPARATOR>"
        self.BUFFER_SIZE = 4096

    def connect(self, host="", port=0):
        if host:
            self.host = host
        if port:
            self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.connection.settimeout(10)
        self.connection.connect((self.host, self.port))

        # Loop to receive server name
        while True:
            data = self.connection.recv(self.BUFFER_SIZE)
            if data:
                server_name = data.decode()
                print(f"Connected to: {server_name}")
                return server_name

    def sendSettingsMessage(self, color, brightness, sensitivity):
        if not self._isSocketClosed():
            # TODO: Check each argument for correct syntax
            if not self._isValidHexaColor(color):
                raise InvalidMessageError(InvalidMessageEnum.INVALID_COLOR)

            if type(brightness) != int or brightness < 0 or brightness > 100:
                raise InvalidMessageError(InvalidMessageEnum.INVALID_BRIGHTNESS)

            if type(sensitivity) != int or sensitivity < 0 or sensitivity > 100:
                raise InvalidMessageError(InvalidMessageEnum.INVALID_SENSITIVITY)

            msg = {
                "id": self.msg_id,
                "data": {
                    "color": color,
                    "brightness": brightness,
                    "sensitivity": sensitivity,
                },
            }
            self._sendMessage(msg)
            self.msg_id += 1

            return
        else:
            raise DisconnectedClientError()

    def sendFileMessage(self, filename):
        if not self._isSocketClosed():
            filesize = os.path.getsize(filename)
            self._sendMessage(f"{filename}{self.SEPARATOR}{filesize}")

            progress = tqdm.tqdm(
                range(filesize),
                f"Sending {filename}",
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            )
            with open(filename, "rb") as f:
                while True:
                    bytes_read = f.read(self.BUFFER_SIZE)
                    if not bytes_read:
                        break
                    self._sendMessage(bytes_read)
                    progress.update(len(bytes_read))
            return
        else:
            raise DisconnectedClientError()

    def _sendMessage(self, message):
        if type(message) == str:
            print("Sending: ", message)
            msg_encoded = message.encode("utf-8")
            self.connection.sendall(msg_encoded)
        elif type(message) == bytes:
            self.connection.sendall(message)
        else:
            print("Sending: ", message)
            self.connection.sendall(json.dumps(message).encode("utf-8"))

    def _receiveMessage(self):
        data = self.connection.recv(self.BUFFER_SIZE)
        resp = json.loads(data)
        print(f"Received {resp}")
        return resp

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

    def _isValidHexaColor(self, str):
        regex = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"

        p = re.compile(regex)

        if str == None:
            return False

        if re.search(p, str):
            return True
        else:
            return False


if __name__ == "__main__":
    client = GUIClient()
    resp = client.connect("127.0.0.1", 5000)
    print(resp)
