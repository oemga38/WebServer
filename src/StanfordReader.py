#!/usr/bin/env python
import sys
import codecs
import re
from pygraph.classes.digraph import digraph
from pygraph.classes.exceptions import AdditionError

StanfordDepPattern = re.compile('([^\(^\)]+)\((.*)-(\d+)\'?, (.*)-(\d+)\'?\)')

def ProduceNodeIdentifier(token, position):
	return token+"-"+str(position)

def GetTokenPositionList(deps):
	tokenBag = set()
	for dep in deps:
		tokenBag.add((dep[1],dep[2]))
		tokenBag.add((dep[3],dep[4]))

	return sorted(list(tokenBag), key=lambda x:x[1])

def GetTokenList(deps):
	"""from depedency relation tuples, generate token list

	:param deps: a set of dependency relations consisting a sentence
	:type deps: a tuple, (relationType:string, headToken:string, headTokenPosition:int, depToken:string, depTokenPosition:int)
	:returns: token list
	:rtype: a list"""
	tokenBag = GetTokenPositionList(deps)
	
	return [token for (token, position) in tokenBag]

def CostructGraph(deps):
	"""from dependency relation tuples, construct dependency graph

	:param deps: a set of dependency relations constisting a sentence
	:type deps: a tuple, (relationType:string, headToken:string, headTokenPosition:int, depToken:string, depTokenPosition:int)
	:returns: dependency graph
	:ttype: a pygraph.classes.digraph
			'nodes' are represented with 'token-position' as defined in ProduceNodeIdentifier method
			'edges' are represented with a tuple (headNodeIdentifier, depNodeIdentifier) with label=depType"""
	
	depGraph = digraph()
	for token, position in GetTokenPositionList(deps):
		depGraph.add_node(ProduceNodeIdentifier(token, position))

	for depType, headToken, headPosition, depToken, depPosition in deps:
		try:
			depGraph.add_edge((ProduceNodeIdentifier(headToken,headPosition), ProduceNodeIdentifier(depToken,depPosition)), label=depType)
		except AdditionError:
			print >> sys.stderr, "AdditionError: %s, (%s, %s)" % (depType, ProduceNodeIdentifier(headToken, headPosition), ProduceNodeIdentifier(depToken, depPosition))

	return depGraph

def ReadSent(deps):
	"""reads a list of strings that represents dendency relations

	:param deps: a list of strings, where each string represents a Stanford style dependency relation
	:type deps: a list
	:returns: a tuple, (relationType:string, headToken:string, headTokenPosition:int, depToken:string, depTokenPosition:int)
	:rtype: a tuple"""
	depTuples = []
	for dep in deps:
		if StanfordDepPattern.match(dep) == None:
			print >> sys.stderr, dep
		else:
			depTuples.append(StanfordDepPattern.match(dep).groups())

	# type conversion of TokenPositions: string -> int	
	newDepTuples = [ (lambda x: (x[0],x[1],int(x[2]),x[3],int(x[4])))(dep) for dep in depTuples ]

	return newDepTuples
	

def ReadSents(infile):
	"""reads a file of Stanford-style dependency parsing results, produces token lists and dependency parse trees
 
    :param infile: a txt file name that contains dependency structures of sentences produced by Stanford Tools
		- Each line contains one dependency relation.
		- Sets of dependency relations from different sentneces are delimited by an empty line.
    :type infile: string
    :returns: a list of tuples, (a list of tuples:(token, position), a pygraph)
    :rtype: list
    """
	fin = codecs.open(infile, encoding='utf-8')
	
	sents = []
	sent = []
	for line in fin:
		if line == "\n":
			sentDeps = ReadSent(sent)
			sents.append((GetTokenPositionList(sentDeps),CostructGraph(sentDeps)))
			sent = []
		else:
			sent.append(line.strip())

	return sents 

if __name__ == "__main__":
	for tokenPositionList, depGraph in ReadSents("../corpus/sents_parsed.dep"):
		print tokenPositionList
		for edge in depGraph.edges():
			print depGraph.edge_label(edge), edge


