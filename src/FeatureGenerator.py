#!/usr/bin/env python
import nltk
import random
import sys
import re
from AnnotationUnit import *
import GraphUtils
import ConTreeUtils

# numerical normalization
#NN = lambda x: x
NN = lambda x: re.sub("\d", "1", x)
 
######################
# Feature Generators #
######################
#	- base feature constructors
def ValueFeature(featureName, feature):
	return dict([(featureName, NN(feature))])
def BagOfFeatures(featureName, featureList):
	return dict([('contain-%s(%s)' % (featureName, NN(unicode(feature))), True) for feature in featureList])

def Ngram(n, items):
	ngrams = list()
	for i in range(0, len(items)-n+1):
		ngrams.append(tuple(items[i:i+n]))
	return ngrams

def BagOfNgramFeatures(featureName, featureList, n):
	features = dict()
	for i in n:
		features.update(BagOfFeatures("%s: %sgram"%(featureName,str(i)), Ngram(i, featureList)))
	return features		

#########
# Words #
#########
def SurfaceTokenFeatures(au, n=set([1])):
	return BagOfNgramFeatures('word', au.get_words(), n)

##############
# Dependency #
##############
def ExtractTokenFromNodeIdentifier(nodeIdentifier):
	return nodeIdentifier.rsplit('-',1)[0]

def GetDepenPathsFromEventToCancer(au):
	"""produce shortest paths on a dependency parse tree of a au, from the head token of event_2 to the head tokens of all the cancer-related terms.
	:param au: an annotation unit
	:type au: AnnotatationUnit
	:returens: a list of shortest paths, where a path is represented as a list of node identifiers on the dependency graph
	:rtype: list"""

	undirGraph = GraphUtils.ConvertToUndirected(au.depGraph)
	event2_index = au.get_event_2_indexes()
	cancer_indexes = au.get_cancer_terms_indexes_list()
	#print cancer_indexes

	#print event2_index
	event2NodeIdentifier = au.parseResult.get_row(DEP)[event2_index[0]] # heuristics 1: head token of event2 key phrase
	cancerNodeIdentifiers = list()
	for cancer_index in cancer_indexes:
		try: cancerNodeIdentifiers.append(au.parseResult.get_row(DEP)[cancer_index[-1]]) # heuristics 2: head token of cancer-related term
		except IndexError:
			print >> sys.stderr, au.orgSent
			print >> sys.stderr, au.get_words()
			print >> sys.stderr, au.cancer_terms
			print >> sys.stderr, au.__get_indexes(au.cancer_terms[0][1])
			print >> sys.stderr, au.get_cancer_terms()
			print >> sys.stderr, cancer_indexes
			print >> sys.stderr, cancer_index
			print >> sys.stderr, cancer_index[-1]
			print >> sys.stderr, au.parseResult.get_row(DEP)
			raise
	return GraphUtils.GetPaths(undirGraph, event2NodeIdentifier, cancerNodeIdentifiers) 

def GetDepenPathToken(au, path):
	return map(ExtractTokenFromNodeIdentifier, path)
def GetDepenPathDep(au, path):
	depPath = list()
	for i, node in enumerate(path[1:]):
		edge = (path[i], node)
		if not au.depGraph.has_edge(edge): edge = (node, path[i])
		depPath.append(au.depGraph.edge_label(edge))
	return depPath
def GetDepenPathEdge(au, path):
	edgePath = list()
	for i, node in enumerate(path[1:]):
		edge = (path[i], node)
		if not au.depGraph.has_edge(edge): edge = (node, path[i])
		edgePath.append((ExtractTokenFromNodeIdentifier(edge[0]), ExtractTokenFromNodeIdentifier(edge[1]), au.depGraph.edge_label(edge)))
	return edgePath

def GetDepenPathFeatures(au, tokenFeature=True, depFeature=True, edgeFeature=True, n=set([1])):
	features = dict()

	depPaths = GetDepenPathsFromEventToCancer(au)
	tokenFeatureSet = set()
	depFeatureSet = set()
	edgeFeatureSet = set()
	for depPath in depPaths:
		tokenFeatureSet = tokenFeatureSet.union(set(GetDepenPathToken(au, depPath)))
		depFeatureSet = depFeatureSet.union(set(GetDepenPathDep(au, depPath)))
		edgeFeatureSet = edgeFeatureSet.union(set(GetDepenPathEdge(au, depPath)))
	
	if tokenFeature: features.update(BagOfNgramFeatures('DepPathToken',list(tokenFeatureSet),n))
	if depFeature: features.update(BagOfNgramFeatures('DepPathDep',list(depFeatureSet),n))
	if edgeFeature: features.update(BagOfNgramFeatures('DepPathEdge',list(edgeFeatureSet),n))

	return features


##########
# Others #
##########
# For Chun et al., BMC Bioinformatics, 2006.
def keywords(au):
	d = dict()
	d.update(ValueFeature('gene', au.get_gene()))
    #d.update(ValueFeature('event_1', au.get_event_1()))
	d.update(ValueFeature('event_2', au.get_event_2()))
	for cancer_term in au.get_cancer_terms():
		d.update(ValueFeature('cancer_term', cancer_term))
	return d

def keyword_ranges_order(au, keyword_type1, keyword_range1, keyword_type2, keyword_range2):
	if keyword_range1[-1] < keyword_range2[0]: order = "<"
	elif keyword_range2[-1] < keyword_range1[0]: order = ">"
	else: order = "="
	#return ValueFeature("order:%s-%s"%(keyword_type1, keyword_type2), order) 
	return BagOfFeatures("order:%s-%s"%(keyword_type1, keyword_type2), [order]) # for multiple cancer terms
def keywords_order(au):
    d = dict()
    for cancer_term_indexes in au.get_cancer_terms_indexes_list():
        d.update(keyword_ranges_order(au, "gene", au.get_gene_indexes(), "cancer", cancer_term_indexes))
        d.update(keyword_ranges_order(au, "event_2", au.get_event_2_indexes(), "cancer", cancer_term_indexes))
    return d
 
def keyword_context_ngrams(au, ws, keyword_type, keyword_range):
	d = dict()
	end_index = min(keyword_range[-1]+ws+1, len(au.get_words()))
	d.update(BagOfNgramFeatures('context:%s'%keyword_type, au.get_words()[keyword_range[-1]+1:end_index],set([ws])))

	begin_index = max(keyword_range[0]-ws, 0) 
	d.update(BagOfNgramFeatures('context:%s'%keyword_type, au.get_words()[begin_index:keyword_range[0]], set([ws])))
	return d
def context_ngrams(au, ws):
	d = dict()
	d.update(keyword_context_ngrams(au, ws, 'gene', au.get_gene_indexes()))
	#if au.get_event_1() != 'None': d.update(keyword_context_ngrams(au, ws, "event_1", au.get_event_1_indexes()))
	d.update(keyword_context_ngrams(au, ws, "event_2", au.get_event_2_indexes()))
	for cancer_term_indexes in au.get_cancer_terms_indexes_list():
		d.update(keyword_context_ngrams(au, ws, "cancer", cancer_term_indexes))
	return d

#	- summary function
def Chun2006Features(au):
	d = dict()
	d.update(SurfaceTokenFeatures(au))
	d.update(keywords(au))
	d.update(keywords_order(au))
	d.update(context_ngrams(au, 1))
	d.update(context_ngrams(au, 2))
	return d

# for MeInfoText2.0 (Fang et al., BMC Bioinformatics 2011)
# 	- word n-gram between keywords
def IndexBetween(range1, range2):
	if range1[-1] < range2[0]: return range(range1[-1]+1,range2[0])
	elif range2[-1] < range1[0]: return range(range2[-1]+1,range1[0])
	else: return []
def TokensBetweenKeywords(au, keywordRange):
	tokensBetween = list()
	for cancerTermRange in au.get_cancer_terms_indexes_list():
		indexes = IndexBetween(keywordRange, cancerTermRange)
		if indexes: tokensBetween.append(au.get_words()[indexes[0]:indexes[-1]+1])
	return tokensBetween
def TokenNgramBetweenKeywords(au, keywordType, keywordRange, n):
	d = dict()
	for TokensBetween in TokensBetweenKeywords(au, keywordRange):
		d.update(BagOfNgramFeatures("inter-%s-cancer"%keywordType, TokensBetween, n))
	return d

#	- surrounding words
def LeftSurroundingIndex(range1, range2, n):
	if range1[0] <= range2[0]: end = range1[0]
	else: end = range2[0]
	return range(max(0,end-n), end)
def RightSurroundingIndex(range1, range2, n, m):
	# m is len of words
	if range1[-1] <= range2[-1]: end = range2[-1]
	else: end = range1[-1]
	return range(end+1, min(m, end+n+1))
def SurroundingWords(au, keywordType, keywordRange, n):
	d = dict()
	words = au.get_words()
	for cancerTermRange in au.get_cancer_terms_indexes_list():
		lsi = LeftSurroundingIndex(keywordRange, cancerTermRange, n)
		rsi = RightSurroundingIndex(keywordRange, cancerTermRange, n, len(words))
		d.update(BagOfNgramFeatures("surrounding-%s-cancer"%keywordType, [words[i] for i in lsi+rsi], set([1])))
	return d

#	- phrase chunks & type
def InterChunkHead(au, keywordType, keywordRange, chunkFeature=True, typeFeature=True):
	d = dict()
	for cancerTermRange in au.get_cancer_terms_indexes_list():
		between = IndexBetween(keywordRange,cancerTermRange)
		if between:
			betweenPhrase = ConTreeUtils.GetMinimumPhraseCovering(au.conTree, between[0], between[-1]+1)
			if chunkFeature: d.update(ValueFeature("InterChunk:%s-cancer"%keywordType, "[%s %s]"%(ConTreeUtils.GetRoot(betweenPhrase),ConTreeUtils.GetHead(betweenPhrase))))
			if typeFeature: d.update(ValueFeature("InterChunkType:%s-cancer"%keywordType, ConTreeUtils.GetRoot(betweenPhrase)))
	return d

def SurroundingChunks(au, keywordType, keywordRange, n):
	d = dict()
	for cancerTermRange in au.get_cancer_terms_indexes_list():
		features = list()
		lsi = LeftSurroundingIndex(keywordRange, cancerTermRange, n)
		#print lsi
		#print au.id_str
		if lsi: 
			lsPhrase = ConTreeUtils.GetMinimumPhraseCovering(au.conTree, lsi[0], lsi[-1]+1)
			#print lsPhrase
			features.append("[%s %s]"%(ConTreeUtils.GetRoot(lsPhrase), ConTreeUtils.GetHead(lsPhrase)))
		rsi = RightSurroundingIndex(keywordRange, cancerTermRange, n, len(au.get_words()))
		#print rsi
		if rsi:
			rsPhrase = ConTreeUtils.GetMinimumPhraseCovering(au.conTree, rsi[0], rsi[-1]+1)
			#print rsPhrase
			features.append("[%s %s]"%(ConTreeUtils.GetRoot(rsPhrase), ConTreeUtils.GetHead(rsPhrase)))
		d.update(BagOfFeatures("surroudingChunk:%s-cancer"%keywordType, features))
	return d
			
#	- parse tree path
def ConTreePath(au, keywordType, keywordRange):
	d = dict()
	for cancerTermRange in au.get_cancer_terms_indexes_list():
		p1, p2 = ConTreeUtils.GetPathFromTo(au.conTree, keywordRange[-1], cancerTermRange[-1])
		p1.reverse()
		path = '>'.join(p1[2:]) + '<' + '<'.join(p2[1:-2])
		d.update(ValueFeature("ConTreePath:%s-cancer"%keywordType, path))
	return d

#	- summary function
def MeInfoTextFeatures(au):
	d = dict()
	d.update(TokenNgramBetweenKeywords(au, "gene", au.get_gene_indexes(), set([1,2])))
	d.update(TokenNgramBetweenKeywords(au, "event", au.get_event_2_indexes(), set([1,2])))
	d.update(SurroundingWords(au, "gene", au.get_gene_indexes(), 2))
	d.update(SurroundingWords(au, "event", au.get_event_2_indexes(), 2))
	d.update(InterChunkHead(au, "gene", au.get_gene_indexes(), chunkFeature=True, typeFeature=True))
	d.update(InterChunkHead(au, "event", au.get_event_2_indexes(), chunkFeature=True, typeFeature=True))
	d.update(SurroundingChunks(au, "gene", au.get_gene_indexes(), 2))
	d.update(SurroundingChunks(au, "event", au.get_event_2_indexes(), 2))
	d.update(ConTreePath(au, "gene", au.get_gene_indexes()))
	d.update(ConTreePath(au, "event", au.get_event_2_indexes()))
	return d
###########################
# Main Feature Generators # 
###########################

def featureset(au):
	d = dict()
	d.update(SurfaceTokenFeatures(au, n=set([1])))
	d.update(keywords(au))
	d.update(GetDepenPathFeatures(au, n=set([1])))
	d.update(context_ngrams(au, 1))
	#d.update(keywords_order(au))	
	#d.update(MeInfoTextFeatures(au))
	#d.update(Chun2006Features(au))
	return d
 
def get_featuresets(aus, concept):
	if concept == "CCS":
		return [(featureset(au), au.get_CCS()) for au in aus]
	elif concept == "PT":
		return [(featureset(au), au.get_PT()) for au in aus]
	elif concept == "GeneClass":
		return [(featureset(au), au.get_GeneClass()) for au in aus]
		
	else:
		print >> sys.std_err, "wrong concept to classify"

from AnnotationUnit import *
def test():
	aus = get_annotation_units("../corpus/gene_cancer_corpus_130408-1.xml")
	aus = UnifiedReader(aus, "../corpus/sents_parsed.con", "../corpus/sents_parsed.dep")
	return aus


if __name__ == "__main__":
	from AnnotationUnit import *
	#from pygraph.readwrite.dot import write
	import random
	#import subprocess
	aus = get_annotation_units("../corpus/gene_cancer_corpus_130408-1.xml")
	aus = UnifiedReader(aus, "../corpus/sents_parsed.con", "../corpus/sents_parsed.dep")

	#uid = random.randrange(1,822)
	#uid = 1
	#au = aus[uid-1]
	#print uid
	#print au.cancer_terms
	#print au.parseResult.get_row(RANGE)
	#print au.orgSent
	#f = open("graph","w")
	#f.write(write(au.depGraph))
	#f.close()
	#subprocess.call(['dot', 'graph', '-Tjpg', '-o','graph.jpg'])
	#depPaths = GetDepenPathsFromEventToCancer(au)
	#for depPath in depPaths:
	#	print depPath
	#	print GetDepenPathToken(au, depPath)
	#	print GetDepenPathDep(au, depPath)
	#	print GetDepenPathEdge(au, depPath)

	#print au.conTree.draw()
	#print MeInfoTextFeatures(au)
	for au in aus:
		Chun2006Features(au)
	#print Chun2006Features(au)
