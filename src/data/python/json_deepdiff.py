#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import deepdiff, json

def load(fn):
	return json.load(open(fn,'r'))

@click.command()
@click.argument('a')
@click.argument('b')
def diff(a,b):
	a = load(a)
	b = load(b)
	d = deepdiff.DeepDiff(a,b)
	print(json.dumps(d, indent=4,default=str))

if __name__ == '__main__':
	diff()
