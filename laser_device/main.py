from server import run_server
from analyzer import run_analyzer
from queue import Queue
import threading
import time

if __name__ == "__main__":
    settings_queue = Queue()  # Settings (dict)
    features_queue = Queue()  # Strongest frequencies (int)
    analyzer_settings_queue = Queue()

    thread_server = threading.Thread(
        target=run_server, args=[settings_queue], name="LAN-Server"
    )
    thread_server.daemon = True

    thread_analyzer = threading.Thread(
        target=run_analyzer,
        args=[features_queue, analyzer_settings_queue],
        name="Read Time Audio Processing",
    )
    thread_analyzer.daemon = True

    thread_server.start()
    thread_analyzer.start()

    while True:
        if not settings_queue.empty():
            settings = settings_queue.get()
            analyzer_settings_queue.put(settings["data"]["sensitivity"])
            # Load new thread for galvos and RGB laser
            # Reset features queue
            with features_queue.mutex:
                features_queue.queue.clear()
                features_queue.all_tasks_done.notify_all()
                features_queue.unfinished_tasks = 0

        if not features_queue.empty():
            print(f"Strongest freq: {features_queue.get()}")
