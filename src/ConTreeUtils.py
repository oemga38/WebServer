#!/usr/bin/env python
"""
utilities for constituency trees represented with nltk.tree
"""
import nltk.tree

#################################
# modules for head word finding #
#################################
def HeadTableReader(headTableFile = "phraseHeadTable.txt"):
# 0 for head-final category (right),  1 for head-initial category (left)
	headTable = dict()
	for line in open(headTableFile):
		items = line.split()
		headTable[items[1]] = (items[2], items[3:])
	return headTable

HT = HeadTableReader()

def __findHeadDirec(conTree, direction, headCandidates):
	"""This method is diferrent from the method '__findHead' in that it does not consider the orders among the head candidates."""
	indexes = range(len(conTree))
	if not direction: indexes.reverse()

	for index in indexes:
		if conTree[index].node in headCandidates: return conTree[index]
	
	return None

def __findHead(conTree, direction, headCandidates):
	"""This method is different from the method '__findHeadDirec in that is takes into account the orders among the head candidates. Candidates comes first is more important that those comes later."""
	for headCandidate in headCandidates:
		head = __findHeadDirec(conTree, direction, [headCandidate])
		if head: return head
	
	if direction: return conTree[0]
	else: return conTree[-1]
		
def GetHead(conTree):
	""" return head word of the tree
following http://people.csail.mit.edu/mcollins/papers/heads """
	if type(conTree) == unicode or type(conTree) == str: return conTree

	if conTree.node == "NP":
		if conTree[-1].node == "POS": return GetHead(conTree[-1])
		head = __findHeadDirec(conTree, 0, ['NN', 'NNP', 'NNPS', 'NNS', 'NX', 'POS', 'JJR'])
		if head: return GetHead(head)
		head = __findHeadDirec(conTree, 1, ['NP'])
		if head: return GetHead(head)
		head = __findHeadDirec(conTree, 0, ['$', 'ADJP', 'PRN'])
		if head: return GetHead(head)
		head = __findHeadDirec(conTree, 0, ['CD'])
		if head: return GetHead(head)
		head = __findHeadDirec(conTree, 0, ['JJ', 'JJS', 'RB', 'QP'])
		if head: return GetHead(head)
		return GetHead(conTree[-1])
	elif conTree.node in HT.keys():
		return GetHead(__findHead(conTree, int(HT[conTree.node][0]), HT[conTree.node][1]))
	else:
		return GetHead(conTree[0])


		
############################
# modules for path finding #
############################
def GetRoot(conTree):
	if type(conTree) == str or type(conTree) == unicode: return conTree
	else: return conTree.node
	
def GetMinimumPhraseCovering(conTree, start, end):
	"""returns minimum phrase that dominates conTree.leaves()[start:end]
	:rtype: nltk.tree.Tree"""
	newConTree = nltk.tree.Tree.convert(conTree) # since 'treeposition_spanning_leaves method is for only Tree not parentedTree
	return newConTree[newConTree.treeposition_spanning_leaves(start,end)]
	
def GetDownwardPath(conTree, headPos, leafPos):
	path = list()
	if len(headPos) >= len(leafPos): 
		raise ValueError("length of %s is longer than or equal to length of %s" % (headPos, leafPos))
	if headPos != leafPos[:len(headPos)]:
		raise ValueError("%s does not dominate %s" % (headPos, leafPos))
	for i in range(len(headPos), len(leafPos)+1):
		path.append(GetRoot(conTree[leafPos[:i]]))
	return path

def GetPathFromTo(conTree, start, end):
	"""Generaates a path on a constituency tree 'conTree' from the leaf of index 'start' to the leaf of index 'end'
	:param conTree: constiency tree
	:type conTree:nltk.tree.ParentedTree
	:param start: index of the starting leaf
	:type start: int
	:param end: index of the ending leaf
	:type end: int
	:type: tuple, (list, list), where each of the lists represents downward path from lowest commmon ancestor of 'start' and 'end' to each of the two leaves, respectively. """
	if start == end: return ([conTree.leaves()[start]],[conTree.leaves()[end]])
	swp = False
	if start > end: 
		start, end = end, start
		swp = True

	newConTree = nltk.tree.Tree.convert(conTree) # since 'treeposition_spanning_leaves method is for only Tree not parentedTree
	newRoot = newConTree.treeposition_spanning_leaves(start,end+1)

	leafPositions = conTree.treepositions('leaves')
	path1 = GetDownwardPath(conTree, newRoot, leafPositions[start])
	path2 = GetDownwardPath(conTree, newRoot, leafPositions[end])

	if not swp: return (path1, path2)
	else: return (path2, path1)

########
# test #
########
#from AnnotationUnit import *
def test():
	#import random
	aus = get_annotation_units("../corpus/gene_cancer_corpus_130408-1.xml")
	aus = UnifiedReader(aus, "../corpus/sents_parsed.con", "../corpus/sents_parsed.dep")

	au = aus[0]
	print GetPathFromTo(au.conTree, 0, 1)
	print GetPathFromTo(au.conTree, 0, 3)
	print GetPathFromTo(au.conTree, 3, 8)
	print GetPathFromTo(au.conTree, 3, 3)
	print GetPathFromTo(au.conTree, 13, 16)


	return aus

if __name__ == "__main__":
	#print HT
	from AnnotationUnit import *
	import random
	aus = get_annotation_units("../corpus/gene_cancer_corpus_130408-1.xml")
	aus = UnifiedReader(aus, "../corpus/sents_parsed.con", "../corpus/sents_parsed.dep")

	uid = random.randrange(1,822)
	#uid = 594
	au = aus[uid-1]
	print uid

	#au.conTree.draw()
	
	test()
