def recurse(a):
    if 'children' in a and a['children']:
        if a['title'] != '':
            print "enter folder "+a['title']
        for b in a['children']:
            recurse(b)
        if a['title'] != '':
            print "exit folder"
    elif 'uri' in a:
        if a['uri'][:5] != 'place':
            print "add "+a['uri']

import json
recurse(json.load(open("bookmarks.json","r")))
