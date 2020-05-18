import json
import re
import traceback
import os

import mutagen
import requests
from mutagen.easyid3 import EasyID3 as easyid3

from Base import saavnAPI
from Base import tools
from Tags import addDateLenOrg
from Tags import albumArt
from Tags import albumName
from Tags import artistName
from Tags import composerName
from Tags import songTitle


def printText(text, test=0):
    if test:
        print(text)


def getURL(baseUrl, song_name, tags):
    # get the search url using album or artist or year or only name

    song_name = song_name.lower().strip()

    if tools.isTagPresent(tags, 'album') and \
            tools.removeYear(tags['album'][0]).lower().strip() != song_name:

        album = tools.removeYear(tags['album'][0]).lower()
        album = tools.removeGibberish(album).strip()

        url = baseUrl + song_name + ' ' + album

    elif tools.isTagPresent(tags, 'artist'):

        oldArtist = tools.removeGibberish(tags['artist'][0])
        newArtist = tools.divideBySColon(oldArtist)

        newArtist = tools.removeTrailingExtras(newArtist)
        newArtist = tools.removeDup(newArtist)

        url = baseUrl + song_name + ' ' + newArtist

    elif tools.isTagPresent(tags, 'date'):
        url = baseUrl + song_name + ' ' + tags['date'][0]
    else:
        url = baseUrl + song_name
    return url


def getCertainKeys(song_info):
    # these are the keys which are useful to us

    rel_keys = [
        'title',
        'album',
        'singers',
        'music',
        'url',

        'year',
        'label',
        'duration',

        'e_songid',
        'image_url',
        'tiny_url',
        'actual_album'
    ]

    json_data = json.loads(song_info)

    #########################
    # print(song_info)
    # x = input()
    #########################

    # this will store all relevant keys and their values
    rinfo = {}

    # for k, v in json_data.items():
    #     print(k, ':', v)

    for key in json_data:

        if key in rel_keys:
            if key == 'singers':
                rinfo['artist'] = json_data[key].strip()
            elif key == 'music':
                rinfo['composer'] = json_data[key].strip()
            elif key == 'year':
                rinfo['date'] = json_data[key].strip()
            elif key == 'duration':
                rinfo['length'] = json_data[key].strip()
            elif key == 'label':
                rinfo['organization'] = json_data[key].strip()
            elif key == 'image_url':
                rinfo['image_url'] = tools.fixImageUrl(json_data[key])
            elif key == 'url':
                rinfo['url'] = saavnAPI.decrypt_url(json_data[key])
            elif key == 'tiny_url':
                rinfo['lyrics_url'] = json_data[key].replace("/song/", '/lyrics/')
            # elif key == 'lyrics':
            #     rinfo['lyrics'] = saavnAPI.get_lyrics(json_data['tiny_url'])
            else:
                rinfo[key] = json_data[key].strip()

    return rinfo


def autoMatch(song_info_list, song_name, tags):
    for song in song_info_list:
        json_data = json.loads(song)

        #################################################
        # print(json.dumps(json_data, indent=4))
        # print()
        # print(json_data['title'].lower().strip())
        # print(song_name.lower().strip())
        #################################################

        song_name = song_name.lower().strip()
        title = json_data['title'].lower().strip()

        ed1 = tools.editDistDP(song_name, title, len(song_name), len(title))
        # print(ed1)
        if ed1 > 5:
            continue

        if tools.isTagPresent(tags, 'album'):

            album_from_tags = tools.removeYear(tags['album'][0]).lower().strip()
            # try:
            #     album_from_json = json_data['actual_album'].lower().strip()
            # except KeyError:
            album_from_json = json_data['album'].lower().strip()

            # print(album_from_json)
            # print(album_from_tags)

            ed2 = tools.editDistDP(album_from_tags, album_from_json, len(album_from_tags), len(album_from_json))
            # print(ed2)

            if ed2 >= 4:
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

            # print(artist_from_json)
            # print(artist_from_tags)

            ed3 = tools.editDistDP(artist_from_tags, artist_from_json, len(artist_from_tags), len(artist_from_json))
            # print(ed3)

            if ed3 >= 11:
                continue

        return song

    return None


def getSong(song_info_list, song_name, tags):
    # auto-match song
    song = autoMatch(song_info_list, song_name, tags)
    if song is not None:
        return song

    # if no song was matched, Ask user
    print("\n-------------------------------"
          "--------------------------------\n")

    # printing the song list
    i = 0
    for song in song_info_list:
        rel_keys = getCertainKeys(song)
        print(i + 1, end=' ) \n')
        for key in rel_keys:
            if key != 'actual_album':
                print('\t', key, ':', rel_keys[key])
        print()
        i += 1

    # now asking user
    song_number = input("\nEnter your song number from above list, if none matches, enter 'n': ")

    try:
        if int(song_number) > len(song_info_list):
            song_number = int(input("\nOops..You mistyped, \n"
                                    "Please enter number within above range. If none matches, enter 'n': ")) - 1

            if song_number > len(song_info_list):
                return -1
    except ValueError:
        return -1

    song_number = int(song_number)
    return song_info_list[song_number - 1]


def getSongInfo(song_name, song_with_path, log_file, test=0):
    baseUrl = "https://www.jiosaavn.com/search/"
    tags = easyid3(song_with_path)

    url = getURL(baseUrl, song_name, tags)
    printText(url, test=test)

    list_of_songs_with_info = saavnAPI.start(url, log_file, test=test)

    if len(list_of_songs_with_info) < 1:
        list_of_songs_with_info.clear()

        url = baseUrl + song_name
        printText(url, test=test)

        list_of_songs_with_info = saavnAPI.start(url, log_file, test=test)

    song = getSong(list_of_songs_with_info, song_name, tags)
    song_info = getCertainKeys(song)

    return song_info


def downloadSong(download_dir, log_file, song_info, test=0):
    os.chdir(download_dir)
    name = re.sub(r'[?*<>|":]', '', song_info['title'])

    name_with_path = os.path.join(download_dir, name + '.mp3')

    # check if song name already exists in download folder
    if os.path.isfile(name_with_path):
        old_name_with_path = os.path.join(download_dir, name + '_OLD.mp3')
        print('Song already exists, renaming it to "' + name + '_OLD.mp3"')

        try:
            os.rename(name_with_path, old_name_with_path)
        except FileExistsError:
            os.remove(old_name_with_path)
            os.rename(name_with_path, old_name_with_path)

    # Download Song
    try:
        print("Downloading '{}'.....".format(name))

        raw_data = requests.get(song_info['url'], stream=True)
        with open(name_with_path, "wb") as raw_song:
            for chunk in raw_data.iter_content(chunk_size=2048):
                # writing one chunk at a time to mp3 file
                if chunk:
                    raw_song.write(chunk)

        print("Song download successful.")
        return name_with_path

    except:
        print("Song download failed...")
        tools.writeAndPrintLog(log_file, "\nSong download failed...\n", test=test)

        if os.path.isfile(name_with_path):
            os.remove(name_with_path)

        return '-1'


def addTags(downloaded_song_name_with_path, download_dir, log_file, song_info, test=0):
    os.chdir(download_dir)
    try:
        tags = easyid3(downloaded_song_name_with_path)
    except:
        print("This Song has no tags. Creating tags...")

        tags = mutagen.File(downloaded_song_name_with_path, easy=True)
        tags.add_tags()
        print("Tags created.")

    addDateLenOrg.start(tags, song_info)
    albumName.start(tags, song_info)
    artistName.start(tags, song_info)
    composerName.start(tags, song_info)
    songTitle.start(tags, song_info)
    albumArt.start(song_info, download_dir, downloaded_song_name_with_path)


def start(song_name, song_with_path, download_dir, log_file, test=0):
    song_info = getSongInfo(song_name, song_with_path, log_file, test=test)
    downloaded_song_name_with_path = downloadSong(download_dir, log_file, song_info, test=test)

    if downloaded_song_name_with_path != '-1':
        addTags(downloaded_song_name_with_path, download_dir, log_file, song_info, test=test)

    print()
