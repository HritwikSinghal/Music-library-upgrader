import os
import re
from os.path import isdir
from os.path import isfile

from Base import DownloadSong
from Base import tools


def inputSongDir(test=0):
    while True:
        if test == 1:
            songDir = r'C:\Users\hritwik\Pictures\Camera Roll'
        else:
            songDir = input("Enter song dir:  ")

        if isdir(songDir):
            print("Song dir is: ", songDir)
            return songDir
        else:
            print("No such Dir exist, Please enter Dir again...")


def getSongList(files):
    songs = []
    for x in files:
        x = re.findall(r'(.+\.mp3)', x)
        if len(x) != 0:
            songs.append(x[0])
    return songs


def handleSongsInDir(song_dir, files, sub_dir_flag=-1, test=0):
    print('Now in ', song_dir)

    if sub_dir_flag == 0 and int(input("Do you upgrade songs in " + song_dir + " ?\n1 == Yes, 0 == NO\n")) == 0:
        return

    log_file = tools.createLogFile(song_dir)
    song_list = getSongList(files)

    try:
        print("Creating downloads directory in current folder...")
        download_dir = os.path.join(song_dir, 'Downloaded_songs')
        os.mkdir(download_dir)
    except FileExistsError:
        print("\nSince download directory already exists, I will save songs in it.")

    # noinspection PyUnboundLocalVariable
    print("Download dir =", download_dir, '\n')

    for song in song_list:
        song_with_path = os.path.join(song_dir, song)

        song_name = tools.removeBitrate(song)
        song_name = tools.removeGibberish(song_name)
        song_name = song_name.replace('.mp3', '')
        song_name = song_name.strip()
        print("Song Name: ", song_name)

        try:
            DownloadSong.start(song_name, song_with_path, download_dir, log_file, test=test)

        except:
            tools.writeAndPrintLog(log_file, "\nError Downloading song={0}\n".format(song_name), test=test)


def start(test=0):
    song_dir = inputSongDir(test)

    if test == 1:
        sub_dir_flag = -1
    else:
        sub_dir_flag = int(input("\nDo you want to run this program in all sub-dirs?\n"
                                 "1 == Yes,\n-1 == No,\n0 == Ask in each Dir\n"))

    if sub_dir_flag == -1:
        print("Only upgrading in:", song_dir + "...\n")

        files = [
            x
            for x in os.listdir(song_dir)
            if isfile(os.path.join(song_dir, x))
        ]

        handleSongsInDir(song_dir, files, test=test)

    else:
        print("Walking down ", song_dir, "\b...")
        for curr_dir, sub_dirs, files in os.walk(song_dir, topdown=True):
            handleSongsInDir(curr_dir, files, sub_dir_flag, test=test)
