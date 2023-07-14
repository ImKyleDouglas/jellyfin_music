from PyQt5.QtCore import QThread, pyqtSignal
from pathlib import Path
import mutagen
from mutagen.asf import ASFUnicodeAttribute
import shutil
import os
from PyQt5.QtWidgets import QMessageBox
from resources_rc import *

class OrganizeThread(QThread):
    number_songs_signal = pyqtSignal(int)
    update_progress_signal = pyqtSignal(int, list)
    kill_thread_signal = pyqtSignal(str)
    dialogue_message_signal = pyqtSignal(str)

    def __init__(self, info):
        super().__init__()
        self.info = info

    def __del__(self):
        self.wait()

    def run(self):
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
            self.dialogue_message_signal.emit('No songs were found in the selected folder.')
            # Kill OrganizeThread QThread
            self.kill_thread_signal.emit('organize')
