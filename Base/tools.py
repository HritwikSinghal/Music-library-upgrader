import traceback
import os
import re


# -----------------------------------------------------#
# Website Name Specifics


def removeDjX(oldName):
    # for DJMXXX

    x = re.compile(r'''
    (
    \s*-*\s*                                # for foo - bar
    \[*                                     # for foo [bar or foo [bar]
    w*\.*                                   # for www.foobar
    [dD][jJ][mM]aza
    .*                                   # for foobar.XXX XXX XXX
    )
    ''', re.VERBOSE)

    newName = x.sub('', oldName)
    return newName


def removeSonX(oldName):
    # for SongsXX

    x = re.compile(r'''
    (
    \s*-*\s*                                # for foo - bar
    \[*                                     # for foo[bar or foo[bar]
    w*\.*                                   # for www.foobar
    [sS]ongs
    .*                                   # for foobar.XXX XXX XXX
    )
    ''', re.VERBOSE)

    newName = x.sub('', oldName)
    return newName


def removeMPXX(oldName):
    # for MPXX

    x = re.compile(r'''
    (
    \s*-*\s*                                # for foo - bar
    \[*                                     # for foo[bar or foo[bar]
    w*\.*                                   # for www.foobar
    [mM][pP]3[kK]
    .*                                   # for foobar.XXX XXX XXX
    )
    ''', re.VERBOSE)

    newName = x.sub('', oldName)
    return newName


def removeSiteName(oldName):
    # supportes SonXXX, DjXXX, MPXX as of now
    # and removes everything after site name
    # including .mp3 extension. So re-add it.

    newName = removeDjX(oldName)
    newName = removeSonX(newName)
    newName = removeMPXX(newName)
    return newName


# ----------------------------------------------#


def removeBitrate(oldName):
    # old method
    # x = re.compile(r'\s*\[*(\d+(.*kbps|Kbps|KBPS|KBps))\]*')

    x = re.compile(r'''
    \s*-*\s*                            # for foo - bar
    \[*                                 # for foo [bar
    \d*\s*[kK][bB][pP][sS]         # for KBps or KBPS or kbps or Kbps
    \]*                                 # for foo bar]
    ''', re.VERBOSE)

    newName = x.sub('', oldName)
    return newName.strip()


def removeYear(oldName):
    newName = re.sub(r' \(\d*\)', '', oldName)
    return newName.strip()


def removeGibberish(oldName):
    newName = re.sub(r'&quot;|&*amp', '', oldName)
    return newName.strip()


def removeTrailingExtras(oldName):
    # newName = re.sub(r'&quot;|&*amp', '', oldName)
    newName = re.sub(r';\s*;\s*', '; ', oldName)
    return newName.strip()


def divideBySColon(oldName):
    namesDivided = re.sub(r'\s*[&/,]\s*', ';', oldName)
    return namesDivided


def removeDup(old_name):
    new_name = old_name.split(';')
    new_name = map(str.strip, new_name)

    new_name = list(set(new_name))
    new_name.sort()
    new_name = ';'.join(new_name)

    return new_name


# ---------------------------------------------#

def fixImageUrl(oldUrl):
    url = str(oldUrl)
    url = url.replace('150x150', '500x500')
    return url


def editDistDP(str1, str2, len_str1, len_str2):
    # Create a table to store results of subproblems
    dp = [[0 for x in range(len_str2 + 1)] for x in range(len_str1 + 1)]

    # Fill d[][] in bottom up manner
    for i in range(len_str1 + 1):
        for j in range(len_str2 + 1):

            # If first string is empty, only option is to
            # insert all characters of second string
            if i == 0:
                dp[i][j] = j  # Min. operations = j

            # If second string is empty, only option is to
            # remove all characters of second string
            elif j == 0:
                dp[i][j] = i  # Min. operations = i

            # If last characters are same, ignore last char
            # and recur for remaining string
            elif str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]

            # If last character are different, consider all
            # possibilities and find minimum
            else:
                dp[i][j] = 1 + min(dp[i][j - 1],  # Insert
                                   dp[i - 1][j],  # Remove
                                   dp[i - 1][j - 1])  # Replace

    return dp[len_str1][len_str2]


# ---------------------------------------------#


def isTagPresent(tags, tag_name):
    if tag_name in tags.keys() and tags[tag_name] != '':
        return True
    return False


def saveTags(tag_name, tag_value_from_json, tags):
    tags[tag_name] = tag_value_from_json
    tags.save()
    print("Added " + tag_name)


def checkAndFixTag(tags, tag_name, tag_value_from_json):
    if (not isTagPresent(tags, tag_name)) or \
            (tag_value_from_json != '' and tag_value_from_json != tags[tag_name]):
        saveTags(tag_name, tag_value_from_json, tags)


# ---------------------------------------------#

def writeAndPrintLog(log_file, line, test=0):
    log_file.write(line)
    traceback.print_exc(file=log_file)
    if test:
        traceback.print_exc()


def getLogFile(song_dir):
    os.chdir(song_dir)
    log_file = open('Music-library-upgrader_LOGS.txt', 'a')
    return log_file


def createLogFile(song_dir):
    os.chdir(song_dir)
    with open('Music-library-upgrader_LOGS.txt', 'w+') as log_file:
        log_file.write("This is log file for Music-library-upgrader. SongDir = " + song_dir + "\n\n")

    return getLogFile(song_dir)
