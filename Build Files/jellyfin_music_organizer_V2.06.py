from PyQt5.QtWidgets import QApplication, QMainWindow, QGroupBox, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QProgressBar, QFileDialog, QHBoxLayout, QFrame, QWidget
from PyQt5.QtCore import QThread, pyqtSignal, QRegExp, Qt, QPoint
from PyQt5.QtGui import QIcon, QRegExpValidator
from pathlib import Path
import qdarkstyle
import mutagen
import json
from resources_rc import *

class JellyfinMusicOrganizer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Hides the default titlebar
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Window title, icon, and size
        self.setWindowTitle('Jellyfin Music Organizer')
        self.setWindowIcon(QIcon(':/Octopus.ico'))
        self.resize(400, 285)
        self.center_window()

        # Set default settings
        self.folder_path = ''
        self.file_extension = '.m4a'
        self.dest_folder_name = 'Organized to be Transferred'

        # Load settings from file if it exists
        self.load_settings()

        # Setup and show user interface
        self.setup_titlebar()
        self.setup_ui()
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

        self.title_label = QLabel("Jellyfin Music Organizer")
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
        # Create group box
        self.group_box = QGroupBox('Music Organizer', self)
        self.group_box.setGeometry(10, 45, self.width() - 20, self.height() - 50)

        vbox_music_organizer = QVBoxLayout()

        hbox_folder_select = QHBoxLayout()
        # Create folder select button
        self.folder_select_button = QPushButton('Select Folder')
        self.folder_select_button.clicked.connect(self.select_folder)
        hbox_folder_select.addWidget(self.folder_select_button)

        vbox_music_organizer.addLayout(hbox_folder_select)

        hbox_folder_label = QHBoxLayout()
        # Create folder label
        self.folder_label = QLabel(self.folder_path)
        hbox_folder_label.addWidget(self.folder_label)

        vbox_music_organizer.addLayout(hbox_folder_label)

        hbox_file_ext = QHBoxLayout()
        # Create file extension dropdown menu
        self.file_ext_label = QLabel('File Extension')
        hbox_file_ext.addWidget(self.file_ext_label)
        self.file_ext_dropdown = QComboBox()
        self.file_ext_dropdown.addItems([".aac", ".aif", ".aiff", ".ape", ".ac3", ".flac", ".m4a", ".mp3", ".mp4",
                                        ".mpc", ".mpp", ".ofs", ".ofr", ".ogg", ".tta", ".wav", ".wma", ".wv"])
        self.file_ext_dropdown.setCurrentText(self.file_extension)
        hbox_file_ext.addWidget(self.file_ext_dropdown, 1)

        vbox_music_organizer.addLayout(hbox_file_ext)

        hbox_dest_folder = QHBoxLayout()
        # Create destination folder label
        self.dest_folder_label = QLabel('Destination Folder Name')
        hbox_dest_folder.addWidget(self.dest_folder_label)
        # Create destination folder input
        self.dest_folder_input = QLineEdit()
        # Create QRegExp that matches any character that is not alphanumeric or \ / : * ? " < > |
        reg_ex = QRegExp("[^\\\\/:*?\"<>|]+")
        # Create QRegExpValidator with the regex
        validator = QRegExpValidator(reg_ex, self.dest_folder_input)
        # Set the validator for the QLineEdit widget
        self.dest_folder_input.setValidator(validator)
        self.dest_folder_input.setText(self.dest_folder_name)
        hbox_dest_folder.addWidget(self.dest_folder_input, 1)

        vbox_music_organizer.addLayout(hbox_dest_folder)

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
        if not self.folder_path or self.dest_folder_name == '':
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

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Music Folder')
        if folder_path:
            self.folder_path = folder_path
            self.folder_label.setText(self.folder_path)
            self.organize_button.setEnabled(True)

    def load_settings(self):
        try:
            with open('settings_jmo.json', 'r') as f:
                settings = json.load(f)
                self.folder_path = settings.get("folder_path", "")
                self.file_extension = settings.get("file_ext_dropdown", ".m4a")
                self.dest_folder_name = settings.get("destination_name", "Organized to be Transferred")
        except FileNotFoundError:
            pass

    def save_settings(self):
        # Create settings dictionary
        settings = {
            "folder_path": self.folder_path,
            "file_ext_dropdown": self.file_ext_dropdown.currentText(),
            "destination_name": self.dest_folder_input.text()
        }

        # Save settings to file
        with open('settings_jmo.json', 'w') as f:
            json.dump(settings, f)

    def reset_settings(self):
        #Default settings
        self.folder_path = ''
        self.file_extension = '.m4a'
        self.dest_folder_name = 'Organized to be Transferred'

        # Reset settings to default
        self.folder_label.setText(self.folder_path)
        self.file_ext_dropdown.setCurrentText(self.file_extension)
        self.dest_folder_input.setText(self.dest_folder_name)

        # Update UI
        self.organize_button.setEnabled(False)
        self.dest_folder_input.setEnabled(True)
        self.file_ext_dropdown.setEnabled(True)
        self.folder_select_button.setEnabled(True)

        # Save settings to file
        self.save_settings()

    def organize_function(self):
        # Variables needed in OrganizeThread
        info = {
            'selected_destination_name':self.dest_folder_input.text(),
            'selected_extension':self.file_ext_dropdown.currentText(),
            'selected_folder_path':self.folder_path
        }
        self.organize_thread = OrganizeThread(info)
        self.organize_thread.user_interface_signal.connect(self.user_interface)
        self.organize_thread.number_songs_signal.connect(self.number_songs)
        self.organize_thread.update_progress_signal.connect(self.update_progress)
        self.organize_thread.start()

    def user_interface(self, msg):
        # Define a list of UI elements to enable/disable
        ui_elements = [self.dest_folder_input, self.file_ext_dropdown, self.folder_select_button,
                    self.organize_button, self.reset_button, self.save_button]
        
        # Set the enabled state of each element based on the value of msg
        enabled = msg == 'On'
        for element in ui_elements:
            element.setEnabled(enabled)

    def number_songs(self, msg):
        self.number_songs_label.setText(f'Number of songs found: {msg}')
        if msg:
            # Initialize progress bar
            self.progress_bar.setValue(0)

    def update_progress(self, msg):
        self.progress_bar.setValue(int(msg))
        if self.progress_bar.value() == self.progress_bar.maximum():
            del self.organize_thread
            # Re-enable UI elements
            self.user_interface('On')

class OrganizeThread(QThread):
    user_interface_signal = pyqtSignal(str)
    number_songs_signal = pyqtSignal(int)
    update_progress_signal = pyqtSignal(int)

    def __init__(self, info):
        super().__init__()
        self.info = info

    def __del__(self):
        self.wait()

    def run(self):
        # Disable UI elements
        self.user_interface_signal.emit('Off')

        # Generate list of paths to music files
        pathlist = list(Path(self.info['selected_folder_path']).glob(f"**/*{self.info['selected_extension']}"))

        # Update number of songs label
        total_number_of_songs = len(pathlist)
        self.number_songs_signal.emit(total_number_of_songs)

        # Check if folder has any songs
        if total_number_of_songs:

            # Loop through each song and organize it
            for i, path in enumerate(pathlist):
                # Replace backslashes with forward slashes
                path_in_str = str(path).replace('\\', '/')
                # Get file name from path
                file_name = path_in_str.split("/")[-1]
                # Get artist and album from metadata
                metadata = mutagen.File(path_in_str)
                artist = metadata.get('©ART', ['Unknown Artist'])[0].replace('/', '').replace('\\', '').strip()
                album = metadata.get('©alb', ['Unknown Album'])[0].replace('/', '').replace('\\', '').strip()
                # Construct new location
                new_location = f"./{self.info['selected_destination_name']}/{artist}/{album}"
                new_location = new_location.translate(str.maketrans("", "", ':*?<>|'))
                new_location = new_location.replace('...', '')
                # Create directory and move file to new location
                Path(new_location).mkdir(parents=True, exist_ok=True)
                Path(path_in_str).replace(f"{new_location}/{file_name}")
                # Update progress bar
                self.update_progress_signal.emit(int((i + 1) / len(pathlist) * 100))

        else:
            # Set progress at 100%
            self.update_progress_signal.emit(100)

# Create and run application
if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = JellyfinMusicOrganizer()
    app.exec_()