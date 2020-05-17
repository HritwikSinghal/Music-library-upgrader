from Base import saavn, tools
from traceback import print_exc
import json


def start(url):
    proxies = saavn.fate_proxy()

    try:
        print("All is well with query", url)
        if '/song/' in url:
            print("Song")
            song = saavn.get_songs(url, proxies)[0]
            song['image_url'] = tools.fixImageUrl(song['image_url'])
            song['title'] = tools.removeGibberish(song['title'])
            song['url'] = saavn.decrypt_url(song['url'])
            song['album'] = tools.removeGibberish(song['album'])
            song['lyrics'] = saavn.get_lyrics(url)
            return json.dumps(song)
        elif '/search/' in url:
            print("Text Query Detected")
            songs = saavn.get_songs(url, proxies)
            for song in songs:
                song['image_url'] = tools.fixImageUrl(song['image_url'])
                song['title'] = tools.removeGibberish(song['title'])
                song['url'] = saavn.decrypt_url(song['url'])
                song['album'] = tools.removeGibberish(song['album'])
                song['lyrics'] = saavn.get_lyrics(song['tiny_url'])
            return json.dumps(songs)
        elif '/album/' in url:
            print("Album")
            id = saavn.AlbumId(url, proxies)
            songs = saavn.getAlbum(id, proxies)
            for song in songs["songs"]:
                song['image'] = tools.fixImageUrl(song['image'])
                song['song'] = tools.removeGibberish(song['song'])
                song['album'] = tools.removeGibberish(song['album'])
                song['lyrics'] = saavn.get_lyrics(song['perma_url'])
                song['encrypted_media_path'] = saavn.decrypt_url(song['encrypted_media_path'])
            return json.dumps(songs)
        elif '/playlist/' or '/featured/' in url:
            print("Playlist")
            id = saavn.getListId(url, proxies)
            songs = saavn.getPlayList(id, proxies)
            for song in songs['songs']:
                song['image'] = tools.fixImageUrl(song['image'])
                song['song'] = tools.removeGibberish(song['song'])
                song['lyrics'] = saavn.get_lyrics(song['perma_url'])
                song['encrypted_media_path'] = saavn.decrypt_url(song['encrypted_media_path'])
            return json.dumps(songs)
        raise AssertionError
    except Exception as e:
        errors = []
        print_exc()
        error = {
            "status": str(e)
        }
        errors.append(error)
        return json.dumps(errors)
