from __future__ import absolute_import, division, print_function, unicode_literals

import time
import os
from ilda import *
import threading
import wiringpi
import signal
import sys

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



def run_galvo(dac, x, y, z, blanking, effect):
    # dac.set_dac_raw(1, x)
    # dac.set_dac_raw(2, y)
    dac.set_dac_raw(1, int(x*effect))
    dac.set_dac_raw(2, 4096 - int(y*effect))
    if blanking:
        wiringpi.digitalWrite(0, 0)
    else:
        wiringpi.digitalWrite(0, 1)


# TODO: this is to change laser color, turn on and off
def run_laser(color, brightness, on):
    pass


def run_galvo_and_laser(stop, files, settings, features):
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
    wiringpi.wiringPiSetup() 
    wiringpi.pinMode(0, 1)   

    f_norm = open(files[0], "rb")
    show_norm = [t for t in readFrames(f_norm)]

    f_bass = open(files[1], "rb")
    show_bass = [t for t in readFrames(f_bass)]

    while not stop():
        for table in show_norm:
            # kill thread if flagged
            if stop():
                break
            effect = 1
            if not features.empty():
                # print(features.get())
                feature = features.get()
                if feature <= BASS_FREQ_UPPER:
                    print(f"WE HAVE BASSSSS @ {feature}")
                    for table_bass in show_bass:
                        for point_b in table_bass.iterPoints():
                            run_galvo(adcdac, point_b.x, point_b.y, point_b.z, point_b.blanking, effect)
                elif feature >= HIGH_FREQ_LOWER:
                    print(f"WE HAVE HIGH PITCH @ {feature}")

            for point in table.iterPoints():
                run_galvo(adcdac, point.x, point.y, point.z, point.blanking, effect)

            # TODO: define function that applies feature to coordinates (expand or minimize)



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

def onInterrupt(sig, frame):
    wiringpi.digitalWrite(0,0)
    print("Turn off laser diode.")
    print("Program was interrupted.")
    sys.exit(0)

if __name__ == "__main__":
    from queue import Queue
    import threading

    adcdac = ADCDACPi(2)  # 0 - 4.096 V

    file = "./ilda-files/circle5.ild"

    files = Queue()
    settings = Queue()
    features= Queue()

    thread = threading.Thread(target=run_master_galvo_laser_thread, args=[files,settings, features])
    thread.daemon = True

    thread.start()

    signal.signal(signal.SIGINT, onInterrupt)
    files.put(("./ilda-files/smallcirc.ild", "./ilda-files/burst.ild"))

    feat = [1000,1000,1000,100,1000,1000,1000,1000,100,1000,1000]

    while True:
        # files.put("./ilda-files/smallcirc.ild")
        # time.sleep(3)
        # files.put("./ilda-files/medcirc.ild")
        # time.sleep(3)
        # files.put("./ilda-files/bigcirc.ild")
        time.sleep(5)

        # for f in feat:
        #     features.put(f)
        #     time.sleep(1.25)
        

        
