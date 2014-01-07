#!/usr/bin/env python
import codecs
import nltk
import re

POSPattern = re.compile('\(([^()]*? [^()]*?)\)')

def GetTokenAndPOS(line):
	"""reads a string that represents a constituent structure and produces a list of Tokens and a list of POS's

	:param line: a string that represents a constituent structure
	:type line: string
	:returns: a tuple, (a list of Tokens, a list of POS tags)
	:rtype: tuple
	"""
	TokenList = list()
	POSList = list()
	for matched in POSPattern.findall(line.strip()):
		matchedStrs = matched.split(' ')
		TokenList.append(matchedStrs[1])
		POSList.append(matchedStrs[0])
	return (TokenList, POSList)

def ShiftReduce(line, stack):
	#import sys
	#print >> sys.stderr, line
	while line:
		#print stack
		#print line, len(line)
		if 	 line[0] == ' ':
			line = line[1:]
		if 	 line[0] == '(':
			stack.append('(')
			line = line[1:]
		elif line[0] == ')':
			items = []
			item = stack.pop()
			while item != '(':
				items.append(item)
				item = stack.pop()
			items.reverse()
			stack.append(nltk.tree.ParentedTree(items[0], items[1:]))
			line = line[1:]
		else:
			firstPrthesIndex = line.find(')')
			firstSpaceIndex = line.find(' ')
			#print firstPrthesIndex, firstSpaceIndex
			if firstSpaceIndex == -1 or firstPrthesIndex < firstSpaceIndex:
				stack.append(line[:firstPrthesIndex])
				line = line[firstPrthesIndex:]
			else:
				stack.append(line[:firstSpaceIndex])
				line = line[firstSpaceIndex+1:]

		#s = raw_input()

	#stack[0].draw()
	return stack[0]

def ReadSent(line):
	TokenList, POSList = GetTokenAndPOS(line)
	return (TokenList, POSList, ShiftReduce(line,[]))

def ReadSents(infile):
	"""reads a file of McClosky parsing results, produces token list, pos tag lists and parse trees

	:param infile: a txt file name that contains the constituent structure parse tree of McClosky parsing results - each line contiians a parse tree of a sentence.
	:type infile: string
	:returns: a list of tuples, (a list of tokens, a list of POS tags, an nltk.tree.ParentedTree)
	:rtype: list
	"""
	fin = codecs.open(infile, encoding='utf-8')
	
	sents = []
	for line in fin:
		sents.append(ReadSent(line.strip()))

	return sents

if __name__ == '__main__':
	line = "(S1 (S (S (NP (NP (JJ -LSB-Epidermoid) (NNS cysts)) (PP (IN of) (NP (DT the) (NN ovary))))) (. .)))"
	#t = nltk.tree.Tree(line)
	t = ShiftReduce(line,[])[0]
	print t
	print t[0]
	print t[0][0]
	print t[0][0].parent()
	#t.draw()

	#for sent in ReadSents('McCloskyTest.txt'):
	#	print sent[0]
	#	print sent[1]
	#	print sent[2]
