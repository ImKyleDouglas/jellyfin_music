from PyQt5.QtCore import QThread, pyqtSignal
from pathlib import Path
import mutagen
from mutagen.asf import ASFUnicodeAttribute
import shutil
from resources_rc import *

class OrganizeThread(QThread):
    number_songs_signal = pyqtSignal(int)
    music_progress_signal = pyqtSignal(int)
    kill_thread_signal = pyqtSignal(str)
    custom_dialog_signal = pyqtSignal(str)
    organize_finish_signal = pyqtSignal(dict)

    def __init__(self, info):
        super().__init__()
        self.info = info

    def __del__(self):
        self.wait()

    def run(self):
        # Future Reference | These file types did not work when tested with v2.07: aac, ac3, adts, mp1, ofr, ofs, tta, wv
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

            # Initialize a dictionary to store file info for songs with errors
            recall_files = {
                'error_files': [],
                'replace_skip_files': []
            }

            # Dont include replace_skip_files in progress bar
            i = 0

            # Loop through each song and organize it
            for path in pathlist:
                # Replace backslashes with forward slashes
                path_in_str = str(path).replace('\\', '/')
                # Get file name from path
                file_name = path_in_str.split("/")[-1]

                # Reset variables
                artist_data = ''
                album_data = ''
                metadata_dict = {}
                file_info = {}

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

                    # Check if the file already exists in the new location
                    if Path(f"{new_location}/{file_name}").exists():
                        file_info = {
                            'file_name': file_name,
                            'new_location': new_location,
                            'path_in_str': path_in_str,
                            'error': 'File already exists in the destination folder'
                        }

                        recall_files['replace_skip_files'].append(file_info)
                    else:
                        # Create directory and copy file to new location
                        Path(new_location).mkdir(parents=True, exist_ok=True)
                        shutil.copy(path_in_str, f"{new_location}/{file_name}")

                except Exception as e:
                    file_info = {
                        'file_name': file_name,
                        'artist_found': artist_data,
                        'album_found': album_data,
                        'metadata_dict': metadata_dict,
                        'error': str(e)
                    }

                    recall_files['error_files'].append(file_info)

                finally:
                    # Update progress bar if no error or 'File already exists'
                    if not file_info.get('error') or file_info.get('error') != 'File already exists in the destination folder':
                        i += 1
                        self.music_progress_signal.emit(int(i / len(pathlist) * 100))

            # Send recall_files
            self.organize_finish_signal.emit(recall_files)

        else:
            # No songs were found
            self.custom_dialog_signal.emit('No songs were found in the selected folder.')
            # Kill OrganizeThread QThread
            self.kill_thread_signal.emit('organize')
