import json
import traceback

import mutagen
from mutagen.easyid3 import EasyID3 as easyid3

from Base import saavnAPI
from Base import tools


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
                rinfo['artist'] = json_data[key]
            elif key == 'music':
                rinfo['composer'] = json_data[key]
            elif key == 'year':
                rinfo['date'] = json_data[key]
            elif key == 'duration':
                rinfo['length'] = json_data[key]
            elif key == 'label':
                rinfo['organization'] = json_data[key]
            elif key == 'image_url':
                rinfo['image_url'] = tools.fixImageUrl(json_data[key])
            elif key == 'url':
                rinfo['url'] = saavnAPI.decrypt_url(json_data[key])
            elif key == 'tiny_url':
                rinfo['lyrics_url'] = json_data[key].replace("/song/", '/lyrics/')
            # elif key == 'lyrics':
            #     rinfo['lyrics'] = saavnAPI.get_lyrics(json_data['tiny_url'])
            else:
                rinfo[key] = json_data[key]

    return rinfo


def getSong(song_info_list, song_name, tags):
    pass
    # implement it after fixing it in other project


def start(song_name, song_with_path, log_file, test=0):
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
