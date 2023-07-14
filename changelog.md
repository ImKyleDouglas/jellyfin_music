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
