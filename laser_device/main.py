from server import run_server
from analyzer import run_analyzer
import multiprocessing
import time
import signal
from laser_control import run_master_galvo_laser_task, onInterrupt as onGalvoInterrupt

import wiringpi
import sys


def onInterrupt(sig, frame):
    onGalvoInterrupt(sig, frame)
    active = multiprocessing.active_children()
    for child in active:
        child.terminate()
    for child in active:
        child.join()
    print("Program interrupted")
    sys.exit(0)


if __name__ == "__main__":
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(0, 1)
    wiringpi.digitalWrite(0, 0)
    signal.signal(signal.SIGINT, onInterrupt)

    manager = multiprocessing.Manager()
    client_settings_queue = manager.Queue()  # Settings (dict)
    laser_control_settings_queue = manager.Queue()
    features_queue = manager.Queue()  # Strongest frequencies (int)
    files_queue = manager.Queue()
    analyzer_settings_queue = manager.Queue()
    active_show = manager.Value(value=False)

    # OUT: client_settings & files
    process_server = multiprocessing.Process(
        target=run_server,
        args=[client_settings_queue, files_queue, active_show],
        name="LAN-Server",
    )
    process_server.daemon = True

    # IN: analyzer_settings
    # OUT: features_queue
    process_analyzer = multiprocessing.Process(
        target=run_analyzer,
        args=[features_queue, analyzer_settings_queue],
        name="Read Time Audio Processing",
    )
    process_analyzer.daemon = True

    # IN: files, laser_control_settings, features
    process_galvo_laser = multiprocessing.Process(
        target=run_master_galvo_laser_task,
        args=[files_queue, laser_control_settings_queue, features_queue, active_show],
        name="Galvos and Laser Control",
    )
    process_galvo_laser.daemon = True

    process_server.start()
    process_analyzer.start()
    process_galvo_laser.start()

    while True:
        time.sleep(1)
        if not client_settings_queue.empty():
            client_settings = client_settings_queue.get()
            analyzer_settings_queue.put(client_settings["data"]["sensitivity"])
            laser_control_settings_queue.put(client_settings["data"])
