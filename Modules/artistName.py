from Base import tools
import traceback


def fixArtist(tags):
    try:
        oldArtist = tags['artist'][0]
        print("Curr Artist: ", oldArtist)
    except KeyError:
        print("No Artist was found in tags, moving on...")
        return

    # old one
    # oldArtist = ';'.join(re.split(r'/|,|& ', oldArtist))

    # 2nd old method
    # oldArtist = re.sub(r'\s*&\s*|\s*/\s*|\s*,\s*', ';', oldArtist)
    # oldArtist = re.sub(r';\s*;\s*|;\s*', '; ', oldArtist)

    # new method
    newArtist = tools.removeGibberish(oldArtist)
    newArtist = tools.divideBySColon(newArtist)

    newArtist = tools.removeTrailingExtras(newArtist)
    newArtist = tools.removeDup(newArtist)

    if newArtist != oldArtist:
        tags['artist'] = newArtist
        tags.save()
        print("New Artist: ", newArtist)


def start(tags, json_data, found_data):
    if found_data:
        artist_name = json_data['artist']
        tools.checkAndFixTag(tags, 'artist', artist_name)

    fixArtist(tags)
