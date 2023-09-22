# write program to detect audio  from microphone

import pyaudio
import wave
import os
import sys

def detect():
    # instantiate PyAudio (1)
    p = pyaudio.PyAudio()

    # define callback (2)
    def callback(in_data, frame_count, time_info, status):
        print(in_data)
        return (in_data, pyaudio.paContinue)

    # open stream using callback (3)
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024,
                    stream_callback=callback)

    # start the stream (4)
    stream.start_stream()

    # wait for stream to finish (5)
    while stream.is_active():
        print("stream is active")
        pass

    # stop stream (6)
    stream.stop_stream()
    stream.close()

    # close PyAudio (7)
    p.terminate()
    return 0

if __name__ == "__main__":
    detect()