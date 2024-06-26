#!/usr/bin/env python3

"""
reads and outputs firefox json and jsonlz4 bookmarks backup format: bookmarks->show all bookmarks->import and backup->backup

does deduplication and other cleanup (not sure how well this still works) but also can generate a directory tree with one file for each bookmark, on your filesystem

actual usage:
rm -rf ~/bookmarks/places/;  /d/hackery2/data/bookmarks/deduplicate_bookmarks.py -ol ~/bookmarks/ -id ~/"/Desktop/bookmarks-*.json" -id ~/"snap/firefox/common/.mozilla/firefox/scjibdo1.default/bookmarkbackups/*"


"""

import sys, json, os, stat, lz4.block
import click
from dotdict import Dotdict
from urllib import parse
from PyInquirer import prompt
from collections import defaultdict
import pathlib
import configparser
from click.exceptions import UsageError

seen_uris = defaultdict(list)
# dict from uri to set of "nodedupe" tags



options = Dotdict()

@click.command()
@click.option('-if', '--input_file', type=str, default='')
@click.option('-id', '--input_directory', type=str, multiple=True)
@click.option('-of', '--output_file', type=str, default='')
@click.option('-dd', '--dedupe', type=bool, default=False)
@click.option('-re', '--remove_empty', type=bool, default=False)
@click.option('-ol', '--output_link_tree_path', type=str, default=False)
@click.option('-ug', '--un_great_suspender_ize', type=bool, default=False)
@click.option('-pp', '--pretty_print', type=bool, default=False)
def main(**kw):
	for k,v in kw.items():
		options[k] = v	

	if options.input_file == '':
		if options.input_directory != []:
			options.input_file = find_most_recent_bookmark_backup_in_directory(options.input_directory)
		else:
			raise UsageError('one of --input_file or --input_directory must be given.')

	print('loading %s'%options.input_file)
	j = load_bookmarks_backup_file(options.input_file)
	print_counts(j)
	print('walking...')
	walk([], j)
	print_counts(j)
	if options.output_file != '':
		with open(options.output_file, 'w') as f:
			if options.pretty_print:
				o = {'indent':4}
			else:
				o = {}
			json.dump(j, f, **o)


def load_bookmarks_backup_file(fn):
	if fn.endswith('.jsonlz4'):
		with open(fn, "rb") as f:
			magic = f.read(8)
			return json.loads(lz4.block.decompress(f.read()).decode("utf-8"))
	else:
		with open(options.input_file, 'r') as f:
			return json.load(f)

"""
		for win in jdata.get("windows"):
			for tab in win.get("tabs"):
				i = int(tab.get("index")) - 1
				urls = tab.get("entries")[i].get("url")
				print(urls)
"""

import glob

def find_most_recent_bookmark_backup_in_directory(globs):
	#hh = dir+'/bookmarks-*.json'
	all_files = []
	for g in globs:
		print('glob matching ' + g)
		files = glob.glob(g)
		print('found: ' + str(files))
		all_files += files
	all_files = sorted(all_files, key=os.path.getmtime)
	result = all_files[-1]
	print('reading ' + result  + ' ...')
	return result 


def print_counts(j):
	c = place_count(j)
	if c != place_count2(j):
		raise('hmm')
	print('have '+ str(count(j)) + ' items, '+ str(c) + ' uris.')

def count(x):
	r = 1
	if 'children' in x:
		r += sum([count(ch) for ch in x['children']])
	return r

def place_count(x):
	if x['type'] == "text/x-moz-place-separator":
		return 0
	elif x['type'] == "text/x-moz-place-container":
		if 'children' in x:
			return sum([place_count(ch) for ch in x['children']])
		else:
			return 0
	elif 'uri' in x:
		return 1
	else:
		raise(Exception(x['type']))

def place_count2(x):
	if 'uri' in x:
		return 1
	elif x['type'] == "text/x-moz-place-separator":
		return 0
	elif x['type'] == "text/x-moz-place-container":
		if 'children' in x:
			return sum([place_count2(ch) for ch in x['children']])
		else:
			return 0
	else:
		raise(Exception(x['type']))

def tags(ch):
	assert 'uri' in ch
	return ch.get(tags, "")

def tagset(ch):
	assert 'uri' in ch
	return set(tags(ch).split(','))

def unique_nodedupe_tag(duplicate_entries, t='nodedupe',tid=2):
	unique_tag = f'nodedupe{tid}'
	tagsets = [tagset(e) for e in duplicate_entries]
	for s in tagsets:
		if unique_tag in s:
			return unique_nodedupe_tag(duplicate_entries, t, tid+1)
	return unique_tag
			
			
def walk(path, x):
	assert(type(x) == dict)
	if 'children' in x:
		for ch in x['children'][:]:
			if 'uri' in ch:

				if options.un_great_suspender_ize:
					un_great_suspender_ize(ch)

				if options.dedupe:

					uri = ch['uri']
					if uri in seen_uris:
						duplicate_entries = seen_uris[uri]
						for duplicate_entry in duplicate_entries:
							if tags(duplicate_entry) == tags(ch):
								unique_tag = unique_nodedupe_tag(duplicate_entries)
								if prompt(
									{
										'type':'confirm',
										'name':'ok',
										'message':f'delete {uri} ? If not, we will add a unique tag: {unique_tag}.',
										'default': False
									}
								)['ok']:
									x['children'].remove(ch)
								else:
									ch['tags'] = ','.join(tags(ch).split(',').append(unique_tag))
								break
						else:
							duplicate_entries.append(ch)
					else:
						duplicate_entries.append(ch)
				
				if options.output_link_tree_path:
					output_link(path, ch, x)
				
			else:
				if ch['type'] == "text/x-moz-place-separator":
					pass
				elif ch['type'] == "text/x-moz-place-container":
					walk(path + [ch['title']], ch)
					if options.remove_empty:
						if not 'children' in ch or ch['children'] == []:
							assert('uri' not in ch)
							x['children'].remove(ch)
				else:
					raise(Exception(ch['type']))


def output_link(path, ch, parent):

	p = pathlib.Path(options.output_link_tree_path + '/places/' + '/'.join([p.replace('/','_').replace('..','__') for p in path]))
	p.mkdir(parents=True, exist_ok=True)
	
	config = configparser.ConfigParser(interpolation=None)
	config.optionxform = str
	
	uri = ch['uri']
	s = 'Desktop Entry'
	config.add_section(s)
	config[s]['Version']='1.0'
	config[s]['Type']='Link'
	config[s]['Name']=ch['title']
	#config[s]['Index']=str(ch['index'])
	config[s]['Icon']='user-bookmarks'
	config[s]['ParentGuid']=parent['guid']
	config[s]['URL']=uri

	fn = uri
	fn = fn[:100] + '::' + ch['guid']
	fn = fn.replace('/','_')
	fn = fn.replace('\n','_')
	
	full_path = str(p) + '/' + fn +'.desktop'
	if pathlib.Path(full_path).is_file():
		print(f'overwriting already existing file: {full_path}', file=sys.stderr)

	with open(full_path, 'w') as configfile:
		config.write(configfile, space_around_delimiters=False)
		os.fchmod(configfile.fileno(), os.fstat(configfile.fileno()).st_mode | stat.S_IXUSR)

	output_details(ch)




seen_guids = set()


def output_details(ch):
	p = pathlib.Path(options.output_link_tree_path + '/details/')
	p.mkdir(parents=True, exist_ok=True)
	
	config = configparser.ConfigParser(interpolation=None)
	config.optionxform = str
	
	s = 'Bookmark Details'
	config.add_section(s)
	config[s]['Index']=str(ch['index'])

	guid = ch['guid']

	if guid in seen_guids:
		raise('hmm')
	seen_guids.add(guid)
	
	fn = guid
	fn = fn.replace('/','_')
	fn = fn.replace('\n','_')
	if fn != guid:
		print(f'weird guid: {guid}', file=sys.stderr)
	
	full_path = str(p) + '/' + fn +'.ini'
	#if pathlib.Path(full_path).is_file():
	#	print(f'overwriting already existing file: {full_path}', file=sys.stderr)

	with open(full_path, 'w') as configfile:
		config.write(configfile, space_around_delimiters=False)


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

