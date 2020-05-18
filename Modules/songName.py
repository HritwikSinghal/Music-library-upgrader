from Base.tools import *
from Base.tools import join


def joinPathAndRename(old_name, newName, songDir, song_list):
    # get index of current song from list, so that after we rename,
    # we can edit the entry in list

    old_name_index = song_list.index(old_name)
    newNameWithPath = join(songDir, newName)

    try:
        os.rename(join(songDir, old_name), newNameWithPath)
        song_list[old_name_index] = newName

    except FileExistsError:
        print("\nFile with name '" + newName + "' already exists")
        x = int(input("Do you want to PERMANENTLY delete this old file?"
                      "\n1 == Yes, 0 == NO\n"))

        if x == 1:
            duplicate_file_index = song_list.index(newName)

            os.remove(newNameWithPath)
            del song_list[duplicate_file_index]
            print("File removed successfully. Now renaming new file.")

            os.rename(join(songDir, old_name), newNameWithPath)
            print("File renamed successfully.")

            song_list[old_name_index] = newName
        else:
            print("Moving on to next file...")


def fixName(songDir, old_name, song_list):
    print("Current Name: ", old_name)

    newName = removeBitrate(old_name)
    newName = removeGibberish(newName)
    newName = removeSiteName(newName)
    newName = (newName.replace('.mp3', '')).strip()

    if '.mp3' not in newName:
        newName = newName + '.mp3'

    if old_name != newName:
        print("New Name    : ", newName)
        joinPathAndRename(old_name, newName, songDir, song_list)


def start(songDir, song, song_list):
    changeDir(songDir)
    fixName(songDir, song, song_list)
