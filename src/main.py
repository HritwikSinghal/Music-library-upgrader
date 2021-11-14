import os
import re
from os.path import isdir
from os.path import isfile

from src import downloadSong
from src import tools


def inputSongDir(test=0):
    while True:
        if test:
            songDir = r'/home/hritwik/Music/Old_Songs_OLD/Rafi_test'
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

    if not sub_dir_flag and not int(input("Do you upgrade songs in " + song_dir + " ?\n1 == Yes, 0 == NO\n")):
        return

    log_file = tools.createLogFile(song_dir)
    song_list = getSongList(files)

    print("Creating downloads and done directory in current folder...")

    download_dir = os.path.join(song_dir, 'Downloaded_songs')
    done_dir = os.path.join(song_dir, 'Done')

    try:
        os.mkdir(download_dir)
        os.mkdir(done_dir)
    except FileExistsError:
        print(
            "\n ==================== Since download directory already exists, I will save songs in it. ==================== ")

    print("Download dir =", download_dir, '\n')

    for song in song_list:
        try:
            downloadSong.start(song, song_dir, download_dir, log_file, test=test)
        except:
            print(" ==================== There Was Some Error Downloading {0} ==================== ".format(song))
            tools.writeAndPrintLog(log_file,
                                   "\n ==================== Error Downloading song={0} ==================== \n".format(
                                       song), test=test)


def start(test=0):
    song_dir = inputSongDir(test)

    if test:
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
            if 'Downloaded_songs' not in curr_dir:
                handleSongsInDir(curr_dir, files, sub_dir_flag, test=test)
