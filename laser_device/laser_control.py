from __future__ import absolute_import, division, print_function, unicode_literals

import time
import os
from ilda import *
import threading

try:
    from ADCDACPi import ADCDACPi
except ImportError:
    print("Failed to import ADCDACPi from python system path")
    print("Importing from parent folder instead")
    try:
        import sys

        sys.path.append("..")
        from ADCDACPi import ADCDACPi
    except ImportError:
        raise ImportError("Failed to import library from parent folder")

BASS_FREQ_UPPER = 200
HIGH_FREQ_LOWER = 5000
FPS = 60


def decode_color(hex):
    hex_striped = hex.lstrip("#")
    return tuple(int(hex_striped[i : i + 2], 16) for i in (0, 2, 4))


def run_galvo(dac, x, y, z):
    dac.set_dac_raw(1, x)
    dac.set_dac_raw(2, y)


# TODO: this is to change laser color, turn on and off
def run_laser(color, brightness, on):
    pass


def run_galvo_and_laser(stop, file, settings, features):
    """
    Main program function
    """

    # Laser settings
    brightness = 0
    color = (0, 0, 0)
    specified_color = False

    # DAC Setup
    adcdac = ADCDACPi(2)  # 0 - 4.096 V

    # TODO: RGB Laser Setup

    f = open(file, "rb")
    show = [t for t in readFrames(f)]

    while not stop():
        for table in show:
            # kill thread if flagged
            if stop():
                break

            # TODO: Check queues for updates
            if not settings.empty():
                setting = settings.get()
                # TODO: include setting to reset color to ilda file
                specified_color = False

                brightness, color = (
                    setting["brightness"],
                    decode_color(setting["color"]),
                )

            if not features.empty():
                # print(features.get())
                feature = features.get()
                if feature <= BASS_FREQ_UPPER:
                    print(f"WE HAVE BASSSSS @ {feature}")
                elif feature >= HIGH_FREQ_LOWER:
                    print(f"WE HAVE HIGH PITCH @ {feature}")

            # TODO: define function that applies feature to coordinates (expand or minimize)
            last_update = time.time()

            if (time.time() - last_update) > (1.0 / FPS):
                for point in table.iterPoints():
                    # run_galvo(adcdac, point.x, point.y, point.z)
                    # run_laser(color, brightness, not point.blanking)
                    # print(point)
                    pass
            else:
                try:
                    time.sleep(((1.0 / FPS) - (time.time() - last_update)) * 0.95)
                except:
                    continue


def run_master_galvo_laser_thread(files, settings, features):
    galvo_laser_thread = None
    stop_thread = False

    while True:
        if not files.empty():
            file = files.get()

            if galvo_laser_thread and galvo_laser_thread.is_alive():
                print(f"Killing {galvo_laser_thread.getName()} ...")
                stop_thread = True
                galvo_laser_thread.join()

            with features.mutex:
                features.queue.clear()
                features.all_tasks_done.notify_all()
                features.unfinished_tasks = 0

            stop_thread = False
            galvo_laser_thread = threading.Thread(
                target=run_galvo_and_laser,
                args=[lambda: stop_thread, file, settings, features],
                name=f"Galvo and Laser Show: {file}",
            )
            galvo_laser_thread.daemon = True
            galvo_laser_thread.start()
            print(f"Starting  {galvo_laser_thread.getName()}")
        time.sleep(1)
