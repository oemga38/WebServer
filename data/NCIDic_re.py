#!/usr/bin/env python
import codecs
import re
import os
import pickle
import sys
############################################################
#### dictionary file chracteristics ########################
#### forced to lowercases
#### the longest disease name is on top of the dic file
############################################################

NCIDic = list()
OUTDIR = None
FILE = None
SCHARPAIRS = [(' ',' '), (' ',','), (' ',':'), (' ',';'), (' ','.'), (' ','!'), (' ','?'), (' ','\n'), (' ',')'), (' ','}'), (' ',']'), (' ','-'), ('-',' '), ('-',','), ('-',':'), ('-','!'), ('-','?'), ('-','\n'), ('-',')'), ('-','}'), ('-',']'), ('(',')'),('{','}'),('[',']')]
SCHARPAIRSre = [(' ',' '), (' ',','), (' ',':'), (' ',';'), (' ','.'), (' ','!'), (' ','\?'), (' ','\n'), (' ','\)'), (' ','\}'), (' ','\]'), (' ','-'), ('-',' '), ('-',','), ('-',':'), ('-','!'), ('-','\?'), ('-','\n'), ('-','\)'), ('-','\}'), ('-','\]'), ('\(','\)'),('\{','\}'),('\[','\]')]
def InitDic(dic_file='/home/heejin/work/WebServer/data/dic/NCIThesaurusDic.txt.sorted'):
	for line in codecs.open(dic_file, encoding='utf-8'):
		dname, NCIid = line.strip().split('\t')
		dnames = [sCharBeg + dname + sCharEnd for sCharBeg, sCharEnd in SCHARPAIRS]
		tokenSet = set(' '.join(dnames).split())
		NCIDic.append((dname, NCIid, dnames, tokenSet))
	print >> sys.stderr, "DicInitilization Completed"

def InitDic2(dic_file='/home/heejin/work/WebServer/data/dic/NCIThesaurusDic.txt.sorted'):
	tempDic = list()
	for line in codecs.open(dic_file, encoding="utf-8"):
		dname, NCIid = line.strip().split('\t')
		dnames = [sCharBeg + dname + sCharEnd for sCharBeg, sCharEnd in SCHARPAIRS]
		
		dnamesRe = [sCharBeg + dname + sCharEnd for sCharBeg, sCharEnd in SCHARPAIRSre]
		tempDic.append((dname, NCIid, dnamesRe, 
	for dname, NCIid, dnames, tokenSet in NCIDic:
		try: 
			newDic[NCIid][0].extend(dnamesRe)
			newDic[NCIid][1].add(dnamesRe)
		except KeyError: newDic[NCIid] = dnamesRe
	for key, dnamesRe in newDic:
		newDic[key] = re.compile(r'%s'%('|'.join(dnamesRe)))
	return newDic

# use NCIDicStr.pickle
def getMatches(text):
	# matches: [ ( dname, offsetS, offsetE, dID), ... ]
	textTokens = set(text.split(' '))
	matches = []
	for dname, NCIid, dnames, tokenSet in NCIDic:
		if set(textTokens).intersection(tokenSet):
			for dname in dnames:
				index = 0
				while(index < len(text) and index != -1):
					index = text.find(dname, index)
					if index != -1:
						newItem = (dname[1:-1], str(index), str(index+len(dname)))
						if all(map(lambda x: not x[1]<=newItem[1] or not newItem[2]<= x[2], matches)):  matches.append(newItem)
						index = index + len(dname) + 2
	return matches

def getMatches_re(text):
	# matches: [ ( dname, offsetS, offsetE, dID), ... ]
	textTokens = set(text.split(' '))
	matches = []
	for dname, NCIid, _, tokenSet, rePattern in NCIDic:
		if set(textTokens).intersection(tokenSet):
			spans = [m.span() for m in rePattern.finditer(text)]
			for newItem in [(dname, str(s), str(e-2), NCIid) for s, e in spans]:
				if all(map(lambda x: not x[1]<=newItem[1] or not newItem[2]<= x[2], matches)):  matches.append(newItem)
	return matches

def Matcher(filename=FILE):
	filename = FILE
	fin = codecs.open(filename, encoding='utf=8')
	text = fin.read().strip()
	fin.close()
	text = ' ' + text.lower()
	matches = getMatches(text)

	pmid = os.path.split(filename)[1].split('.')[0]
	matchFile = os.path.join(OUTDIR, pmid+'.diseaseOff')
	if matches and not os.path.exists(matchFile):
		fout = codecs.open(matchFile, mode='w', encoding='utf-8')
		for match in matches: print >> fout, '\t'.join(match)
		fout.close()
		

if __name__=="__main__":
	import argparse	
	import timeit
	arg_parser = argparse.ArgumentParser(description="NCIDic matching")
	arg_parser.add_argument('dic_file', help="dictionary file")
	arg_parser.add_argument('input_file', help="input txt file to match NCIDic")
	arg_parser.add_argument('outDir', help="directory for out .diseaseOff files")
	args = arg_parser.parse_args()

	InitDic(args.dic_file)
	pout = open('NCIDicStr.pickle', 'wb')
	pickle.dump(NCIDic, pout)
	pout.close()
	#OUTDIR = args.outDir
	#FILE = args.input_file
	#pin = open('NCIDic.pickle','rb')
	#NCIDic = pickle.load(pin)
	#pin.close()
	#print >> sys.stderr, "NCIDic loaded"
	#print timeit.timeit("Matcher()", setup="from __main__ import NCIDic, OUTDIR, FILE, getMatches, getMatches_re, Matcher", number=1)
	#Matcher(args.input_file)
