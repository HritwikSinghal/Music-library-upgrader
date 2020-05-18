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
            # elif key == 'url':
            #     rinfo['url'] = tools.decrypt_url(json_data[key])
            elif key == 'tiny_url':
                rinfo['lyrics_url'] = json_data[key]
            else:
                rinfo[key] = json_data[key]

    return rinfo


def getSong(song_info_list, song_name, tags):
    # auto-match song
    song = autoMatch(song_info_list, song_name, tags)
    if song is not None:
        return song

    #############################
    # print("STOP")
    # x = input()
    #############################

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
        # if user entered 'n' or any letter, then conversion to int will fail and ValueError is raised

        # check if the user entered an index number which was out of range of list, if yes, ask user again
        if int(song_number) > len(song_info_list):
            song_number = int(input("\nOops..You mistyped, \n"
                                    "Please enter number within above range. If none matches, enter 'n': ")) - 1

            if song_number > len(song_info_list):
                return -1

    # if user entered 'n' or any letter, return -1 (since no song was matched correctly)
    except ValueError:
        return -1

    song_number = int(song_number)
    return song_info_list[song_number - 1]


def start(song_name, log_file, test=0):
    baseUrl = "https://www.jiosaavn.com/search/"

    url = getURL(baseUrl, song_name, tags)
    printText(url, test=test)

    # get a list of songs which match search
    list_of_songs_with_info = jioSaavnApi.fetchList(url, log_file, test=test)

    # None can only be returned in case of any error, so we were not able to find data
    if list_of_songs_with_info is None:
        return None

    ###########################
    # tools.printList(list_of_songs_with_info)
    # x = input()
    ###########################

    # if songs were found, get the correct song from that list
    if len(list_of_songs_with_info) != 0:
        song = getSong(list_of_songs_with_info, song_name, tags)

    # else set retry flag to -1 so we can retry below
    else:
        print("Oops...Couldn't find the song in this turn, let me retry :p ..... ")
        song = -1

    # if retry flag is -1, retry, but search only using song name
    # this flag was set by us if no songs were found in first try
    # or it may be set by user when there are no matching songs in the list
    # (the getSongs function returns -1 if user inputs 'n')

    # in both cases, we have to retry search using song name

    if song == -1:
        list_of_songs_with_info.clear()

        # new url based only on song name
        url = baseUrl + song_name
        printText(url, test=test)

        list_of_songs_with_info = jioSaavnApi.fetchList(url, log_file, test=test)

        # None can only be returned in case of any error, so we were not able to find data
        if list_of_songs_with_info is None:
            return None

        song = getSong(list_of_songs_with_info, song_name, tags)

    # if we were still not able to find correct song in 2nd try, just return None
    # (means we failed to find data about song)
    if song == -1:
        return None

    # if the song was found in any of above cases, then we go below.
    # the info we got had too much info, we will save only certain keys like artist from it
    song_info = getCertainKeys(song)

    # return those selected keys
    return song_info
