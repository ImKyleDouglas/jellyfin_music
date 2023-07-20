from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QProgressBar, QApplication,
                            QFileDialog, QSizeGrip, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import json
from resources_rc import *

# Other classes within files
from notification_audio_thread import NotificationAudioThread
from organize_thread import OrganizeThread
from custom_dialog import CustomDialog
from music_error_window import MusicErrorWindow
from replace_skip_window import ReplaceSkipWindow
from settings_window import SettingsWindow

class MusicOrganizer(QWidget):
    def __init__(self):
        super().__init__()

        # Version Control
        self.version = '3.06'

        # Set default settings
        self.music_folder_path = ''
        self.destination_folder_path = ''

        # Setup and show user interface
        self.setup_ui()

        # Load settings from file if it exists
        self.load_settings()

        # Show starting window
        self.show()

    def showEvent(self, event):
        super().showEvent(event)
        self.center_window()

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

        self.title_label = QLabel(f"Music Organizer v{self.version}")
        self.title_label.setStyleSheet("color: white;")
        hbox_title_layout.addWidget(self.title_label)

        hbox_title_layout.addStretch()

        self.settings_button = QPushButton("⚙")
        self.settings_button.setToolTip('Settings')
        self.settings_button.setFixedSize(24, 24)
        self.settings_button.setStyleSheet(
            "QPushButton { color: white; background-color: transparent; }"
            "QPushButton:hover { background-color: blue; }"
        )
        hbox_title_layout.addWidget(self.settings_button)
        self.settings_button.clicked.connect(self.settings_window)

        self.minimize_button = QPushButton("—")
        self.minimize_button.setToolTip('Minimize window')
        self.minimize_button.setFixedSize(24, 24)
        self.minimize_button.setStyleSheet(
            "QPushButton { color: white; background-color: transparent; }"
            "QPushButton:hover { background-color: green; }"
        )
        hbox_title_layout.addWidget(self.minimize_button)
        self.minimize_button.clicked.connect(self.showMinimized)

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
        self.setWindowTitle(f'Music Organizer v{self.version}')
        self.setWindowIcon(QIcon(':/Octopus.ico'))
        self.setGeometry(100, 100, 400, 260) # Set initial size of window (x, y, width, height)

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

        # Create music folder select button
        self.music_folder_select_button = QPushButton('Select Music Folder')
        vbox_main_layout.addWidget(self.music_folder_select_button)
        self.music_folder_select_button.clicked.connect(self.select_music_folder)

        # Create music folder label
        self.music_folder_label = QLabel(self.music_folder_path)
        vbox_main_layout.addWidget(self.music_folder_label)

        # Create destination folder select button
        self.destination_folder_select_button = QPushButton('Select Destination Folder')
        vbox_main_layout.addWidget(self.destination_folder_select_button)
        self.destination_folder_select_button.clicked.connect(self.select_destination_folder)

        # Create destination folder label
        self.destination_folder_label = QLabel(self.destination_folder_path)
        vbox_main_layout.addWidget(self.destination_folder_label)

        # Add a spacer item to create an empty line
        spacer_item = QSpacerItem(30, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        vbox_main_layout.addItem(spacer_item)

        # Create organize button
        self.organize_button = QPushButton('Organize')
        # Check if settings are empty
        if not self.music_folder_path or not self.destination_folder_path:
            self.organize_button.setEnabled(False)
        else:
            self.organize_button.setEnabled(True)
        vbox_main_layout.addWidget(self.organize_button)
        self.organize_button.clicked.connect(self.organize_function)

        # Create label for number of songs
        self.number_songs_label = QLabel("")
        vbox_main_layout.addWidget(self.number_songs_label)

        # QHBoxLayout setup for progress bar and grip
        hbox_progress_grip_layout = QHBoxLayout()
        vbox_main_layout.addLayout(hbox_progress_grip_layout)

        # Create progress bar
        self.music_progress_bar = QProgressBar()
        self.music_progress_bar.setValue(0)
        self.music_progress_bar.setMaximum(100)
        hbox_progress_grip_layout.addWidget(self.music_progress_bar)

        # Add resizing handles
        self.bottom_right_grip = QSizeGrip(self)
        self.bottom_right_grip.setToolTip('Resize window')
        hbox_progress_grip_layout.addWidget(self.bottom_right_grip, 0, Qt.AlignBottom | Qt.AlignRight)

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
            # Check if settings are empty
            if not self.music_folder_path or not self.destination_folder_path:
                self.organize_button.setEnabled(False)
            else:
                self.organize_button.setEnabled(True)
            self.reset_progress_songs_label()

    def select_destination_folder(self):
        destination_folder_path = QFileDialog.getExistingDirectory(self, 'Select Destination Folder')
        if destination_folder_path:
            self.destination_folder_path = destination_folder_path
            self.destination_folder_label.setText(self.destination_folder_path)
            # Check if settings are empty
            if not self.music_folder_path or not self.destination_folder_path:
                self.organize_button.setEnabled(False)
            else:
                self.organize_button.setEnabled(True)
            self.reset_progress_songs_label()

    def reset_progress_songs_label(self):
        self.music_progress_bar.setValue(0)  # Reset the progress bar to 0
        self.music_progress_bar.setStyleSheet("") # Reset the style sheet to default
        self.number_songs_label.setText('') # Reset number of songs label

    def load_settings(self):
        try:
            with open('settings_jmo.json', 'r') as f:
                self.settings = json.load(f)
                self.music_folder_path = self.settings.get("music_folder_path", "")
                self.destination_folder_path = self.settings.get("destination_folder_path", "")

                # Update the labels with the loaded values
                self.music_folder_label.setText(self.music_folder_path)
                self.destination_folder_label.setText(self.destination_folder_path)

                # Check if settings are empty
                if not self.music_folder_path or not self.destination_folder_path:
                    self.organize_button.setEnabled(False)
                else:
                    self.organize_button.setEnabled(True)
        except FileNotFoundError:
            # Initialize self.settings dictionary
            self.settings = {}

    def organize_function(self):
        # Disable UI elements
        self.user_interface(False)
        # Variables needed in OrganizeThread
        info = {
            'selected_music_folder_path':self.music_folder_path,
            'selected_destination_folder_path':self.destination_folder_path
        }
        self.organize_thread = OrganizeThread(info)
        self.organize_thread.number_songs_signal.connect(self.number_songs)
        self.organize_thread.music_progress_signal.connect(self.music_progress)
        self.organize_thread.kill_thread_signal.connect(self.kill_thread)
        self.organize_thread.custom_dialog_signal.connect(self.custom_dialog_function)
        self.organize_thread.organize_finish_signal.connect(self.organize_finish)
        self.organize_thread.start()

    def user_interface(self, msg):
        # Define a list of UI elements to enable/disable
        ui_elements = [self.destination_folder_select_button, self.music_folder_select_button,
                    self.organize_button, self.close_button, self.settings_button]

        # Set the enabled state of each element based on the value of msg
        enabled = msg
        for element in ui_elements:
            element.setEnabled(enabled)

    def number_songs(self, msg):
        self.number_songs_label.setText(f'Number of songs found: {msg}')
        if msg:
            # Initialize progress bar at zero percent
            self.music_progress(0)

    def music_progress(self, msg):
        self.music_progress_bar.setValue(int(msg))
        if self.music_progress_bar.value() == self.music_progress_bar.maximum():
            # Update the style sheet for the progress bar
            self.music_progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid black;
                    text-align: center;
                    color: black;
                    background-color: rgba(255, 152, 152, 1);
                }

                QProgressBar::chunk {
                    background-color: rgba(255, 152, 152, 1);
                }
            """)
        else:
            # Check if the current style sheet is different from an empty string
            if self.music_progress_bar.styleSheet() != "":
                # Reset the style sheet to default
                self.music_progress_bar.setStyleSheet("")
            
    def kill_thread(self, msg):
        if msg == 'organize'and hasattr(self, 'organize_thread'):
            # Delete OrganizeThread if it exists
            del self.organize_thread
            # Re-enable UI elements
            self.user_interface(True)
        if msg == 'notification' and hasattr(self, 'notification_thread'):
            # Delete NotificationAudioThread if it exists
            del self.notification_thread

    def custom_dialog_function(self, msg):
        if msg:
            # No songs were found
            custom_dialog = CustomDialog(msg)
            custom_dialog.exec_()

    def organize_finish(self, recall_files):
        self.kill_thread('organize')
        # Save recall_files for other functions
        self.recall_files = recall_files
        # Replace or Skip Files
        if recall_files['replace_skip_files']:
            if not self.settings.get('mute_sound', False):
                # Play ding sound (name of file)
                self.notification_thread = NotificationAudioThread('audio_ding')
                self.notification_thread.kill_thread_signal.connect(self.kill_thread)
                self.notification_thread.start()
            self.organize_replace_skip()
        else:
            self.replace_skip_finish()

    def organize_replace_skip(self):
        if self.recall_files['replace_skip_files']:
            # Music File Replace Skip Window
            self.music_replace_skip_window = ReplaceSkipWindow(self.recall_files['replace_skip_files'])
            self.music_replace_skip_window.windowClosed.connect(self.replace_skip_finish)
            self.music_replace_skip_window.windowOpened.connect(self.user_interface)
            self.music_replace_skip_window.show()
            
    def replace_skip_finish(self):
        self.user_interface(True)
        # Set progress bar to maximum
        self.music_progress(self.music_progress_bar.maximum())
        if self.recall_files['error_files']:
            if not self.settings.get('mute_sound', False):
                # Play ding sound (name of file)
                self.notification_thread = NotificationAudioThread('audio_ding')
                self.notification_thread.kill_thread_signal.connect(self.kill_thread)
                self.notification_thread.start()
            self.organize_error()
        elif not self.settings.get('mute_sound', False):
            # Play complete sound (name of file)
            self.notification_thread = NotificationAudioThread('audio_complete')
            self.notification_thread.kill_thread_signal.connect(self.kill_thread)
            self.notification_thread.start()

    def organize_error(self):
        if self.recall_files['error_files']:
            # Music File Error Window
            self.music_error_window = MusicErrorWindow(self.recall_files['error_files'])
            self.music_error_window.windowClosed.connect(self.user_interface)
            self.music_error_window.windowOpened.connect(self.user_interface)
            self.music_error_window.custom_dialog_signal.connect(self.custom_dialog_function)
            self.music_error_window.show()

    def settings_window(self):
        # Settings Window
        self.music_error_window = SettingsWindow()
        self.music_error_window.windowClosed.connect(self.settings_finish)
        self.music_error_window.windowOpened.connect(self.user_interface)
        self.music_error_window.show()

    def settings_finish(self):
        self.user_interface(True)
        # Load settings from file if it exists
        self.load_settings()
        self.reset_progress_songs_label()


