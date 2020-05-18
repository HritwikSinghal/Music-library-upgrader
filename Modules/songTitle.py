from Base import tools


def modifyTitle(tags):
    try:
        oldTitle = tags['title'][0]
        print("Curr Title: ", tags['title'][0])
    except KeyError:
        print("No Title was found in tags, moving on...")
        return

    newTitle = tools.removeSiteName(oldTitle)
    newTitle = tools.removeGibberish(newTitle)
    newTitle = newTitle.strip()

    if oldTitle != newTitle:
        tags['title'] = newTitle
        tags.save()
        print("New Title : ", newTitle)


def start(tags, json_data, found_data):
    if found_data:
        title_value = json_data['title']
        tools.checkAndFixTag(tags, 'title', title_value)

    modifyTitle(tags)
