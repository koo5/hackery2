#!/usr/bin/env python3

from ordered_rdflib_store2 import OrderedAndIndexedStore
from n3 import N3Serializer
from rdflib import Graph
import rdflib
import sys
g = Graph(store=OrderedAndIndexedStore())
g.parse(sys.argv[1], format='n3')

triples = []

for t in g.triples((None,None,None)):
    triples.append(t)

triples.sort(key=lambda x:x[0])

#for t in triples:
#    print(t[0])

#import IPython; IPython.embed()


g.remove((None,None,None))
#print(list(g.triples((None,None,None))))


for t in triples:
    g.add(t)

#print(list(g2.triples((None,None,None))))
#import IPython; IPython.embed()

#out = open('out.n3', 'wb')
# g.serialize(out, format='n3')

for l in g.serialize(format='n3').splitlines(): print(l.decode())


#out = open('out.n3', 'wb')
#N3Serializer(g.store).serialize(out)
