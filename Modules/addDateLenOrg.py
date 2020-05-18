from Base import tools


def addDate(tags, json_data):
    new_date = json_data['date']
    tools.saveTags('date', new_date, tags)


def addLen(tags, json_data):
    new_len = json_data['length']
    tools.saveTags('length', new_len, tags)


def addOrg(tags, json_data):
    new_org = json_data['organization']
    tools.saveTags('organization', new_org, tags)


def start(tags, json_data):
    addDate(tags, json_data)
    addLen(tags, json_data)
    addOrg(tags, json_data)
