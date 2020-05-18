from Base import saavnAPI, tools
import traceback
import json


def start(url):
    proxies = saavnAPI.fate_proxy()

    try:
        print("All is well with query", url)
        if '/song/' in url:
            print("Song")
            song = saavnAPI.get_songs(url, proxies)[0]
            song['image_url'] = tools.fixImageUrl(song['image_url'])
            song['title'] = tools.removeGibberish(song['title'])
            song['url'] = saavnAPI.decrypt_url(song['url'])
            song['album'] = tools.removeGibberish(song['album'])
            song['lyrics'] = saavnAPI.get_lyrics(url)
            return json.dumps(song)
        elif '/search/' in url:
            print("Text Query Detected")
            songs = saavnAPI.get_songs(url, proxies)
            for song in songs:
                song['image_url'] = tools.fixImageUrl(song['image_url'])
                song['title'] = tools.removeGibberish(song['title'])
                song['url'] = saavnAPI.decrypt_url(song['url'])
                song['album'] = tools.removeGibberish(song['album'])
                song['lyrics'] = saavnAPI.get_lyrics(song['tiny_url'])
            return json.dumps(songs)
        elif '/album/' in url:
            print("Album")
            id = saavnAPI.getAlbumId(url, proxies)
            songs = saavnAPI.getAlbum(id, proxies)
            for song in songs["songs"]:
                song['image'] = tools.fixImageUrl(song['image'])
                song['song'] = tools.removeGibberish(song['song'])
                song['album'] = tools.removeGibberish(song['album'])
                song['lyrics'] = saavnAPI.get_lyrics(song['perma_url'])
                song['encrypted_media_path'] = saavnAPI.decrypt_url(song['encrypted_media_path'])
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
