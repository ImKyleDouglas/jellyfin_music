from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSizeGrip,
                            QLabel, QPushButton, QSizePolicy, QListWidget,
                            QTextEdit, QApplication, QFileDialog)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QIcon
import openpyxl
import json
import csv

class MusicErrorWindow(QWidget):
    windowOpened = pyqtSignal(bool)
    windowClosed = pyqtSignal(bool)
    custom_dialog_signal = pyqtSignal(str)

    def __init__(self, error_files):
        super().__init__()

        # Version Control
        self.version = '3.06'

        self.error_files = error_files

        # Setup and show user interface
        self.setup_ui()

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

        self.title_label = QLabel(f"Music Error Window v{self.version}")
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
        # Window title, icon, and size
        self.setWindowTitle(f"Music Error Window v{self.version}")
        self.setWindowIcon(QIcon(':/Octopus.ico'))

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

        # QHBoxLayout setup for file list and test box
        hbox_list_text_layout = QHBoxLayout()
        vbox_main_layout.addLayout(hbox_list_text_layout)

        # Create the file list widget on the top
        self.file_list_widget = QListWidget(self)
        hbox_list_text_layout.addWidget(self.file_list_widget)
        self.file_list_widget.currentItemChanged.connect(self.displayDetails)

        # QLabel for text details
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
        hbox_list_text_layout.addWidget(text_label)

        # Create the details display widget on the bottom
        self.details_display = QTextEdit(self)
        self.details_display.setReadOnly(True)
        self.details_display.setLineWrapMode(QTextEdit.NoWrap)
        vbox_main_layout.addWidget(self.details_display)

        # QHBoxLayout setup for buttons and grip
        hbox_buttons_grip_layout = QHBoxLayout()
        vbox_main_layout.addLayout(hbox_buttons_grip_layout)

        # Create the copy button
        self.copy_button = QPushButton("Copy Bottom")
        self.copy_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        hbox_buttons_grip_layout.addWidget(self.copy_button)
        self.copy_button.clicked.connect(self.copyDetails)

        # Create the CSV button
        self.txt_button = QPushButton("Generate TXT File")
        self.txt_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        hbox_buttons_grip_layout.addWidget(self.txt_button)
        self.txt_button.clicked.connect(self.generateTXT)

        # Create the CSV button
        self.csv_button = QPushButton("Generate CSV File")
        self.csv_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        hbox_buttons_grip_layout.addWidget(self.csv_button)
        self.csv_button.clicked.connect(self.generateCSV)

        # Create the Excel button
        self.excel_button = QPushButton("Generate Excel File")
        self.excel_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        hbox_buttons_grip_layout.addWidget(self.excel_button)
        self.excel_button.clicked.connect(self.generateExcel)

        # Create the JSON button
        self.json_button = QPushButton("Generate JSON File")
        self.json_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        hbox_buttons_grip_layout.addWidget(self.json_button)
        self.json_button.clicked.connect(self.generateJSON)

        # Add resizing handles
        self.bottom_right_grip = QSizeGrip(self)
        self.bottom_right_grip.setToolTip('Resize window')
        hbox_buttons_grip_layout.addWidget(self.bottom_right_grip, 0, Qt.AlignBottom | Qt.AlignRight)

        # Populate QListWidget
        self.populate_list_widget()

    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def populate_list_widget(self):
        # Populate the file list
        for info in self.error_files:
            file_name = info['file_name']
            self.file_list_widget.addItem(file_name)

        # Set the first item as the current row 
        self.file_list_widget.setCurrentRow(0)

    def displayDetails(self, current_item):
        if current_item is None:
            return

        # Get the selected file name
        selected_file = current_item.text()

        # Find the corresponding error_info
        selected_info = next((info for info in self.error_files if info['file_name'] == selected_file), None)

        # Update the details display with file name, error, artist_found, album_found, and metadata information
        if selected_info:
            file_name = selected_info['file_name']
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

        # Stop any existing copy timers before creating a new one
        if hasattr(self, "reset_copy_timer"):
            self.reset_copy_timer.stop()

        # Create a new copy timer to reset the button text and color after 1 seconds
        self.reset_copy_timer = QTimer(self)
        self.reset_copy_timer.timeout.connect(self.resetCopyButton)
        self.reset_copy_timer.start(1000)

    def resetCopyButton(self):
        self.copy_button.setText("Copy Bottom")
        self.copy_button.setStyleSheet("")

    def generateTXT(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save TXT", "", "Text Files (*.txt)")
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as file:
                    for info in self.error_files:
                        file.write(f"File Name: {info['file_name']}\n")
                        file.write(f"Error: {info['error']}\n")
                        if info['artist_found']:
                            file.write(f"Artist Found: {info['artist_found'][0]}\n")
                        else:
                            file.write("Artist Found: False\n")
                        if info['album_found']:
                            file.write(f"Album Found: {info['album_found'][0]}\n\n")
                        else:
                            file.write("Album Found: False\n\n")
                        file.write("Metadata:\n")
                        metadata_dict = info['metadata_dict']
                        if metadata_dict:
                            for key, value in metadata_dict.items():
                                file.write(f"{key}: {value}\n")
                        else:
                            file.write("No metadata available\n")
                        file.write("\n")

                    # Update the button text and color temporarily
                    self.txt_button.setText("Success")
                    self.txt_button.setStyleSheet("""
                        background-color: rgba(255, 152, 152, 1);
                        color: black;
                    """)

                    # Stop any existing txt timers before creating a new one
                    if hasattr(self, "reset_txt_timer"):
                        self.reset_txt_timer.stop()

                    # Create a new txt timer to reset the button text and color after 1 seconds
                    self.reset_txt_timer = QTimer(self)
                    self.reset_txt_timer.timeout.connect(self.resetTXTButton)
                    self.reset_txt_timer.start(1000)

            except Exception as e:
                self.custom_dialog_signal.emit('An error occurred while generating the TXT file.')
        else:
            self.custom_dialog_signal.emit('Please provide a valid file name for the TXT file.')

    def resetTXTButton(self):
        self.txt_button.setText("Generate TXT File")
        self.txt_button.setStyleSheet("")

    def generateCSV(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if file_name:
            try:
                # Create a list to store all rows
                rows = []

                # Determine the maximum number of metadata fields
                max_metadata_fields = max(len(info['metadata_dict']) for info in self.error_files)

                # Generate rows
                for info in self.error_files:
                    metadata_dict = {str(key): str(value) for key, value in info['metadata_dict'].items()}

                    # Get the first value from the list if available
                    artist_found = info['artist_found'][0] if info['artist_found'] else "None"
                    album_found = info['album_found'][0] if info['album_found'] else "None"

                    # Create an empty row
                    row = [info['file_name'], info['error'], artist_found, album_found]

                    # Generate metadata keys and values for the current row
                    metadata_keys = list(metadata_dict.keys())
                    metadata_values = list(metadata_dict.values())

                    # Fill in missing metadata fields with 'None'
                    metadata_keys.extend(['None'] * (max_metadata_fields - len(metadata_keys)))
                    metadata_values.extend(['None'] * (max_metadata_fields - len(metadata_values)))

                    # Add the metadata keys and values to the row
                    for key, value in zip(metadata_keys, metadata_values):
                        row.append(key)
                        row.append(value)

                    # Add the row to the list
                    rows.append(row)

                # Determine the maximum number of columns for the header
                max_columns = max(len(row) for row in rows)

                # Fill in missing values in each row with 'None' to ensure equal length
                for row in rows:
                    row.extend(['None'] * (max_columns - len(row)))

                # Determine the column headers based on the maximum row length
                header = ['File Name', 'Error', 'Artist Found', 'Album Found']
                header.extend([f"Key {i//2 + 1}" if i % 2 == 0 else f"Value {i//2 + 1}" for i in range(max_metadata_fields*2)])

                # Write to the CSV file with UTF-8 encoding
                with open(file_name, mode='w', encoding='utf-8-sig', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(header)
                    writer.writerows(rows)

                # Update the button text and color temporarily
                self.csv_button.setText("Success")
                self.csv_button.setStyleSheet("""
                    background-color: rgba(255, 152, 152, 1);
                    color: black;
                """)

                # Stop any existing csv timers before creating a new one
                if hasattr(self, "reset_csv_timer"):
                    self.reset_csv_timer.stop()

                # Create a new csv timer to reset the button text and color after 1 seconds
                self.reset_csv_timer = QTimer(self)
                self.reset_csv_timer.timeout.connect(self.resetCSVButton)
                self.reset_csv_timer.start(1000)

            except Exception as e:
                self.custom_dialog_signal.emit('An error occurred while generating the CSV file.')
        else:
            self.custom_dialog_signal.emit('Please provide a valid file name for the CSV.')

    def resetCSVButton(self):
        self.csv_button.setText("Generate CSV File")
        self.csv_button.setStyleSheet("")

    def generateExcel(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Excel", "", "Excel Files (*.xlsx)")
        if file_name:
            try:
                # Create a new workbook
                wb = openpyxl.Workbook()
                ws = wb.active

                # Generate rows
                rows = []
                max_metadata_columns = 0
                for info in self.error_files:
                    metadata_dict = {str(key): str(value) for key, value in info['metadata_dict'].items()}

                    # Extract values from the list if available
                    artist_found = info['artist_found'][0] if info['artist_found'] else "None"
                    album_found = info['album_found'][0] if info['album_found'] else "None"

                    row = [
                        info['file_name'],
                        info['error'],
                        artist_found,
                        album_found
                    ]

                    # Generate metadata keys and values for the current row
                    metadata_keys = list(metadata_dict.keys())
                    metadata_values = list(metadata_dict.values())

                    # Convert problematic values to strings before appending to the row
                    row = [str(cell) if isinstance(cell, list) else cell for cell in row]
                    metadata_values = [str(value) if isinstance(value, list) else value for value in metadata_values]

                    # Add the metadata keys and values to the row
                    for key, value in zip(metadata_keys, metadata_values):
                        row.append(key)
                        row.append(value)

                    # Add the row to the list
                    rows.append(row)

                    # Update the maximum number of metadata columns
                    max_metadata_columns = max(max_metadata_columns, len(metadata_dict) * 2)

                # Determine the maximum number of columns for the header
                max_columns = 4 + max_metadata_columns

                # Fill in missing values in each row with 'None' to ensure equal length
                for row in rows:
                    row.extend(['None'] * (max_columns - len(row)))

                # Determine the column headers based on the maximum row length
                header = ['File Name', 'Error', 'Artist Found', 'Album Found']
                header.extend([f"Key {i//2 + 1}" if i % 2 == 0 else f"Value {i//2 + 1}" for i in range(0, max_columns - 4)])

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

                # Update the button text and color temporarily
                self.excel_button.setText("Success")
                self.excel_button.setStyleSheet("""
                    background-color: rgba(255, 152, 152, 1);
                    color: black;
                """)

                # Stop any existing excel timers before creating a new one
                if hasattr(self, "reset_excel_timer"):
                    self.reset_excel_timer.stop()

                # Create a new excel timer to reset the button text and color after 1 seconds
                self.reset_excel_timer = QTimer(self)
                self.reset_excel_timer.timeout.connect(self.resetExcelButton)
                self.reset_excel_timer.start(1000)

            except Exception as e:
                self.custom_dialog_signal.emit('An error occurred while generating the Excel file.')
        else:
            self.custom_dialog_signal.emit('Please provide a valid file name for the Excel file.')

    def resetExcelButton(self):
        self.excel_button.setText("Generate Excel File")
        self.excel_button.setStyleSheet("")

    def generateJSON(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON Files (*.json)")
        if file_name:
            try:
                data = []
                for info in self.error_files:
                    metadata_dict = {str(key): str(value) for key, value in info['metadata_dict'].items()}
                    
                    artist_found = info['artist_found'][0] if info['artist_found'] else "False"
                    album_found = info['album_found'][0] if info['album_found'] else "False"
                    
                    row_data = {
                        'filename': info['file_name'],
                        'error': info['error'],
                        'artist_found': artist_found,
                        'album_found': album_found,
                        'metadata_dict': metadata_dict
                    }
                    data.append(row_data)

                with open(file_name, 'w') as file:
                    json.dump(data, file, indent=4)

                # Update the button text and color temporarily
                self.json_button.setText("Success")
                self.json_button.setStyleSheet("""
                    background-color: rgba(255, 152, 152, 1);
                    color: black;
                """)

                # Stop any existing json timers before creating a new one
                if hasattr(self, "reset_json_timer"):
                    self.reset_json_timer.stop()

                # Create a new json timer to reset the button text and color after 1 seconds
                self.reset_json_timer = QTimer(self)
                self.reset_json_timer.timeout.connect(self.resetJSONButton)
                self.reset_json_timer.start(1000)

            except Exception as e:
                self.custom_dialog_signal.emit('An error occurred while generating the JSON file.')
        else:
            self.custom_dialog_signal.emit('Please provide a valid file name for the JSON file.')

    def resetJSONButton(self):
        self.json_button.setText("Generate JSON File")
        self.json_button.setStyleSheet("")

