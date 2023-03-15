import threading
import multiprocessing
import time
import psutil
import os
import math
from queue import Queue


def add_task(queue):
    while True:
        time.sleep(2)
        queue.put((5, time.time()))


def use_task(queue):
    while True:
        if not queue.empty():
            print(f"Task time: {time.time() - queue.get()[1]}s")


def test_threading():
    queue = Queue()
    thread1 = threading.Thread(target=add_task, args=[queue])
    thread1.daemon = True

    thread2 = threading.Thread(target=use_task, args=[queue])
    thread2.daemon = True

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()


def test_multiprocessing():
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    process1 = multiprocessing.Process(target=add_task, args=[queue])
    process1.daemon = True

    process2 = multiprocessing.Process(target=use_task, args=[queue])
    process2.daemon = True

    process1.start()
    process2.start()

    process1.join()
    process2.join()


if __name__ == "__main__":
    # test_threading()

    test_multiprocessing()
    while True:
        time.sleep(2)
