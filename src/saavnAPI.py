import base64
import json
import re
import traceback

import requests
import urllib3.exceptions
from pyDes import *

from src import tools

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
    'referer': 'https://www.jiosaavn.com/song/tere-naal/KD8zfAZpZFo',
    'origin': 'https://www.jiosaavn.com'
}

search_api_url = 'https://www.jiosaavn.com/api.php?p=1&q={0}&_format=json&_marker=0&api_version=4&ctx=web6dot0&n=20&__call=search.getResults'


def decrypt_url(url, test=0):
    des_cipher = des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
    enc_url = base64.b64decode(url.strip())
    dec_url = des_cipher.decrypt(enc_url, padmode=PAD_PKCS5).decode('utf-8')

    dec_url = re.sub('_96.mp4', '_320.mp4', dec_url).replace('http', 'https')

    try:
        aac_url = dec_url[:]
        h_url = aac_url.replace('aac.saavncdn.com', 'h.saavncdn.com')

        # ---------------------------------------------------------#

        # check for 320 m4a on aac.saavncdn.com
        r = requests.head(aac_url, allow_redirects=True, headers=headers)
        if str(r.status_code) == '200':
            return aac_url

        # check for 320 m4a on h.saavncdn.com
        r = requests.head(h_url, allow_redirects=True, headers=headers)
        if str(r.status_code) == '200':
            return h_url

        # ---------------------------------------------------------#

        # check for 160 m4a on aac.saavncdn.com
        aac_url = aac_url.replace('_320.mp4', '_160.mp4')
        r = requests.head(aac_url, allow_redirects=True, headers=headers)
        if str(r.status_code) == '200':
            return aac_url

        # check for 160 m4a on h.saavncdn.com
        h_url = h_url.replace('_320.mp4', '_160.mp4')
        r = requests.head(h_url, allow_redirects=True, headers=headers)
        if str(r.status_code) == '200':
            return h_url

        # ---------------------------------------------------------#
        # check for 128 m4a on aac.saavncdn.com
        aac_url = aac_url.replace('_320.mp4', '.mp4')
        r = requests.head(aac_url, allow_redirects=True, headers=headers)
        if str(r.status_code) == '200':
            return aac_url

        # check for 128 m4a on h.saavncdn.com
        h_url = h_url.replace('_320.mp4', '.mp4')
        r = requests.head(h_url, allow_redirects=True, headers=headers)
        if str(r.status_code) == '200':
            return h_url

        return None
    except:
        if test:
            traceback.print_exc()
        return None


def getURL(baseUrl, song_name, tags):
    # get the search url using album or artist or year or only name

    song_name = song_name.lower().strip()

    if tools.isTagPresent(tags, 'album') and \
            tools.removeYear(tags['album'][0]).lower().strip() != song_name:

        album = tools.removeYear(tags['album'][0]).lower().strip()
        album = tools.removeGibberish(album)

        url = baseUrl.format(song_name + ' ' + album)

    elif tools.isTagPresent(tags, 'artist'):

        oldArtist = tools.removeGibberish(tags['artist'][0])
        newArtist = tools.divideBySColon(oldArtist)

        newArtist = tools.removeTrailingExtras(newArtist)
        newArtist = tools.removeDup(newArtist)

        url = baseUrl.format(song_name + ' ' + newArtist)

    elif tools.isTagPresent(tags, 'date'):
        url = baseUrl.format(song_name + ' ' + tags['date'][0])
    else:
        # todo: change below
        # url = baseUrl.format(song_name)
        url = baseUrl.format(song_name + ' Rafi')
    return url.replace(" ", '+')


def fix(song_info, test=0):
    oldArtist = song_info["primary_artists"].replace('&#039;', '')
    newArtist = tools.removeGibberish(oldArtist)
    newArtist = tools.divideBySColon(newArtist)
    newArtist = tools.removeTrailingExtras(newArtist)
    song_info['primary_artists'] = tools.removeDup(newArtist)

    song_info["singers"] = song_info['primary_artists']

    old_composer = song_info["music"]
    new_composer = tools.removeGibberish(old_composer)
    new_composer = tools.divideBySColon(new_composer)
    new_composer = tools.removeTrailingExtras(new_composer)
    song_info["music"] = tools.removeDup(new_composer)

    song_info['image'] = song_info['image'].replace('-150x150.jpg', '-500x500.jpg')

    # ---------------------------------------------------------------#

    new_title = song_info['title'].replace('&quot;', '#')
    if new_title != song_info['title']:
        song_info['title'] = new_title
        song_info['title'] = tools.removeGibberish(song_info['title'])

        x = re.compile(r'''
                                (
                                [(\[]
                                .*          # 'featured in' or 'from' or any other shit in quotes
                                \#(.*)\#      # album name
                                [)\]]
                                )
                                ''', re.VERBOSE)

        album_name = x.findall(song_info['title'])
        song_info['title'] = song_info['title'].replace(album_name[0][0], '').strip()

        song_info['actual_album'] = album_name[0][1]

        # old method, if above wont work, this will work 9/10 times.
        # json_data = re.sub(r'.\(\b.*?"\)', "", str(info.text))
        # json_data = re.sub(r'.\[\b.*?"\]', "", json_data)
        # actual_album = ''

    else:
        song_info['actual_album'] = ''

    song_info['title'] = tools.removeGibberish(song_info['title'])
    song_info["album"] = tools.removeGibberish(song_info["album"]).strip()

    if test:
        print(json.dumps(song_info, indent=2))


def getImpKeys(song_info, log_file, test=0):
    keys = {}

    keys["title"] = song_info["title"]
    keys["primary_artists"] = ", ".join(
        [artist["name"] for artist in song_info["more_info"]["artistMap"]["primary_artists"]])
    keys["album"] = song_info["more_info"]["album"]
    keys["singers"] = keys["primary_artists"]
    keys["music"] = song_info["more_info"]["music"]
    keys["starring"] = ";".join(
        [artist["name"] for artist in song_info["more_info"]["artistMap"]["artists"] if artist['role'] == 'starring'])
    keys['year'] = song_info['year']
    keys["label"] = song_info["more_info"]["label"]
    keys['image'] = song_info['image']
    keys['encrypted_media_url'] = song_info['more_info']['encrypted_media_url']
    keys["duration"] = song_info["more_info"]["duration"]

    fix(keys, test=test)

    return keys


def getSongInfo(data, log_file, test=0):
    songs_info = []
    for curr_song in data['results']:
        songs_info.append(getImpKeys(curr_song, log_file, test=test))

    return songs_info


def retrieveData(url, log_file, test=0):
    if test:
        print(url)

    res = requests.get(url, headers=headers)

    data = str(res.text).strip()
    try:
        data = json.loads(data)
    except:
        data = fixContent(data)
        data = json.loads(data)

    if int(data['total']) == 0:
        return None

    if test:
        with open('song_info.txt', 'w+', encoding='utf-8') as mf:
            json.dump(data, mf, indent=4)

    songs_info = getSongInfo(data, log_file, test=test)
    return songs_info


def fixContent(data):
    # old
    # data = re.sub(r'<!DOCTYPE html>\s*<.*>?', '', data)
    # return data

    fixed_json = [x for x in data.splitlines() if x.strip().startswith('{')][0]
    return fixed_json


def start(song_name, tags, log_file, retry_flag=0, test=0):
    if not retry_flag:
        url = getURL(search_api_url, song_name, tags)
        songs_info = retrieveData(url, log_file, test=test)

        if songs_info is None:
            retry_flag = 1
        else:
            retry_flag = 0

    if retry_flag:
        print("Let me retry :p ..... ")

        # new url based only on song name
        url = search_api_url.format(song_name)
        songs_info = retrieveData(url, log_file, test=test)

    # noinspection PyUnboundLocalVariable
    return songs_info
