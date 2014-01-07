#!/usr/bin/env python
from pygraph.classes.graph import graph
from pygraph.algorithms.searching import breadth_first_search
from pygraph.classes.exceptions import AdditionError

def ConvertToUndirected(dgr):
	gr = graph()
	for node in dgr.nodes():
		gr.add_node(node)
	for edge in dgr.edges():
		try:
			gr.add_edge(edge, label=dgr.edge_label(edge))
		except AdditionError:
			pass
	return gr


def TracePath(st, end):
	"""produce a list of node from the 'root' to 'end', using dictionary of spanning tree produced by pygraph.algorithms.searching.breadth_first_search
	returns an empty list when there is no path from `root' to 'end'

	:param st: a dictionary of edges of a spanning tree {from:to}, for the root node the value of 'to' is None
	:type st: dictionary
	:param end: node identifier
	:type end: string
	:returns: a list of node identifiers
	:rtype: list"""
	try:
		pointer = st[end]
	except KeyError:
		return []

	path = list()
	path.append(end)
	while(pointer != None):
		path.insert(0,pointer)
		pointer = st[pointer]

	return path

def GetPaths(gr, start, ends):
	"""produce shortest paths from 'start' to 'ends' on gr
	an empty list represents that there is no path from `start' to an `end'

	:param gr: undirected graph
	:type gr: pygraph.classes.graph
	:param start: node identifier of 'start' node
	:type start: string
	:param ends: a list of node identifiers
	:type ends: list of strings
	:returns: a list of paths
	:rtype: list"""

	paths = list()
	st, order = breadth_first_search(gr, root=start)
	for end in ends:
		paths.append(TracePath(st, end))
	
	return paths

if __name__ == "__main__":
	gr = graph()
	
	gr.add_nodes(["Portugal","Spain","France","Germany","Belgium","Netherlands","Italy"])
	gr.add_nodes(["Switzerland","Austria","Denmark","Poland","Czech Republic","Slovakia","Hungary"])
	gr.add_nodes(["England","Ireland","Scotland","Wales"])

	gr.add_edge(("Portugal", "Spain"))
	gr.add_edge(("Spain","France"))
	gr.add_edge(("France","Belgium"))
	gr.add_edge(("France","Germany"))
	gr.add_edge(("France","Italy"))
	gr.add_edge(("Belgium","Netherlands"))
	gr.add_edge(("Germany","Belgium"))
	gr.add_edge(("Germany","Netherlands"))
	gr.add_edge(("England","Wales"))
	gr.add_edge(("England","Scotland"))
	gr.add_edge(("Scotland","Wales"))
	gr.add_edge(("Switzerland","Austria"))
	gr.add_edge(("Switzerland","Germany"))
	gr.add_edge(("Switzerland","France"))
	gr.add_edge(("Switzerland","Italy"))
	gr.add_edge(("Austria","Germany"))
	gr.add_edge(("Austria","Italy"))
	gr.add_edge(("Austria","Czech Republic"))
	gr.add_edge(("Austria","Slovakia"))
	gr.add_edge(("Austria","Hungary"))
	gr.add_edge(("Denmark","Germany"))
	gr.add_edge(("Poland","Czech Republic"))
	gr.add_edge(("Poland","Slovakia"))
	gr.add_edge(("Poland","Germany"))
	gr.add_edge(("Czech Republic","Slovakia"))
	gr.add_edge(("Czech Republic","Germany"))
	gr.add_edge(("Slovakia","Hungary"))

	print GetPaths(gr, "Switzerland", ["Portugal", "Netherlands", "Ireland"])

