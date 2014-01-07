#!/usr/bin/env python
import McCloskyReader
import StanfordReader
import Matrix
import sys

TOKEN, RANGE, POS, CON, DEP = range(5)

class UnifiedData:
	"""A data structure to contain all the information for a sentence.

	:attribute orgSent: original sentence
	:type orgSent: string
	:attribute parseResult: a matrix containing parsing results of a sentence, row by row
	:type parseResult: matrix, whose rows are...
		TOKEN 	-> [string:token]
		RANGE 	-> [tuple:(int:startIndex, int:endIndex)]
		POS		-> [string:POS]
		CON		-> [positions of leaves of self.conTree as defined in nltk.tree.ParentedTree]
		DEP		-> [string:node identifier of self.depGraph]
	:attribute conTree: a constitency tree
	:type conTree: nltk.tree.ParentedTree
	:attribute depGraph: a dependency graph
	:type depGraph: pygraph.classes.digraph
	
	:method __alignTokensToOrigSent:
	:method __GenerateConMatchingDep:
	:method AddParseResults:"""

	def __init__(self, sent):
		self.orgSent = sent

	def __alignTokensToOrigSent(self, tokenList):
		"""finds the ranges of tokens from the original sentence

		:param tokenList: a list of tokens
		:type tokenList: list
		:returns: a list of tuples, (int:starting_char_index, int:ending_char_index), index starts from 0.
		:rtype: list"""
		current = 0
		rangeList = list()
		for token in tokenList:
			# string reformation to deal with McClosky conversion
			token = token.replace('-LRB-','(')
			token = token.replace('-RRB-',')')
			token = token.replace('-LSB-','[')
			token = token.replace('-RSB-',']')
			token = token.replace('-LCB-','{')
			token = token.replace('-RCB-','}')
			token = token.replace("``",'"')
			token = token.replace("''",'"')

			found = self.orgSent.find(token, current)
			if found == -1:
				import sys
				print >> sys.stderr, "error on token alignment"
				print >> sys.stderr, "token: %s, current:%s" % (token, current)
				print >> sys.stderr, rangeList
				print >> sys.stderr, tokenList
				print >> sys.stderr, "orignal sentence: %s" % self.orgSent
			rangeList.append((found, found+len(token)-1))
			current = found+len(token)

		return rangeList

	def __GenerateConMatchingDep(self, depTokenPos):
		#print >> sys.stderr, "__GenerateConMatchingDep"
		depTokenList = map(lambda x: x[0], depTokenPos)
		#print >> sys.stderr, depTokenList
		depTokenRanges = self.__alignTokensToOrigSent(depTokenList)
		#print >> sys.stderr, depTokenRanges
		depLeaves = [None for i in range(len(self.parseResult.get_row(TOKEN)))]
		#print >> sys.stderr, depLeaves
		depRangeIndex = 0
		for i, (s, e) in enumerate(self.parseResult.get_row(RANGE)):
			if depRangeIndex < len(depTokenRanges) and s <= depTokenRanges[depRangeIndex][0] and depTokenRanges[depRangeIndex][1] <= e:
				depLeaves[i] = StanfordReader.ProduceNodeIdentifier(depTokenPos[depRangeIndex][0],depTokenPos[depRangeIndex][1])
				depRangeIndex = depRangeIndex + 1
	
		if depRangeIndex < len(depTokenList):
			print >> sys.stderr, "error on matching constituent tree and dependency tree"
			print >> sys.stderr, depTokenList
			print >> sys.stderr, depTokenRanges
			print >> sys.stderr, depLeaves
			print >> sys.stderr, "sentence: %s" % self.orgSent
		#print >> sys.stderr, depLeaves	
		return depLeaves		
			
	def AddParseResults(self, tokenList, POSList, conTree, depTokenPos, depGraph):
		try: 
			self.parseResult = Matrix.matrix(tokenList)
			self.parseResult.add_row(self.__alignTokensToOrigSent(tokenList))
			self.parseResult.add_row(POSList)		
		except:
			print >> sys.stderr, "token"
			raise


		# conTree -> nltk.tree.ParentedTree
		# parseResut[CON] row contains treepositions of the leaves
		try:
			self.conTree = conTree
			self.parseResult.add_row(conTree.treepositions('leaves'))
		except:
			print >> sys.stderr, "con"
			raise


		# depGraph -> pygraph.classes.digraph
		# parseResult[DEP] row contains identifiers of the leaves
		try:
			self.depGraph = depGraph
			self.parseResult.add_row(self.__GenerateConMatchingDep(depTokenPos))
		except:
			print >> sys.stderr, "dep"
			raise

def UnifiedReader(uds, confile, depfile):
	"""Reads files of parsing results, and store the infomraiton into UnifiedDatas
		- len(uds) == #of sentences in confile == # of sentences in depfile
		- the sentences in uds, confile, depfile, should be the same and in the same order.
	:param uds: a list of UnifiedDatas
	:type uds: list
	:param confile: file name with constituency structure to be read by McCloskyReader
	:type confile: string
	:param depfile: file name with dependency structure to be read by StanfordReader
"""

	parsedList = McCloskyReader.ReadSents(confile)
	depTuples = StanfordReader.ReadSents(depfile)

	for i, ud in enumerate(uds):
		try: ud.AddParseResults(parsedList[i][0],parsedList[i][1], parsedList[i][2], depTuples[i][0], depTuples[i][1])
		except: 
			print >> sys.stderr, i
			raise

	return uds

########
# TEST #
########
if __name__ == "__main__":
	import McCloskyReader
	import StanfordReader
	import codecs

	orgfin = codecs.open('../corpus/sents_only.txt',encoding='utf-8')
	parsedList = McCloskyReader.ReadSents('../corpus/sents_parsed.con')
	depTuples = StanfordReader.ReadSents('../corpus/sents_parsed.dep')
	outfile = codecs.open('UnifiedData.result.130131',mode='w',encoding='utf-8')	
	
	for i, line in enumerate(orgfin):
		ud = UnifiedData(line.strip())
		ud.AddParseResults(parsedList[i][0],parsedList[i][1], parsedList[i][2], depTuples[i][0], depTuples[i][1])
		#if i > 600: print i

		print >> outfile, "###"
		print >> outfile, ud.orgSent
		print >> outfile, ud.parseResult.get_row(TOKEN)

		s = str()
		for sindex, eindex in ud.parseResult.get_row(RANGE):
			s = s + ' ' + ud.orgSent[sindex:eindex+1]
		print >> outfile, s

		print >> outfile, ud.parseResult.get_row(POS)

		#print >> outfile, ud.conTree
		s = str()
		for position in ud.parseResult.get_row(CON):
			s = s + ' ' + ud.conTree[position]
		print >> outfile, s	

		print >> outfile, ud.depGraph
		depList = ud.parseResult.get_row(DEP)
		tokenList = ud.parseResult.get_row(TOKEN)
		for i in range(len(tokenList)):
			print >> outfile, "%s\t%s" % (depList[i], tokenList[i])
