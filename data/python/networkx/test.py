#!/usr/bin/env python3
import networkx as nx
G = nx.Graph()
H = nx.path_graph(10)

G.add_nodes_from(H)
G.add_node(H)
G.add_edges_from([(1, 2), (1, 3)])

