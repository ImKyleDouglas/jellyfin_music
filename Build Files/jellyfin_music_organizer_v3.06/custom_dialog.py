from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
                            QPushButton, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import json
from resources_rc import *

# Other classes within files
from notification_audio_thread import NotificationAudioThread

class CustomDialog(QDialog):
    def __init__(self, custom_message):
        super().__init__()

        # Version Control
        self.version = '3.06'

        # Set notification thread variable
        self.notification_thread = None

        # Hides the default titlebar
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Window title, icon, and size
        self.setWindowTitle(f'Alert v{self.version}')
        self.setWindowIcon(QIcon(':/Octopus.ico'))

        # Main layout
        layout = QVBoxLayout()

        # Custom title bar widget
        title_bar_widget = QWidget()
        layout.addWidget(title_bar_widget)

        # Title bar layout
        title_layout = QHBoxLayout()

        # Icon top left
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(':/Octopus.ico').pixmap(24, 24))
        title_layout.addWidget(icon_label)

        title_label = QLabel(f"Alert v{self.version}")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        close_button = QPushButton("X")
        close_button.setToolTip('Close window')
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet(
            "QPushButton { color: white; background-color: transparent; }"
            "QPushButton:hover { background-color: red; }"
        )
        title_layout.addWidget(close_button)
        close_button.clicked.connect(self.reject)

        title_bar_widget.setLayout(title_layout)

        # Error message label
        error_label = QLabel(custom_message)
        error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(error_label)
        self.setLayout(layout)

        # Apply stylesheet for red border
        self.setStyleSheet("QDialog { border: 2px solid rgba(255, 152, 152, 1); }")

    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def showEvent(self, event):
        # Load settings from file if it exists
        self.load_settings()
        if not self.settings.get('mute_sound', False):
            self.notification_thread = NotificationAudioThread('audio_ding') # (name of file)
            self.notification_thread.start()
        super().showEvent(event)
        self.center_window()

    def closeEvent(self, event):
        if self.notification_thread.isRunning():
            self.notification_thread.terminate()
        super().closeEvent(event)
        # Wait for the thread to finish before quitting the application
        self.notification_thread.wait()
        
    def load_settings(self):
        try:
            with open('settings_jmo.json', 'r') as f:
                self.settings = json.load(f)

        except FileNotFoundError:
            # Initialize self.settings dictionary
            self.settings = {}