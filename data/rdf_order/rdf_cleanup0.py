#!/usr/bin/env python3

"""
read rdf and pretty-print it (with the default n3 output format option)
TODO figure out how to register the modified n3.py and turtle.py as rdflib plugins,
currently, you have to copy those manually somewhere like ~/.local/lib/python3.6/site-packages/rdflib/plugins/serializers
"""

from ordered_and_indexed_store import OrderedAndIndexedStore
from n3 import N3Serializer
from rdflib import ConjunctiveGraph
import rdflib
import sys
import click

@click.command()
@click.argument('input_file', nargs=1)
@click.option('-i', '--input_format_hint', type=str)
@click.option('-o', '--output_format', type=str, default='n3')

def run(input_file, input_format_hint, output_format):
    g = ConjunctiveGraph(store=OrderedAndIndexedStore())
    g.parse(input_file, format=input_format_hint)
    for l in g.serialize(format=output_format).splitlines(): print(l.decode())

if __name__ == '__main__':
    run()
 