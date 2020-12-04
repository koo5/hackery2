from rdflib import Graph
import rdflib
g = Graph()
g.parse('/home/koom/RdfTemplates.n3', format='n3')



def blanknodize(x):
	if type(x) == rdflib.term.URIRef:
		u = 'https://lodgeit.net.au/doc/bn'
		if x.startswith(u):
			b = x[len(u):]
			return rdflib.term.BNode('_:bnnn'+b)
	return x
			

g2 = Graph()

for t in g.triples((None,None,None)):
	t2 = [blanknodize(n) for n in t]
	g2.add(t2)
	
print(list(g2.triples((None,None,None))))
import IPython; IPython.embed()
