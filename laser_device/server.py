import socket
import json
import os
from dotenv import load_dotenv
import tqdm
from queue import Queue
import time


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


def handle_client_msg(conn, data, settings_queue: Queue, files_queue: Queue):
    # TODO: check message validity
    if len(data.split(SEPARATOR)) == 2:
        filename, filesize = data.split(SEPARATOR)
        filename = os.path.basename(filename)
        filesize = int(filesize)
        filepath = ILDA_FILES_PATH + filename
        download_file(conn, filepath, filesize)
        print("Received file: ", filename)
        files_queue.put(filepath)
    elif data.endswith(".ild"):
        filename = os.path.basename(data)
        filepath = ILDA_FILES_PATH + filename
        files_queue.put(filepath)
        print("Received show selection: ", data)
    else:
        data_json = json.loads(data)
        settings_queue.put(data_json)
        print("Received settings: ", data_json)


def download_file(conn, filepath, filesize):
    progress = tqdm.tqdm(
        range(filesize),
        f"Receiving {filepath}",
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    )
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, ILDA_FILES_PATH)

    if os.path.exists(path) and os.path.isdir(path):
        print("exists and is directory")
    else:
        os.mkdir(path)

    bytes_downloaded = 0
    with open(filepath, "wb") as f:
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
    elif type(message) == list:
        conn.sendall(str(message).encode("utf-8"))
    else:
        conn.sendall(json.dumps(message).encode("utf-8"))
    print("Sending: ", message)


def retrieve_ilda_files():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, ILDA_FILES_PATH)
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


def run_server(settings_queue: Queue, files_queue: Queue):
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

            # Send server name
            send_message(conn, SERVER_NAME)

            # Send list of saved ilda files
            send_message(conn, retrieve_ilda_files())

            while True:
                time.sleep(1)
                data = conn.recv(BUFFER_SIZE).decode("utf-8")
                if data:
                    handle_client_msg(conn, data, settings_queue, files_queue)
                else:
                    break
        finally:
            print("Closing current connection")
            conn.close()


if __name__ == "__main__":
    if not (SERVER_NAME and HOST and PORT):
        raise MissingEnvVariableError()

    run_server()
