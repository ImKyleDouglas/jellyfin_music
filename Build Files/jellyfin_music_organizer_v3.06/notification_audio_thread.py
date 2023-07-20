from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import sys
import os

class NotificationAudioThread(QThread):
    kill_thread_signal = pyqtSignal(str)

    def __init__(self, audio_file_name):
        super().__init__()
        self.audio_file_name = audio_file_name
        self.media_player = QMediaPlayer()
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)

    def run(self):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        audio_path = os.path.join(base_path, f"notification_audio/{self.audio_file_name}.wav")

        # Set media content and play the audio using QMediaPlayer
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_path)))
        self.media_player.play()

    def on_media_status_changed(self, status):
        # Check if the media player has finished playing
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.stop()
            self.media_player.deleteLater()
            self.kill_thread_signal.emit('notification')
