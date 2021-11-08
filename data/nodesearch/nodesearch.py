#pydot seems to not load the file correctly and some edges dont have a target


import pydot
graphs = pydot.graph_from_dot_file('test.gv')
print(graphs)

g = graphs[0]
# for e in g.edges:
# 	pair = (e.source,e.target)
# 	if pair in edges:
# 		print(pair)
# 	edges.add(pair)
	
