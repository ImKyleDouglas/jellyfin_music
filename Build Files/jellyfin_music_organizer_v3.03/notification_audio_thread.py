from PyQt5.QtCore import QThread, pyqtSignal
import pyaudio
import numpy as np
from resources_rc import *

class NotificationAudioThread(QThread):
    finished = pyqtSignal()

    def __init__(self, audio_bytearray, sample_rate=44100, channels=1, format=pyaudio.paInt16):
        super().__init__()
        self.audio_bytearray = audio_bytearray
        self.sample_rate = sample_rate
        self.channels = channels
        self.format = format

    def run(self):
        pa = pyaudio.PyAudio()
        audio_data = np.frombuffer(self.audio_bytearray, dtype=np.int16)
        stream = pa.open(format=self.format, channels=self.channels, rate=self.sample_rate, output=True)
        stream.write(audio_data.tobytes())
        stream.stop_stream()
        stream.close()
        pa.terminate()
        self.finished.emit()