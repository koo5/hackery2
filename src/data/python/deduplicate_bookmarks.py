#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
handles and output firefox json bookmarks backup format: bookmarks->show all bookmarks->import and backup->backup
"""

import sys, json
import click

seen_uris = []

@click.command()
@click.argument('input_file')
@click.argument('output_file')
def main(input_file, output_file):
	print('loading %s'%input_file)
	with open(input_file, 'r') as f:
		j = json.load(f)
	print('deduping...')
	dedupe(j)
	with open(output_file, 'w') as f:
		json.dump(j, f)

def dedupe(x):
	assert(type(x) == dict)
	if 'children' in x:
		for ch in x['children'][:]:
			if 'uri' in ch:
				uri = ch['uri']
				if uri in seen_uris:
					x['children'].remove(ch)
				else:
					seen_uris.append(uri)
			else:
				dedupe(ch)

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
