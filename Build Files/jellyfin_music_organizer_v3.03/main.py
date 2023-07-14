from PyQt5.QtWidgets import QApplication
import qdarkstyle

# Other classes within files
from jellyfin_music_organizer import JellyfinMusicOrganizer

# Create and run application
if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = JellyfinMusicOrganizer()
    app.exec_()
    