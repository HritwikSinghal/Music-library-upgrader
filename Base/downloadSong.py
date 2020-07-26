import html
import json
import os
import re
import traceback
import urllib

import mutagen
from mutagen.easyid3 import EasyID3 as easyid3
import requests
from mutagen.mp3 import *
from mutagen.mp4 import *
import shutil

from Base import saavnAPI
from Base import tools

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
    'referer': 'https://www.jiosaavn.com/song/tere-naal/KD8zfAZpZFo',
    'origin': 'https://www.jiosaavn.com'
}


def mod(num):
    if num >= 0:
        return num
    return -num


def autoMatch(song_info_list, song_name, tags, song_with_path, test=0):
    for song in song_info_list:
        json_data = json.loads(json.dumps(song))

        #################################################
        if test:
            # print(json.dumps(json_data, indent=4))
            print()
            print(json_data['title'].lower().strip())
            print(song_name.lower().strip())
        #################################################

        song_name = song_name.lower().strip()
        title = json_data['title'].lower().strip()

        ed_title = tools.editDistDP(song_name, title, len(song_name), len(title))
        if test:
            print(ed_title)

        if ed_title > 5:
            continue

        if tools.isTagPresent(tags, 'album'):

            album_from_tags = tools.removeYear(tags['album'][0]).lower().strip()
            # try:
            #     album_from_json = json_data['actual_album'].lower().strip()
            # except KeyError:
            album_from_json = json_data['album'].lower().strip()
            ed_album = tools.editDistDP(album_from_tags, album_from_json, len(album_from_tags), len(album_from_json))

            if test:
                print(album_from_json)
                print(album_from_tags)
                print(ed_album)

            if ed_album > 4:
                continue

        if tools.isTagPresent(tags, 'artist'):
            artist_from_json = json_data['singers']
            artist_from_json = tools.divideBySColon(artist_from_json)
            artist_from_json = tools.removeTrailingExtras(artist_from_json)
            artist_from_json = tools.removeDup(artist_from_json)

            artist_from_tags = tags['artist'][0]
            artist_from_tags = tools.divideBySColon(artist_from_tags)
            artist_from_tags = tools.removeTrailingExtras(artist_from_tags)
            artist_from_tags = tools.removeDup(artist_from_tags)

            ed_artist = tools.editDistDP(artist_from_tags, artist_from_json, len(artist_from_tags),
                                         len(artist_from_json))

            if test:
                print(artist_from_json)
                print(artist_from_tags)
                print(ed_artist)

            if ed_artist >= 11:
                continue

        audio = MP3(song_with_path)
        length_from_tags = int(audio.info.length)
        length_from_json = int(json_data['duration'])

        if test:
            print(length_from_json)
            print(length_from_tags)
            print(mod(length_from_json) - length_from_tags)

        if mod(length_from_json - length_from_tags) > 10:
            continue

        return song

    return None


def getSong(song_info_list, song_name, tags, song_with_path, test=0):
    # auto-match song
    song = autoMatch(song_info_list, song_name, tags, song_with_path, test)
    if song is not None:
        return song

    #############################
    # print("STOP")
    # x = input()
    #############################
    print("\n-------------------------------"
          "--------------------------------")

    # if no song was matched, Ask user

    print("-------------------------------"
          "\nFrom Below, Select song number.")

    # printing the song list
    keys = [
        'title',
        'album',
        'singers',
        'year',
        'label',
        'music',
        'duration',
        'primary_artists'
    ]

    i = len(song_info_list)
    for song in reversed(song_info_list):
        print(i, end=' ) \n')
        for key in keys:
            print('\t', key.title(), ':', song[key])
        print()
        i -= 1

    print("-------------------------------"
          "--------------------------------\n")

    print("Your song info...")
    print('Name  : ', song_name)
    for key in tags.keys():
        print(key, ":", tags[key][0])

    # now asking user
    song_number = input("\nEnter your song number from above list, if none matches, enter 'n': ")

    try:
        # if user entered 'n' or any letter, then conversion to int will fail and ValueError is raised

        # check if the user entered an index number which was out of range of list, if yes, ask user again
        if int(song_number) > len(song_info_list):
            song_number = int(input("\nOops..You mistyped, \n"
                                    "Please enter number within above range. If none matches, enter 'n': ")) - 1

            if song_number > len(song_info_list):
                return -1

    # if user entered 'n' or any letter, return -1 (since no song was matched correctly)
    except ValueError:
        return None

    song_number = int(song_number)
    return song_info_list[song_number - 1]


def getDownloadSongsInfo(song_name, song_with_path, tags, log_file, test=0):
    list_of_songs = saavnAPI.start(song_name, tags, log_file, test=test)
    song_info = getSong(list_of_songs, song_name, tags, song_with_path, test=test)

    if song_info is None:
        list_of_songs = saavnAPI.start(song_name, tags, log_file, retry_flag=1, test=test)
        song_info = getSong(list_of_songs, song_name, tags, song_with_path, test=test)

    return song_info


def downloadSong(song_dir, song_name, song_info, download_dir, log_file, test=0):
    dec_url = saavnAPI.decrypt_url(song_info['encrypted_media_url'], test=test)
    filename = song_info['title'] + '.m4a'
    filename = re.sub(r'[?*<>|/\\":]', '', filename)

    save_location = os.path.join(download_dir, filename)

    print("Downloading '{0}'.....".format(song_info['title']))

    raw_data = requests.get(dec_url, stream=True, headers=headers)
    with open(save_location, "wb") as raw_song:
        for chunk in raw_data.iter_content(chunk_size=2048):
            if chunk:
                raw_song.write(chunk)

    print("Download Successful")

    if test:
        print("\nMoving song to done Dir....")
        try:
            moveSong(song_dir, song_name)
        except:
            traceback.print_exc()
            print("Some error occured in moving...")

    return save_location


def moveSong(song_dir, song_name):
    old_path = os.path.join(song_dir, song_name) + '.mp3'
    new_path = os.path.join(os.path.join(song_dir, 'Done'), song_name) + '.mp3'
    try:
        shutil.move(old_path, new_path)
        print("Song Moved")
    except:
        traceback.print_exc()
        print("Error Moving")


def addTags(filename, json_data, log_file, test=0):
    audio = MP4(filename)

    audio['\xa9nam'] = html.unescape(str(json_data['title']))
    audio['\xa9ART'] = html.unescape(str(json_data['primary_artists']))

    if json_data['actual_album'] == '':
        audio['\xa9alb'] = html.unescape(str(json_data['album'] +
                                             ' (' + json_data['year'] + ')'))
    else:
        audio['\xa9alb'] = html.unescape(str(json_data['actual_album'] +
                                             ' (' + json_data['year'] + ')'))

    audio['aART'] = html.unescape(str(json_data['singers']))
    audio['\xa9wrt'] = html.unescape(str(json_data['music']))
    audio['desc'] = html.unescape(str(json_data['starring']))
    audio['\xa9gen'] = html.unescape(str(json_data['label']))
    audio['\xa9day'] = html.unescape(str(json_data['year']))

    audio.save()

    cover_url = str(json_data['image'])
    fd = urllib.request.urlopen(cover_url)
    cover = MP4Cover(fd.read(), getattr(MP4Cover, 'FORMAT_PNG' if cover_url.endswith('png') else 'FORMAT_JPEG'))
    fd.close()
    audio['covr'] = [cover]

    audio.save()


def start(song_name, song_dir, download_dir, log_file, test=0):
    song_with_path = os.path.join(song_dir, song_name) + '.mp3'

    try:
        tags = easyid3(song_with_path)
    except:
        tags = {}

    song_info = getDownloadSongsInfo(song_name, song_with_path, tags, log_file, test=test)
    if song_info is None:
        return

    # noinspection PyTypeChecker
    location = downloadSong(song_dir, song_name, song_info, download_dir, log_file, test=test)

    # noinspection PyTypeChecker
    addTags(location, song_info, log_file, test=test)
    print()
