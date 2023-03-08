import time
from audio_analyzer.stream_analyzer import Stream_Analyzer
from queue import Queue


def run_analyzer(features_queue, analyzer_settings_queue):
    sampling_period = 3.0

    ear = Stream_Analyzer(
        device=None,  # Pyaudio (portaudio) device index, defaults to first mic input
        rate=None,  # Audio samplerate, None uses the default source settings
        FFT_window_size_ms=60,  # Window size used for the FFT transform
        updates_per_second=1000,  # How often to read the audio stream for new data
        smoothing_length_ms=50,  # Apply some temporal smoothing to reduce noisy features
        n_frequency_bins=600,  # The FFT features are grouped in bins
        visualize=0,  # Visualize the FFT features with PyGame
        verbose=0,  # Print running statistics (latency, fps, ...)
    )

    fps = 60
    count = 0

    last_update = time.time()
    while True:
        if not analyzer_settings_queue.empty():
            sensitivity = analyzer_settings_queue.get()
            sampling_period = -1 * (sensitivity / 20.0) + 5.25
            print(f"Updated sampling period: {sampling_period}s")
        if (time.time() - last_update) > (1.0 / fps):
            count += 1
            last_update = time.time()
            raw_fftx, raw_fft, binned_fftx, binned_fft = ear.get_audio_features()
            if count % int(sampling_period * fps) == 0:
                features_queue.put(int(ear.strongest_frequency))
                print(f"Analyzer: {int(ear.strongest_frequency)}")
                # now = time.strftime("%H:%M:%S", time.localtime(last_update))
        #         # print(f"Strongest frequency @ {now}: {ear.strongest_frequency}")
        else:
            try:
                time.sleep(((1.0 / fps) - (time.time() - last_update)) * 0.95)
            except:
                continue


if __name__ == "__main__":
    queue1 = Queue()
    queue2 = Queue()
    run_analyzer(queue1, queue2)
