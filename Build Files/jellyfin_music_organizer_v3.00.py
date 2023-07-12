from PyQt5.QtWidgets import (QApplication, QMainWindow, QGroupBox, QVBoxLayout, QLabel, QPushButton,
                            QProgressBar, QFileDialog, QHBoxLayout, QFrame, QWidget, QDialog, QListWidget, QTextEdit,
                            QMessageBox, QSplitter)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QPoint, QTimer
from PyQt5.QtGui import QIcon
from pathlib import Path
import qdarkstyle
import mutagen
from mutagen.asf import ASFUnicodeAttribute
import shutil
import openpyxl
import json
import csv
from resources_rc import *

class JellyfinMusicOrganizer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set default settings
        self.music_folder_path = ''
        self.destination_folder_path = ''

        # Load settings from file if it exists
        self.load_settings()

        # Setup and show user interface
        self.setup_titlebar()
        self.setup_ui()
        self.initialize_windows()
        self.show()

    def setup_titlebar(self):
        # Create a central widget and set the layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title bar widget
        self.title_bar = QWidget(self)
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(32)

        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon(':/Octopus.ico').pixmap(24, 24))
        title_layout.addWidget(self.icon_label)

        self.title_label = QLabel("Jellyfin Music Organizer v3.00")
        self.title_label.setStyleSheet("color: white;")
        title_layout.addWidget(self.title_label)

        title_layout.addStretch()

        self.minimize_button = QPushButton("—")
        self.minimize_button.setFixedSize(24, 24)
        self.minimize_button.setStyleSheet(
            "QPushButton { color: white; background-color: transparent; }"
            "QPushButton:hover { background-color: red; }"
        )
        title_layout.addWidget(self.minimize_button)

        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet(
            "QPushButton { color: white; background-color: transparent; }"
            "QPushButton:hover { background-color: red; }"
        )
        title_layout.addWidget(self.close_button)

        title_layout.setAlignment(Qt.AlignRight)

        self.minimize_button.clicked.connect(self.showMinimized)
        self.close_button.clicked.connect(self.close)

        layout.addWidget(self.title_bar, 0, Qt.AlignTop)

        # Initialize variables for dragging
        self.draggable = False
        self.offset = QPoint()

    # Mouse events allow the title bar to be dragged around
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() <= self.title_bar.height():
            self.draggable = True
            self.offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self.draggable:
            if event.buttons() & Qt.LeftButton:
                self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = False

    def setup_ui(self):
        # Hides the default titlebar
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Window title, icon, and size
        self.setWindowTitle('Jellyfin Music Organizer')
        self.setWindowIcon(QIcon(':/Octopus.ico'))
        self.resize(400, 265)
        self.center_window()

        # Create group box
        self.group_box = QGroupBox('Music Organizer', self)
        self.group_box.setGeometry(10, 45, self.width() - 20, self.height() - 50)

        vbox_music_organizer = QVBoxLayout()

        hbox_music_folder_select = QHBoxLayout()
        # Create music folder select button
        self.music_folder_select_button = QPushButton('Select Music Folder')
        self.music_folder_select_button.clicked.connect(self.select_music_folder)
        hbox_music_folder_select.addWidget(self.music_folder_select_button)

        vbox_music_organizer.addLayout(hbox_music_folder_select)

        hbox_music_folder_label = QHBoxLayout()
        # Create music folder label
        self.music_folder_label = QLabel(self.music_folder_path)
        hbox_music_folder_label.addWidget(self.music_folder_label)

        vbox_music_organizer.addLayout(hbox_music_folder_label)

        hbox_destination_folder_select = QHBoxLayout()
        # Create destination folder select button
        self.destination_folder_select_button = QPushButton('Select Destination Folder')
        self.destination_folder_select_button.clicked.connect(self.select_destination_folder)
        hbox_destination_folder_select.addWidget(self.destination_folder_select_button)

        vbox_music_organizer.addLayout(hbox_destination_folder_select)

        hbox_destination_folder_label = QHBoxLayout()
        # Create destination folder label
        self.destination_folder_label = QLabel(self.destination_folder_path)
        hbox_destination_folder_label.addWidget(self.destination_folder_label)

        vbox_music_organizer.addLayout(hbox_destination_folder_label)

        hbox_save_reset = QHBoxLayout()
        # Create save settings button
        self.save_button = QPushButton('Save Settings')
        self.save_button.clicked.connect(self.save_settings)
        hbox_save_reset.addWidget(self.save_button)

        # Create a line between the save and reset button
        line_save_reset = QFrame()
        line_save_reset.setFrameShape(QFrame.VLine)
        line_save_reset.setFrameShadow(QFrame.Sunken)
        hbox_save_reset.addWidget(line_save_reset)

        # Create reset settings button
        self.reset_button = QPushButton('Reset Settings')
        self.reset_button.clicked.connect(self.reset_settings)
        hbox_save_reset.addWidget(self.reset_button)

        vbox_music_organizer.addLayout(hbox_save_reset)

        hbox_organize_button = QHBoxLayout()
        # Create organize button
        self.organize_button = QPushButton('Organize')
        self.organize_button.clicked.connect(self.organize_function)
        # Check if settings are empty
        if not self.music_folder_path or not self.destination_folder_path:
            self.organize_button.setEnabled(False)
        else:
            self.organize_button.setEnabled(True)
        hbox_organize_button.addWidget(self.organize_button)

        vbox_music_organizer.addLayout(hbox_organize_button)

        hbox_number_songs = QHBoxLayout()
        # Create label for number of songs
        self.number_songs_label = QLabel("")
        hbox_number_songs.addWidget(self.number_songs_label)

        vbox_music_organizer.addLayout(hbox_number_songs)

        hbox_progress_bar = QHBoxLayout()
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        hbox_progress_bar.addWidget(self.progress_bar)

        vbox_music_organizer.addLayout(hbox_progress_bar)

        self.group_box.setLayout(vbox_music_organizer)

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
            self.organize_button.setEnabled(True)

    def select_destination_folder(self):
        destination_folder_path = QFileDialog.getExistingDirectory(self, 'Select Destination Folder')
        if destination_folder_path:
            self.destination_folder_path = destination_folder_path
            self.destination_folder_label.setText(self.destination_folder_path)
            self.organize_button.setEnabled(True)

    def load_settings(self):
        try:
            with open('settings_jmo.json', 'r') as f:
                settings = json.load(f)
                self.music_folder_path = settings.get("music_folder_path", "")
                self.destination_folder_path = settings.get("destination_folder_path", "")
        except FileNotFoundError:
            pass

    def save_settings(self):
        # Create settings dictionary
        settings = {
            "music_folder_path": self.music_folder_path,
            "destination_folder_path": self.destination_folder_path
        }

        # Save settings to file
        with open('settings_jmo.json', 'w') as f:
            json.dump(settings, f)

    def reset_settings(self):
        #Default settings
        self.music_folder_path = ''
        self.destination_folder_path = ''

        # Reset settings to default
        self.music_folder_label.setText(self.music_folder_path)
        self.destination_folder_label.setText(self.destination_folder_path)

        # Update UI
        self.organize_button.setEnabled(False)
        self.music_folder_select_button.setEnabled(True)
        self.destination_folder_select_button.setEnabled(True)

        # Save settings to file
        self.save_settings()

    def organize_function(self):
        # Variables needed in OrganizeThread
        info = {
            'selected_music_folder_path':self.music_folder_path,
            'selected_destination_folder_path':self.destination_folder_path
        }
        self.organize_thread = OrganizeThread(info)
        self.organize_thread.user_interface_signal.connect(self.user_interface)
        self.organize_thread.number_songs_signal.connect(self.number_songs)
        self.organize_thread.update_progress_signal.connect(self.update_progress)
        self.organize_thread.kill_thread_signal.connect(self.kill_thread)
        self.organize_thread.error_dialogue_signal.connect(self.error_dialogue)
        self.organize_thread.start()

    def user_interface(self, msg):
        # Define a list of UI elements to enable/disable
        ui_elements = [self.destination_folder_select_button, self.music_folder_select_button,
                    self.organize_button, self.reset_button, self.save_button]

        # Check if any window is open
        window_open = self.isWindowOpen()

        # Future reference | checking if anther window is open was giving me problems
        # Set the enabled state of each element based on the value of msg
        enabled = msg and not window_open
        for element in ui_elements:
            element.setEnabled(enabled)

    def number_songs(self, msg):
        self.number_songs_label.setText(f'Number of songs found: {msg}')
        if msg:
            # Initialize progress bar
            self.progress_bar.setValue(0)

    def update_progress(self, msg, error_files):
        self.progress_bar.setValue(int(msg))
        if self.progress_bar.value() == self.progress_bar.maximum():
            self.kill_thread('organize')
            self.error_data(error_files)
            
    def error_data(self, msg):
        if msg and (self.music_error is None or not self.music_error.isVisible()):
            # Disable UI elements
            self.user_interface(False)
            # Music File Error Window
            self.music_error = MusicErrorWindow(msg)
            self.music_error.music_error_signal.connect(self.user_interface)
            self.music_error.show()

    def kill_thread(self, msg):
        if msg == 'organize':
            # Delete OrganizeThread QThread
            del self.organize_thread
            # Re-enable UI elements
            self.user_interface(True)

    def error_dialogue(self, msg):
        if msg == 'no_songs':
            # No songs were found
            dialog = CustomErrorDialog("No songs were found in the selected folder.")
        dialog.exec_()
            
    def initialize_windows(self):
        self.music_error = None

    def isWindowOpen(self):
        # The function returns True if a window is open and False otherwise
        return self.music_error is not None and self.music_error.isVisible()

    def closeEvent(self, event):
        if self.music_error is not None:
            self.music_error.close()

class OrganizeThread(QThread):
    user_interface_signal = pyqtSignal(bool)
    number_songs_signal = pyqtSignal(int)
    update_progress_signal = pyqtSignal(int, list)
    kill_thread_signal = pyqtSignal(str)
    error_dialogue_signal = pyqtSignal(str)

    def __init__(self, info):
        super().__init__()
        self.info = info

    def __del__(self):
        self.wait()

    def run(self):
        # Disable UI elements
        self.user_interface_signal.emit(False)

        #Future Reference | These file types did not work when tested with v2.07: aac, ac3, adts, mp1, ofr, ofs, tta, wv
        extensions = [".aif", ".aiff", ".ape", ".flac", ".m4a", ".m4b", ".m4r", ".mp2", ".mp3", ".mp4", ".mpc", ".ogg", ".opus", ".wav", ".wma"]

        # Generate list of paths to music files
        pathlist = []
        for extension in extensions:
            pathlist.extend(list(Path(self.info['selected_music_folder_path']).glob(f"**/*{extension}")))

        # Update number of songs label
        total_number_of_songs = len(pathlist)
        self.number_songs_signal.emit(total_number_of_songs)

        # Define the artist and album values to search for
        artist_values = ['©art', 'artist', 'author', 'tpe1']
        album_values = ['©alb', 'album', 'talb', 'wm/albumtitle']

        # Check if folder has any songs
        if total_number_of_songs:

            # Initialize a list to store file info for songs with errors
            error_files = []

            # Loop through each song and organize it
            for i, path in enumerate(pathlist):
                # Replace backslashes with forward slashes
                path_in_str = str(path).replace('\\', '/')
                # Get file name from path
                file_name = path_in_str.split("/")[-1]

                # Reset variables
                artist_data = ''
                album_data = ''
                metadata_dict = {}

                try:
                    # Load and extract metadata from the music file
                    metadata = mutagen.File(path_in_str)

                    # Iterate over the metadata items and add them to the dictionary
                    for key, value in metadata.items():
                        metadata_dict[key] = value

                    # Loop through the metadata to find matching artist and album values
                    for key, value in metadata.items():
                        lowercase_key = key.lower()
                        if lowercase_key in artist_values:
                            artist_data = value
                        elif lowercase_key in album_values:
                            album_data = value

                    # Check if artist_data and album_data were found
                    if artist_data == '' or album_data == '':
                        raise Exception("Artist or album data not found")

                    # Convert the metadata values to strings
                    artist = str(artist_data[0]) if isinstance(artist_data[0], ASFUnicodeAttribute) else artist_data[0]
                    album = str(album_data[0]) if isinstance(album_data[0], ASFUnicodeAttribute) else album_data[0]

                    # Remove unwanted characters and whitespace
                    artist = artist.translate(str.maketrans("", "", ':*?<>|')).replace('/', '').replace('\\', '').replace('"', '').replace("'", '').replace('...', '').strip()
                    album = album.translate(str.maketrans("", "", ':*?<>|')).replace('/', '').replace('\\', '').replace('"', '').replace("'", '').replace('...', '').strip()

                    # Construct new location
                    new_location = f"{self.info['selected_destination_folder_path']}/{artist}/{album}"

                    # Create directory and copy file to new location
                    Path(new_location).mkdir(parents=True, exist_ok=True)
                    shutil.copy(path_in_str, f"{new_location}/{file_name}")

                except Exception as e:
                    file_info = {
                        'filename': file_name,
                        'artist_found': artist_data,
                        'album_found': album_data,
                        'metadata_dict': metadata_dict,
                        'error': str(e)
                    }

                    error_files.append(file_info)

                finally:
                    # Update progress bar and send error_files
                    self.update_progress_signal.emit(int((i + 1) / len(pathlist) * 100), error_files)
            
        else:
            # No songs were found
            self.error_dialogue_signal.emit('no_songs')
            # Kill OrganizeThread QThread
            self.kill_thread_signal.emit('organize')

class CustomErrorDialog(QDialog):
    def __init__(self, error_message):
        super().__init__()

        # Hides the default titlebar
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Window title, icon, and size
        self.setWindowTitle('Error')
        self.setWindowIcon(QIcon(':/Octopus.ico'))
        self.resize(250, 100)
        self.center_window()

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

        title_label = QLabel("Error")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        close_button = QPushButton("X")
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet(
            "QPushButton { color: white; background-color: transparent; }"
            "QPushButton:hover { background-color: red; }"
        )
        title_layout.addWidget(close_button)
        close_button.clicked.connect(self.reject)

        title_bar_widget.setLayout(title_layout)

        # Error message label
        error_label = QLabel(error_message)
        layout.addWidget(error_label)
        self.setLayout(layout)

        # Apply stylesheet for red border
        self.setStyleSheet("QDialog { border: 2px solid rgba(255, 152, 152, 1); }")

    def close_dialog(self):
        self.close()

    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

class MusicErrorWindow(QMainWindow):
    music_error_signal = pyqtSignal(bool)

    def __init__(self, error_info):
        super().__init__()

        self.error_info = error_info

        # Setup and show user interface
        self.setup_titlebar()
        self.setup_ui()

    def closeEvent(self, event):
        self.music_error_signal.emit(True)

    def setup_titlebar(self):
        # Create a central widget and set the layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title bar widget
        self.title_bar = QWidget(self)
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(32)

        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon(':/Octopus.ico').pixmap(24, 24))
        title_layout.addWidget(self.icon_label)

        self.title_label = QLabel("Music Error Window")
        self.title_label.setStyleSheet("color: white;")
        title_layout.addWidget(self.title_label)

        title_layout.addStretch()

        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet(
            "QPushButton { color: white; background-color: transparent; }"
            "QPushButton:hover { background-color: red; }"
        )
        title_layout.addWidget(self.close_button)

        title_layout.setAlignment(Qt.AlignRight)

        self.close_button.clicked.connect(self.close)

        layout.addWidget(self.title_bar, 0, Qt.AlignTop)

        # Initialize variables for dragging
        self.draggable = False
        self.offset = QPoint()

    # Mouse events allow the title bar to be dragged around
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() <= self.title_bar.height():
            self.draggable = True
            self.offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self.draggable:
            if event.buttons() & Qt.LeftButton:
                self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = False

    def setup_ui(self):
        # Hides the default titlebar
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Window title, icon, and size
        self.setWindowTitle("Music Error Window")
        self.setWindowIcon(QIcon(':/Octopus.ico'))
        self.resize(700, 500)
        self.center_window()

        # Create group box
        self.group_box = QGroupBox('Error Details', self)
        self.group_box.setGeometry(10, 45, self.width() - 20, self.height() - 50)

        vbox_main_layout = QVBoxLayout(self.group_box)

        vertical_splitter = QSplitter(self.group_box)

        hbox_file_list_top = QHBoxLayout()
        # Create the file list widget on the top
        self.file_list_widget = QListWidget(self)
        self.file_list_widget.currentItemChanged.connect(self.displayDetails)
        hbox_file_list_top.addWidget(self.file_list_widget)
        vertical_splitter.addWidget(self.file_list_widget)

        # Add the text label to the splitter
        text_label = QLabel(self)
        text_label.setText("Files that don't have any metadata are unreadable by mutagen\n\n"
                        "These are the known audio file keys that are being looked for:\n"
                        "(capitalization doesn't matter)\n"
                        "artist_values = ['©art', 'artist', 'author', 'tpe1']\n"
                        "album_values = ['©alb', 'album', 'talb', 'wm/albumtitle']\n\n"
                        "These audio files have missing artist and/or album keys\n"
                        "Either:\n"
                        "- Your files don't have an artist/album name\n"
                        "- New keys need to be added to the program\n"
                        "- Your file is corrupt/tampered with")
        hbox_file_list_top.addWidget(text_label)
        vertical_splitter.addWidget(text_label)

        vbox_main_layout.addWidget(vertical_splitter)

        hbox_file_details = QHBoxLayout()
        # Create the details display widget on the bottom
        self.details_display = QTextEdit(self)
        self.details_display.setReadOnly(True)
        # Set line wrap mode to NoWrap
        self.details_display.setLineWrapMode(QTextEdit.NoWrap)
        hbox_file_details.addWidget(self.details_display)

        vbox_main_layout.addLayout(hbox_file_details)

        # Create the buttons widget
        buttons_widget = QWidget(self)
        hbox_buttons = QHBoxLayout()
        buttons_widget.setLayout(hbox_buttons)
        vbox_main_layout.addWidget(buttons_widget)

        # Create the copy button
        self.copy_button = QPushButton("Copy Bottom", self)
        self.copy_button.clicked.connect(self.copyDetails)
        hbox_buttons.addWidget(self.copy_button)

        # Create the CSV button
        self.csv_button = QPushButton("Generate CSV File", self)
        self.csv_button.clicked.connect(self.generateCSV)
        hbox_buttons.addWidget(self.csv_button)

        # Create the Excel button
        self.excel_button = QPushButton("Generate Excel File", self)
        self.excel_button.clicked.connect(self.generateExcel)
        hbox_buttons.addWidget(self.excel_button)

        # Create the JSON button
        self.json_button = QPushButton("Generate JSON File", self)
        self.json_button.clicked.connect(self.generateJSON)
        hbox_buttons.addWidget(self.json_button)

        self.group_box.setLayout(vbox_main_layout)

        # Populate the file list
        for info in self.error_info:
            file_name = info['filename']
            self.file_list_widget.addItem(file_name)

        # Set the first item as the current row 
        self.file_list_widget.setCurrentRow(0)

    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def displayDetails(self, current_item):
        if current_item is None:
            return

        # Get the selected file name
        selected_file = current_item.text()

        # Find the corresponding error_info
        selected_info = next((info for info in self.error_info if info['filename'] == selected_file), None)

        # Update the details display with file name, error, artist_found, album_found, and metadata information
        if selected_info:
            file_name = selected_info['filename']
            error = selected_info['error']
            artist_found = selected_info['artist_found']
            album_found = selected_info['album_found']
            metadata_dict = selected_info['metadata_dict']

            details_text = f"File Name: {file_name}\n"
            details_text += f"Error: {error}\n"
            if artist_found:
                details_text += f"Artist Found: {artist_found[0]}\n"
            else:
                details_text += f"Artist Found: False\n"
            if album_found:
                details_text += f"Album Found: {album_found[0]}\n\n"
            else:
                details_text += f"Album Found: False\n\n"
            details_text += "Metadata:\n"
            if metadata_dict:
                for key, value in metadata_dict.items():
                    details_text += f"{key}: {value}\n"
            else:
                details_text += "No metadata available\n"

            self.details_display.setPlainText(details_text)

    def copyDetails(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.details_display.toPlainText())

        # Update the button text and color temporarily
        self.copy_button.setText("Success")
        self.copy_button.setStyleSheet("""
            background-color: rgba(255, 152, 152, 1);
            color: black;
        """)

        # Stop any existing timers before creating a new one
        if hasattr(self, "reset_timer"):
            self.reset_timer.stop()

        # Create a new timer to reset the button text and color after 2 seconds
        self.reset_timer = QTimer(self)
        self.reset_timer.timeout.connect(self.resetCopyButton)
        self.reset_timer.start(1000)

    def resetCopyButton(self):
        self.copy_button.setText("Copy Bottom")
        self.copy_button.setStyleSheet("")

    def generateCSV(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if file_name:
            try:
                # Collect all unique metadata keys
                metadata_keys = set()
                for info in self.error_info:
                    metadata_keys.update(info['metadata'].keys())

                # Sort metadata keys
                metadata_keys = sorted(metadata_keys)

                # Create a list to store all rows
                rows = []

                # Generate rows
                for info in self.error_info:
                    row = [
                        info['filename'],
                        info['error'],
                        info['artist_found'],
                        info['album_found']
                    ]

                    # Generate metadata values for the current row
                    metadata_values = [f"{key} : {info['metadata'].get(key)}" for key in metadata_keys if key in info['metadata']]

                    # Add the metadata values to the row
                    row.extend(metadata_values)

                    # Add the row to the list
                    rows.append(row)

                # Determine the maximum number of columns for the header
                max_columns = max(len(row) for row in rows)

                # Fill in missing values in each row with 'None' to ensure equal length
                for row in rows:
                    row.extend(['None'] * (max_columns - len(row)))

                # Determine the column headers based on the maximum row length
                header = ['File Name', 'Error', 'Artist Found', 'Album Found']
                header.extend(['Metadata {}'.format(i + 1) for i in range(max_columns - len(header))])

                # Write to the CSV file
                with open(file_name, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(header)
                    writer.writerows(rows)

                self.showSuccessMessage("CSV file generated successfully.")
            except Exception as e:
                self.showErrorMessage("An error occurred while generating the CSV file.")
        else:
            self.showErrorMessage("Please provide a valid file name for the CSV.")

    def generateExcel(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Excel", "", "Excel Files (*.xlsx)")
        if file_name:
            try:
                # Create a new workbook
                wb = openpyxl.Workbook()
                ws = wb.active

                # Generate rows
                rows = []
                for info in self.error_info:
                    row = [
                        info['filename'],
                        info['error'],
                        info['artist_found'],
                        info['album_found']
                    ]

                    # Generate metadata values for the current row
                    metadata_values = [f"{key} : {info['metadata'].get(key)}" for key in sorted(info['metadata'].keys())]
                    row.extend(metadata_values)

                    # Add the row to the list
                    rows.append(row)

                # Determine the maximum number of columns for the header
                max_columns = max(len(row) for row in rows)

                # Fill in missing values in each row with 'None' to ensure equal length
                for row in rows:
                    row.extend(['None'] * (max_columns - len(row)))

                # Determine the column headers based on the maximum row length
                header = ['File Name', 'Error', 'Artist Found', 'Album Found']
                header.extend(['Metadata {}'.format(i + 1) for i in range(max_columns - len(header))])

                # Write the header row
                ws.append(header)

                # Write the data rows
                for row in rows:
                    ws.append(row)

                # Auto-size columns for better visibility
                for column in ws.columns:
                    max_length = 0
                    column = [cell for cell in column]
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(cell.value)
                        except:
                            pass
                    adjusted_width = (max_length + 2)
                    ws.column_dimensions[column[0].column_letter].width = adjusted_width

                # Save the Excel file
                wb.save(file_name)

                self.showSuccessMessage("Excel file generated successfully.")
            except Exception as e:
                self.showErrorMessage("An error occurred while generating the Excel file.")
        else:
            self.showErrorMessage("Please provide a valid file name for the Excel file.")

    def generateJSON(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON Files (*.json)")
        if file_name:
            try:
                data = []
                for info in self.error_info:
                    row_data = {
                        'File Name': info['filename'],
                        'Error': info['error'],
                        'Artist Found': info['artist_found'],
                        'Album Found': info['album_found'],
                        'Metadata': info['metadata']
                    }
                    data.append(row_data)

                with open(file_name, 'w') as file:
                    json.dump(data, file, indent=4)

                self.showSuccessMessage("JSON file generated successfully.")
            except Exception as e:
                self.showErrorMessage("An error occurred while generating the JSON file.")
        else:
            self.showErrorMessage("Please provide a valid file name for the JSON file.")

    def showSuccessMessage(self, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Success")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec_()

    def showErrorMessage(self, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.exec_()

# Create and run application
if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = JellyfinMusicOrganizer()
    app.exec_()