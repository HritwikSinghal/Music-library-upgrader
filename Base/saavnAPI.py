import ast
import base64
import json
import os
import re
import traceback
from Base import tools

import requests
import urllib3.exceptions
from bs4 import BeautifulSoup
from pyDes import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

json_decoder = json.JSONDecoder()
user_agent = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
}


# -------------------------------------------#


def get_songs(query, proxies):
    if not query.startswith('https://www.jiosaavn.com'):
        url = "https://www.jiosaavn.com/search/" + query
        flag = "link"
    else:
        url = query
        flag = "query"
    songs = []
    try:
        res = requests.get(url, headers=user_agent, data=[('bitrate', '320')])
        soup = BeautifulSoup(res.text, "html5lib")
        all_song_divs = soup.find_all('div', {"class": "hide song-json"})
        for i in all_song_divs:
            try:
                try:
                    song_info = json.loads(i.text)
                    songs.append(song_info)
                except:
                    esc_text = re.sub(r'.\(\bFrom .*?"\)', "", str(i.text))
                    try:
                        song_info = json_decoder.decode(esc_text)
                        songs.append(song_info)
                    except:
                        try:
                            song_info = json.loads(esc_text)
                            songs.append(song_info)
                        except:
                            print(esc_text)

            except Exception as e:
                traceback.print_exc()
                continue
        if len(songs) > 0:
            return songs
    except Exception as e:
        for test_proxy in proxies:
            try:
                print("Testing with proxy", test_proxy)
                res = requests.get(url, headers=user_agent, data=[('bitrate', '320')],
                                   proxies={"http": test_proxy, "https": test_proxy}, timeout=5)
                soup = BeautifulSoup(res.text, "html5lib")
                all_song_divs = soup.find_all('div', {"class": "hide song-json"})
                for i in all_song_divs:
                    try:
                        try:
                            song_info = json.loads(i.text)
                            songs.append(song_info)
                        except:
                            song_info = json_decoder.decode(i.text)
                            songs.append(song_info)
                    except Exception as e:
                        # print_exc()
                        continue
            except Exception as e:
                # print_exc()
                continue
            finally:
                if (len(songs) > 0):
                    return songs
    return songs


def getAlbumId(input_url, proxies):
    try:
        proxi, headers = setProxy()
        res = requests.get(input_url, headers=headers)
        if 'internal error' in res.text:
            for p in proxies:
                try:
                    res = requests.get(input_url, proxies={"http": p, "https": p}, headers=headers, timeout=4)
                    if 'internal error' in res.text:
                        continue
                    break
                except Exception as e:
                    print("Skipped this proxy")
    except Exception as e:
        print('Error accessing website error: ')
        traceback.print_exc()

    soup = BeautifulSoup(res.text, "html5lib")
    try:
        getAlbumID = soup.select(".play")[0]["onclick"]
        getAlbumID = ast.literal_eval(re.search("\[(.*?)\]", getAlbumID).group())[1]
        if getAlbumID is not None:
            return getAlbumID
    except Exception as e:
        print(e)
        pass


def getAlbum(albumId, proxies):
    songs_json = []
    try:
        response = requests.get(
            'https://www.saavn.com/api.php?_format=json&__call=content.getAlbumDetails&albumid={0}'.format(albumId),
            verify=False, timeout=4)
        if response.status_code == 200:
            songs_json = list(filter(lambda x: x.startswith("{"), response.text.splitlines()))[0]
            songs_json = json.loads(songs_json)
            return dict(songs_json)
    except Exception as e:
        traceback.print_exc()

    for proxy in proxies:
        try:
            response = requests.get(
                'https://www.saavn.com/api.php?_format=json&__call=content.getAlbumDetails&albumid={0}'.format(albumId),
                verify=False, proxies={"http": proxy, "https": proxy}, timeout=4)
            if response.status_code == 200:
                songs_json = list(filter(lambda x: x.startswith("{"), response.text.splitlines()))[0]
                songs_json = json.loads(songs_json)
                return dict(songs_json)
        except Exception as e:
            print("Skipped proxy in album")

    return dict(songs_json)


def get_lyrics(url):
    try:
        if '/song/' in url:
            url = url.replace("/song/", '/lyrics/')
            source = requests.get(url).text
            soup = BeautifulSoup(source, 'html5lib')
            res = soup.find('p', class_='lyrics')
            lyrics = str(res).replace("<br/>", "\n")
            lyrics = lyrics.replace('<p class="lyrics"> ', '')
            lyrics = lyrics.replace("</p>", '')
            return (lyrics)
    except Exception:
        traceback.print_exc()
        return


def decrypt_url(url):
    des_cipher = des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
    base_url = 'http://h.saavncdn.com'

    enc_url = base64.b64decode(url.strip())
    dec_url = des_cipher.decrypt(enc_url, padmode=PAD_PKCS5).decode('utf-8')
    dec_url = base_url + dec_url[10:] + '_320.mp3'
    r = requests.get(dec_url)
    if str(r.status_code) != '200':
        dec_url = dec_url.replace('_320.mp3', '.mp3')
    return dec_url


# -------------------------------------------#
# todo: inspect below func's

def fate_proxy():
    resp = requests.get('https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list')
    a = resp.text.split('\n')
    p_list = []
    for i in a:
        try:
            p_list.append(json.loads(i))
        except Exception as e:
            continue
    np_list = []
    for i in p_list:
        if i['country'] == 'IN':
            np_list.append(i)
    proxy = []
    fast_proxy = sorted(np_list, key=lambda k: k['response_time'])
    for p in fast_proxy:
        proxy.append(str(p['host']) + ':' + str(p['port']))
    return proxy


def setProxy():
    base_url = 'http://h.saavncdn.com'
    proxy_ip = ''
    if 'http_proxy' in os.environ:
        proxy_ip = os.environ['http_proxy']
    proxies = {
        'http': proxy_ip,
        'https': proxy_ip,
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
    }
    return proxies, headers


# -------------------------------------------#


def start(url):
    proxies = fate_proxy()

    try:
        print("All is well with query", url)
        if '/song/' in url:
            print("Song")
            song = get_songs(url, proxies)[0]
            song['image_url'] = tools.fixImageUrl(song['image_url'])
            song['title'] = tools.removeGibberish(song['title'])
            song['url'] = decrypt_url(song['url'])
            song['album'] = tools.removeGibberish(song['album'])
            # song['lyrics'] = get_lyrics(url)
            return json.dumps(song)
        elif '/search/' in url:
            print("Text Query Detected")
            songs = get_songs(url, proxies)
            for song in songs:
                song['image_url'] = tools.fixImageUrl(song['image_url'])
                song['title'] = tools.removeGibberish(song['title'])
                song['url'] = decrypt_url(song['url'])
                song['album'] = tools.removeGibberish(song['album'])
                # song['lyrics'] = get_lyrics(song['tiny_url'])
            return json.dumps(songs)
        elif '/album/' in url:
            print("Album")
            id = getAlbumId(url, proxies)
            songs = getAlbum(id, proxies)

            for song in songs["songs"]:
                song['image'] = tools.fixImageUrl(song['image'])
                song['song'] = tools.removeGibberish(song['song'])
                song['album'] = tools.removeGibberish(song['album'])
                # song['lyrics'] = get_lyrics(song['perma_url'])
                song['encrypted_media_path'] = decrypt_url(song['encrypted_media_path'])
            return json.dumps(songs)
        raise AssertionError
    except Exception as e:
        errors = []
        traceback.print_exc()
        error = {
            "status": str(e)
        }
        errors.append(error)
        return json.dumps(errors)
