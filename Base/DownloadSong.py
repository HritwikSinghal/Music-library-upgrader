import json
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


def getSong(song_info_list, song_name, tags):
    return song_info_list[0]

    # todo: implement it after fixing it in other project


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
    name_with_path = os.path.join(download_dir, song_info['title'] + '.mp3')

    # check if song name already exists in download folder
    if os.path.isfile(name_with_path):
        old_name_with_path = os.path.join(download_dir, song_info['title'] + '_OLD.mp3')
        print('Song already exists, renaming it to "' + song_info['title'] + '_OLD.mp3"')

        try:
            os.rename(name_with_path, old_name_with_path)
        except FileExistsError:
            os.remove(old_name_with_path)
            os.rename(name_with_path, old_name_with_path)

    # Download Song
    try:
        print("Downloading '{}'.....".format(song_info['title']))

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
