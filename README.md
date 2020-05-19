# Music-library-upgrader

This program is in early stages so it may download wrong song sometimes. So just download it manually or change song nome and run program again.

This program will upgrade the songs in your folder in 320Kbps (or 128Kbps if 320Kbps is not on server) from saavn.

The purpose of this project is to upgrade old songs which are generally in 32Kbps and have no tags. This will search for song name on saavn and download appropriate song from it (and then append tags to it). If it cannot find the song itself from web, it will ask user to select appropiriate song to download.

It will store downloaded songs of each dir in folder named 'Downloaded_songs'
which will be located in the folder itself.

Installation:

Clone this repository using
```sh
$ git clone https://github.com/HritwikSinghal/Music-library-upgrader
```
Enter the directory and install all the requirements using
```sh
$ pip3 install -r requirements.txt
```
Run the app using
```sh
$ python3 Music-library-upgrader.py
```


**SS:** 

https://imgur.com/a/JxLgqY6
