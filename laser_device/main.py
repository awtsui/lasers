from server import run_server
from analyzer import run_analyzer
from queue import Queue
import threading
import time
from laser_control import run_master_galvo_laser_thread

# SETTINGS: TYPES OF MSGS
# new file

if __name__ == "__main__":
    client_settings_queue = Queue()  # Settings (dict)
    laser_control_settings_queue = Queue()
    features_queue = Queue()  # Strongest frequencies (int)
    files_queue = Queue()
    analyzer_settings_queue = Queue()

    # OUT: client_settings & files
    thread_server = threading.Thread(
        target=run_server, args=[client_settings_queue, files_queue], name="LAN-Server"
    )
    thread_server.daemon = True

    # IN: analyzer_settings
    # OUT: features_queue
    thread_analyzer = threading.Thread(
        target=run_analyzer,
        args=[features_queue, analyzer_settings_queue],
        name="Read Time Audio Processing",
    )
    thread_analyzer.daemon = True

    # IN: files, laser_control_settings, features
    thread_galvo_laser = threading.Thread(
        target=run_master_galvo_laser_thread,
        args=[files_queue, laser_control_settings_queue, features_queue],
        name="Galvos and Laser Control",
    )
    thread_galvo_laser.daemon = True

    thread_server.start()
    thread_analyzer.start()
    thread_galvo_laser.start()

    while True:
        if not client_settings_queue.empty():
            client_settings = client_settings_queue.get()
            analyzer_settings_queue.put(client_settings["data"]["sensitivity"])
            laser_control_settings_queue.put(client_settings["data"])
        time.sleep(1)
