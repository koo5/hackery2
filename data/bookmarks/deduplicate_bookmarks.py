#!/usr/bin/env python3

"""
handles and outputs firefox json bookmarks backup format: bookmarks->show all bookmarks->import and backup->backup
"""

import sys, json
import click
from dotdict import Dotdict
from urllib import parse


seen_uris = []

options = Dotdict()

@click.command()
@click.argument('input_file')
@click.argument('output_file')
@click.option('-u', '--un_great_suspender_ize', type=bool)
@click.option('-e', '--remove_empty', type=bool)
@click.option('-pp', '--pretty_print', type=bool)
def main(input_file, output_file, un_great_suspender_ize, remove_empty, pretty_print):

    options.un_great_suspender_ize = un_great_suspender_ize
    options.remove_empty = remove_empty

    print('loading %s'%input_file)
    with open(input_file, 'r') as f:
        j = json.load(f)
    print('deduping...')
    dedupe(j)
    with open(output_file, 'w') as f:
        if pretty_print:
            o = {'indent':4}
        else:
            o = {}
        json.dump(j, f, **o)

def dedupe(x):
    assert(type(x) == dict)
    if 'children' in x:
        for ch in x['children'][:]:
            if 'uri' in ch:

                if options.un_great_suspender_ize:
                    un_great_suspender_ize(ch)

                uri = ch['uri']

                if uri in seen_uris:
                    x['children'].remove(ch)
                else:
                    seen_uris.append(uri)
            else:
                dedupe(ch)
                if options.remove_empty:
                    if not 'children' in ch or ch['children'] == []:
                        assert('uri' not in ch)
                        x['children'].remove(ch)

def un_great_suspender_ize(x):
    un_great_suspender_ize2('uri', x)
    un_great_suspender_ize2('title', x)

def un_great_suspender_ize2(k, x):
    hint = "chrome-extension://klbibkeccnjlkjkiokjodocebajanakg/suspended.html#"
    if hint in x[k]:
        p = parse.urlparse(x[k])
        pp = parse.parse_qs(p.fragment)
        if 'uri' in pp:
            x['uri'] = pp['uri'][0]
        if 'url' in pp:
            x['uri'] = pp['url'][0]
            #print('uri=',pp['url'])
        if 'ttl' in pp:
            x['title'] = pp['ttl'][0]
            #print('title=', pp['ttl'])



if __name__ == '__main__':
    main()

"""

def new_folder(guid,title):
    return {
        "guid":guid,
        "title":title,
        "children":[]}

root = {
    "guid":,
    "title":"",
    "dateAdded":1527314652142000,"lastModified":1575831586218000,"id":1,"typeCode":2,"type":"text/x-moz-place-container","root":"placesRoot","children":
"""
