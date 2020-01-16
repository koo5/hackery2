from rdflib import Graph
import rdflib
g = Graph()
g.parse('/home/koom/lodgeit2/master2/static/RdfTemplates.n3', format='n3')


#g2 = Graph()
#for t in g.triples((None,None,None)):
#	g2.add(t)

#print(list(g2.triples((None,None,None))))
#import IPython; IPython.embed()

for l in g.serialize(format='n3').splitlines(): print(l.decode())
