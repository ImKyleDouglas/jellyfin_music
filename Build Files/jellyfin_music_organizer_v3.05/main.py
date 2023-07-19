from PyQt5.QtWidgets import QApplication
import qdarkstyle

# Other classes within files
from music_organizer import MusicOrganizer

# Create and run application
if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MusicOrganizer()
    app.exec_()
    