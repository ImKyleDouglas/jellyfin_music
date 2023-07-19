# Jellyfin Music Organizer v3.05

Pushed to GitHub on July 19, 2023

* All windows can now dynamically expand and contract
* All windows have a grip in the bottom right to expand the window size
* All close buttons, minimize buttons, and grips now have a tool tip that appear on hover
* Splitter on Music Error WIndow removed as it is no longer needed
* Settings window added
* Settings buttons to save and reset on music_organizer.py moved to the settings window
* You can now mute all sounds in the settings window

# Jellyfin Music Organizer v3.04

Pushed to GitHub on July 17, 2023

* Progress bar function only updates progress bar percentage and style now. Nothing else. Also, every time the progress bar is updated, it will only apply a new style sheet if the current style sheet doesn't equal the desired style sheet
* TXT, CSV, Excel, and JSON buttons now change color if the file was successfuly built
* Changed 'filename' to 'file_name' in error_files dictionary for orgainize_thread.py and music_error_window.py
* OrganizeThread reconstructed to work with new recall_files dictionary
* OrganizeThread progress bar only updates if the file is not put in replace_skip_files dictionary
* Progress bar organize_progress function is triggered and resets to zero after hitting the organize button
* Function kill_thread will only attempt to kill the given thread if it exists
* Main window no longer fully disables, only the user interface including the close button. windowEnabled and windowDisabled removed as they are no longer needed
* Replace or Skip window feature added. After you hit the 'Organize' button, if the desired file location already has that file name, a window will pop up asking you if you want to replace or skip the selected file. You can also 'Skip All' or 'Replace All'. Progress bar shows progress of only the entries in the Replace or Skip window
* Fixed a bug where the program would crash if you tried to drag/move a window without a draggable attribute using mouseMoveEvent

# Jellyfin Music Organizer v3.03

Pushed to GitHub on July 14, 2023

* Added version in the title of every window
* Fixed a bug where if the 100% completion and error audio were playing at the same time, the program would crash
* Added a generate TXT file option in the Music Error Window
* Fixed JSON artist_found and album_found values from either giving a list or empty string to the fisrt list item or 'False' otherwise
* Fixed CSV and Excel artist and album names from giving a list value instead of a string
* Changed CSV and Excel header from Metadata 1, Metadata 2 to Key 1, Value 1, Key 2, Value 2. This required all rows to be reworked
* Removed Success windows from TXT, CSV, Excel, JSON files

# Jellyfin Music Organizer v3.02

Pushed to GitHub on Never

* Progress bar for music organizer changes color at 100% completion
* Main window UI elements on/off state reverted back to a previous update due to multiple errors and complication in the code. A disable feature was added to replace this. If the Music Error Window is open, then the main window will be disabled
* Fixed success/fail button messages for csvm excel, and json in the Music Error Window
* Added sound support. When a notification or error report occurs, a ding sound will be played. A complete sound will be played when the progress bar reaches 100%
* If a new music or destination folder is selected, then the progress bar will reset to zero and its style will be restored. The number of songs label will also be reset
* Every class was put into its own py file
* Fixed a bug where you were able to click the organize button without selecting both a music and destination folder

# Jellyfin Music Organizer v3.01

Pushed to GitHub on July 12, 2023

* Fixed csv, excel, and json files not properly forming from Music Error Window

# changelog.md Started
