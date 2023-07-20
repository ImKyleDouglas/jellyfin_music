from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QApplication, QSizeGrip, QCheckBox,
                            QSpacerItem, QSizePolicy,QFrame, QFileDialog)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QIcon
import json

class SettingsWindow(QWidget):
    windowOpened = pyqtSignal(bool)
    windowClosed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        # Version Control
        self.version = '3.06'

        # Initialize attributes
        self.music_folder_path = ''
        self.destination_folder_path = ''

        # Setup and show user interface
        self.setup_ui()

        # Load settings from file if it exists
        self.load_settings()

    def showEvent(self, event):
        self.windowOpened.emit(False)
        super().showEvent(event)
        self.center_window()

    def closeEvent(self, event):
        self.windowClosed.emit(True)
        super().closeEvent(event)

    def setup_titlebar(self):
        # Hides the default titlebar
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Title bar widget
        self.title_bar = QWidget(self)
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(32)

        hbox_title_layout = QHBoxLayout(self.title_bar)
        hbox_title_layout.setContentsMargins(0, 0, 0, 0)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon(':/Octopus.ico').pixmap(24, 24))
        hbox_title_layout.addWidget(self.icon_label)

        self.title_label = QLabel(f"Settings Window v{self.version}")
        self.title_label.setStyleSheet("color: white;")
        hbox_title_layout.addWidget(self.title_label)

        hbox_title_layout.addStretch()

        self.close_button = QPushButton("✕")
        self.close_button.setToolTip('Close window')
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet(
            "QPushButton { color: white; background-color: transparent; }"
            "QPushButton:hover { background-color: red; }"
        )
        hbox_title_layout.addWidget(self.close_button)
        self.close_button.clicked.connect(self.close)

        hbox_title_layout.setAlignment(Qt.AlignRight)

    # Mouse events allow the title bar to be dragged around
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() <= self.title_bar.height():
            self.draggable = True
            self.offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'draggable') and self.draggable:
            if event.buttons() & Qt.LeftButton:
                self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = False

    def setup_ui(self):
        # Window setup
        self.setWindowTitle(f"Settings Window v{self.version}")
        self.setWindowIcon(QIcon(':/Octopus.ico'))
        self.setGeometry(100, 100, 400, 300) # Set initial size of window (x, y, width, height)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Custom title bar
        self.setup_titlebar()
        main_layout.addWidget(self.title_bar)

        # Central widget
        self.central_widget = QWidget(self)
        main_layout.addWidget(self.central_widget)

        # QVBoxLayout for central widget
        vbox_main_layout = QVBoxLayout(self.central_widget)

        # QLabel for sound
        self.sound_label = QLabel(self)
        self.sound_label.setText("Sound:")
        vbox_main_layout.addWidget(self.sound_label)

        # Create the checkbox
        self.checkbox = QCheckBox("Mute all sound")
        self.checkbox.setChecked(False)
        vbox_main_layout.addWidget(self.checkbox)

        # Add a spacer item to create an empty line
        spacer_item = QSpacerItem(30, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        vbox_main_layout.addItem(spacer_item)

        # QLabel for music library
        self.music_label = QLabel(self)
        self.music_label.setText("Folders:")
        vbox_main_layout.addWidget(self.music_label)

        # QHBoxLayout setup for music select and music clear
        hbox_music_clear_layout = QHBoxLayout()
        vbox_main_layout.addLayout(hbox_music_clear_layout)

        # Create music folder select button
        self.music_folder_select_button = QPushButton('Set Default Music Folder')
        hbox_music_clear_layout.addWidget(self.music_folder_select_button, 1)
        self.music_folder_select_button.clicked.connect(self.select_music_folder)

        # Create music folder clear button
        self.music_folder_clear_button = QPushButton('Clear')
        hbox_music_clear_layout.addWidget(self.music_folder_clear_button)
        self.music_folder_clear_button.clicked.connect(self.clear_music_folder)

        # Create music folder label
        self.music_folder_label = QLabel(self.music_folder_path)
        vbox_main_layout.addWidget(self.music_folder_label)

        # QHBoxLayout setup for destination select and destination clear
        hbox_destination_clear_layout = QHBoxLayout()
        vbox_main_layout.addLayout(hbox_destination_clear_layout)

        # Create destination folder select button
        self.destination_folder_select_button = QPushButton('Set Default Destination Folder')
        hbox_destination_clear_layout.addWidget(self.destination_folder_select_button, 1)
        self.destination_folder_select_button.clicked.connect(self.select_destination_folder)

        # Create destination folder clear button
        self.destination_folder_clear_button = QPushButton('Clear')
        hbox_destination_clear_layout.addWidget(self.destination_folder_clear_button)
        self.destination_folder_clear_button.clicked.connect(self.clear_destination_folder)

        # Create destination folder label
        self.destination_folder_label = QLabel(self.destination_folder_path)
        vbox_main_layout.addWidget(self.destination_folder_label)

        # Add a spacer item to create an empty line
        spacer_item = QSpacerItem(30, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        vbox_main_layout.addItem(spacer_item)

        # QHBoxLayout setup for save and reset settings
        hbox_save_reset_layout = QHBoxLayout()
        vbox_main_layout.addLayout(hbox_save_reset_layout)

        # Create save settings button
        self.save_button = QPushButton('Save Settings')
        hbox_save_reset_layout.addWidget(self.save_button, 1)
        self.save_button.clicked.connect(self.save_settings)
        
        # Create a line between the save and reset button
        line_save_reset = QFrame()
        line_save_reset.setFrameShape(QFrame.VLine)
        line_save_reset.setFrameShadow(QFrame.Sunken)
        hbox_save_reset_layout.addWidget(line_save_reset)

        # Create reset settings button
        self.reset_button = QPushButton('Reset && Save All Settings')
        hbox_save_reset_layout.addWidget(self.reset_button, 1)
        self.reset_button.clicked.connect(self.reset_settings)
        
        # Add resizing handles
        self.bottom_right_grip = QSizeGrip(self)
        self.bottom_right_grip.setToolTip('Resize window')
        hbox_save_reset_layout.addWidget(self.bottom_right_grip, 0, Qt.AlignBottom | Qt.AlignRight)

    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def select_music_folder(self):
        music_folder_path = QFileDialog.getExistingDirectory(self, 'Select Music Folder')
        if music_folder_path:
            self.music_folder_path = music_folder_path
            self.music_folder_label.setText(self.music_folder_path)

    def clear_music_folder(self):
        self.music_folder_path = ''
        self.music_folder_label.setText('')

    def select_destination_folder(self):
        destination_folder_path = QFileDialog.getExistingDirectory(self, 'Select Destination Folder')
        if destination_folder_path:
            self.destination_folder_path = destination_folder_path
            self.destination_folder_label.setText(self.destination_folder_path)

    def clear_destination_folder(self):
        self.destination_folder_path = ''
        self.destination_folder_label.setText('')

    def load_settings(self):
        try:
            with open('settings_jmo.json', 'r') as f:
                self.settings = json.load(f)
                self.music_folder_path = self.settings.get("music_folder_path", "")
                self.destination_folder_path = self.settings.get("destination_folder_path", "")
                self.checkbox.setChecked(self.settings.get("mute_sound", False))

                # Update the labels with the loaded values
                self.music_folder_label.setText(self.music_folder_path)
                self.destination_folder_label.setText(self.destination_folder_path)
        except FileNotFoundError:
            # Initialize self.settings dictionary
            self.settings = {}

    def save_settings(self):
        # Create settings dictionary
        settings = {
            "music_folder_path": self.music_folder_path,
            "destination_folder_path": self.destination_folder_path,
            "mute_sound": self.checkbox.isChecked()
        }

        # Save settings to file
        with open('settings_jmo.json', 'w') as file:
            json.dump(settings, file, indent=4)

        # Update the button text and color temporarily
        self.save_button.setText("Success")
        self.save_button.setStyleSheet("""
            background-color: rgba(255, 152, 152, 1);
            color: black;
        """)

        # Stop any existing save timers before creating a new one
        if hasattr(self, "reset_save_timer"):
            self.reset_save_timer.stop()

        # Create a new save timer to reset the button text and color after 1 seconds
        self.reset_save_timer = QTimer(self)
        self.reset_save_timer.timeout.connect(self.resetSaveButton)
        self.reset_save_timer.start(1000)

    def resetSaveButton(self):
        self.save_button.setText("Save Settings")
        self.save_button.setStyleSheet("")

    def reset_settings(self):
        #Default settings
        self.music_folder_path = ''
        self.destination_folder_path = ''
        self.checkbox.setChecked(False)

        # Reset settings to default
        self.music_folder_label.setText(self.music_folder_path)
        self.destination_folder_label.setText(self.destination_folder_path)

        # Save settings to file
        self.save_settings()

        # Update the button text and color temporarily
        self.reset_button.setText("Success")
        self.reset_button.setStyleSheet("""
            background-color: rgba(255, 152, 152, 1);
            color: black;
        """)

        # Stop any existing reset timers before creating a new one
        if hasattr(self, "reset_reset_timer"):
            self.reset_reset_timer.stop()

        # Create a new reset timer to reset the button text and color after 1 seconds
        self.reset_reset_timer = QTimer(self)
        self.reset_reset_timer.timeout.connect(self.resetResetButton)
        self.reset_reset_timer.start(1000)

    def resetResetButton(self):
        self.reset_button.setText("Reset && Save All Settings")
        self.reset_button.setStyleSheet("")


