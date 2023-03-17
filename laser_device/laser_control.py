from __future__ import absolute_import, division, print_function, unicode_literals

from ilda import *
import threading

import wiringpi
import sys
import queue
import math
from utils import map_feature_to_effect

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

BASS_FREQ_UPPER = 300
HIGH_FREQ_LOWER = 1000
FPS = 60
X_CENTER = 2048
Y_CENTER = 2048


def decode_color(hex):
    hex_striped = hex.lstrip("#")
    return tuple(int(hex_striped[i : i + 2], 16) for i in (0, 2, 4))


def check_and_map_point(val):
    if val > 32767:
        val = 32767
    if val < -32768:
        val = -32768
    map_val = lambda x: int((x + 32768) / (32767 + 32768) * 4096)
    return map_val(val)


def map_point_to_range(x, y):
    return (check_and_map_point(x), check_and_map_point(y))


def scale_point(x, y, effect):
    y_diff = y - Y_CENTER
    x_diff = x - X_CENTER
    r = math.sqrt(pow(x_diff, 2) + pow(y_diff, 2))
    # print(f"R: {r}")
    if x_diff == 0:
        return (x, y + (effect * r)) if y_diff > 0 else (x, y - (effect * r))

    angle = math.atan(y_diff / x_diff)
    x_change = effect * r * math.cos(angle)
    y_change = effect * r * math.sin(angle)
    # print(
    #     f"X_DIFF: {x_diff} | Y_DIFF: {y_diff} | X_CHANGE: {x_change} | y_change: {y_change}"
    # )
    # print(f"X: {x} --> X_NEW: {x+x_change} | Y: {y} --> Y_NEW: {y+y_change}")

    x_effected = x + x_change if x_diff >= 0 else x - x_change
    y_effected = y + y_change if x_diff >= 0 else y - y_change
    return map_point_to_range(x_effected, y_effected)


def run_galvo(dac, x, y, z, effect):
    # print(map_feature_to_effect(feature))
    x_effected, y_effected = scale_point(x, y, effect)
    dac.set_dac_raw(1, int(x_effected))
    dac.set_dac_raw(2, 4096 - int(y_effected))


# TODO: this is to change laser color, turn on and off
def run_laser(color, brightness, blanking):
    if blanking:
        wiringpi.digitalWrite(0, 0)
    else:
        wiringpi.digitalWrite(0, 1)
    # pass


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
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(0, 1)

    f = open(file, "rb")
    show = [t for t in readFrames(f)]

    effect = 0
    brightness, color, sensitivity, paused, enable_scaling = 0, 0, 0, False, True

    while not stop():
        for table in show:
            # kill thread if flagged
            if stop():
                break
            # check_settings = time.time()
            if not settings.empty():
                setting = settings.get()
                # TODO: include setting to reset color to ilda file
                # specified_color = False

                paused_old = paused
                enable_scaling_old = enable_scaling

                brightness, color, sensitivity, paused, enable_scaling = (
                    setting["brightness"],
                    decode_color(setting["color"]),
                    setting["sensitivity"],
                    setting["paused"],
                    setting["enable_scaling"],
                )

                if not enable_scaling:
                    effect = 0

                if (not paused and paused_old) or (
                    enable_scaling and not enable_scaling_old
                ):
                    try:
                        while True:
                            features.get_nowait()
                    except queue.Empty:
                        pass

            if not paused:
                if not features.empty() and enable_scaling:
                    feature = features.get()
                    if feature <= 3000:
                        effect = map_feature_to_effect(feature)
                # print(f"EFFECT: {effect}")

                for point in table.iterPoints():
                    run_galvo(adcdac, point.x, point.y, point.z, effect)
                    run_laser(None, None, point.blanking)

    wiringpi.digitalWrite(0, 0)


def run_master_galvo_laser_task(files, settings, features, active_show):
    galvo_laser_thread = None
    stop_thread = False

    while True:
        if active_show.value and not files.empty():
            file = files.get()

            if galvo_laser_thread and galvo_laser_thread.is_alive():
                print(f"Killing {galvo_laser_thread.getName()} ...")
                stop_thread = True
                galvo_laser_thread.join()

            try:
                while True:
                    features.get_nowait()
            except queue.Empty:
                pass

            stop_thread = False
            galvo_laser_thread = threading.Thread(
                target=run_galvo_and_laser,
                args=[lambda: stop_thread, file, settings, features],
                name=f"Galvo and Laser Show: {file}",
            )
            galvo_laser_thread.daemon = True
            galvo_laser_thread.start()
            print(f"Starting  {galvo_laser_thread.getName()}")

        if not active_show.value:
            if galvo_laser_thread and galvo_laser_thread.is_alive():
                print(f"Killing {galvo_laser_thread.getName()} ...")
                stop_thread = True
                galvo_laser_thread.join()


def onInterrupt(sig, frame):
    wiringpi.digitalWrite(0, 0)
    print("Turn off laser diode.")


if __name__ == "__main__":
    # from queue import Queue
    # import threading

    # adcdac = ADCDACPi(2)  # 0 - 4.096 V

    # file = "./ilda-files/circle5.ild"

    # files = Queue()
    # settings = Queue()
    # features= Queue()

    # thread = threading.Thread(target=run_master_galvo_laser_task, args=[files,settings, features])
    # thread.daemon = True

    # thread.start()

    # signal.signal(signal.SIGINT, onInterrupt)
    # # files.put("./ilda-files/burst.ild")

    # feat = [100,100,1000,100,10000,100,100,1000,100,10000,1000]

    # while True:
    #     files.put("./ilda-files/smallcirc.ild")
    #     time.sleep(3)
    #     files.put("./ilda-files/medcirc.ild")
    #     time.sleep(3)
    #     files.put("./ilda-files/bigcirc.ild")
    #     time.sleep(3)

    # for f in feat:
    #     features.put(f)
    #     time.sleep(1.25)
    pass
