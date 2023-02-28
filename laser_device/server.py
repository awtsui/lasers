import socket
import json
import os
from dotenv import load_dotenv
import tqdm
from queue import Queue


class MissingEnvVariableError(Exception):
    pass


load_dotenv()

# example_msg = {
#     "id": self.msg_id,
#     "data": {
#         "color": color,
#         "brightness": brightness,
#         "sensitivity": sensitivity,
#     },
# }


# Server Settings
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
ILDA_FILES_PATH = "ilda-files/"
SERVER_NAME = os.environ.get("SERVER_NAME")
HOST = os.environ.get("HOST")
PORT = os.environ.get("PORT")


def handle_client_msg(conn, data, settings_queue: Queue):
    # TODO: check message validity
    if len(data.split(SEPARATOR)) == 2:
        filename, filesize = data.split(SEPARATOR)
        filename = os.path.basename(filename)
        filesize = int(filesize)
        download_file(conn, filename, filesize)
        print("Received file: ", filename)
    else:
        data_json = json.loads(data)
        settings_queue.put(data_json)
        print("Received settings: ", data_json)


def download_file(conn, filename, filesize):
    progress = tqdm.tqdm(
        range(filesize),
        f"Receiving {filename}",
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    )
    bytes_downloaded = 0
    with open(ILDA_FILES_PATH + filename, "wb") as f:
        while bytes_downloaded < filesize:
            bytes_read = conn.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            f.write(bytes_read)
            progress.update(len(bytes_read))
            bytes_downloaded += len(bytes_read)


def send_message(conn, message):
    if type(message) == str:
        conn.sendall(message.encode("utf-8"))
    elif type(message) == json:
        conn.sendall(json.dumps(message).encode("utf-8"))
    else:
        pass
    print("Sending: ", message)


def run_server(settings_queue: Queue):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, int(PORT)))
    sock.listen()

    print("Server Name: ", SERVER_NAME)
    print("Hostname: ", HOST)
    print("Port: ", PORT)
    while True:
        # Server persists indefinitely, constantly searching for new 1-on-1 connection
        conn, addr = sock.accept()
        try:
            print(f"Connected by {addr}")
            send_message(conn, SERVER_NAME)
            while True:
                data = conn.recv(BUFFER_SIZE).decode("utf-8")
                if data:
                    handle_client_msg(conn, data, settings_queue)
                else:
                    break
        finally:
            print("Closing current connection")
            conn.close()


if __name__ == "__main__":
    if not (SERVER_NAME and HOST and PORT):
        raise MissingEnvVariableError()

    run_server()
