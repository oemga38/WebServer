#!/usr/bin/env python
import codecs
import re
import os
import pickle
import sys
import MySQLdb
############################################################
#### dictionary file chracteristics ########################
#### forced to lowercases
#### the longest disease name is on top of the dic file
############################################################

NCIDic = list()
OUTDIR = None
#SCHARPAIRS = [(' ',' '), (' ',','), (' ',':'), (' ',';'), (' ','.'), (' ','!'), (' ','?'), (' ','\n'), (' ',')'), (' ','}'), (' ',']'), (' ','-'), ('-',' '), ('-',','), ('-',':'), ('-','!'), ('-','?'), ('-','\n'), ('-',')'), ('-','}'), ('-',']'), ('(',')'),('{','}'),('[',']')]
SCHARPAIRS = [
	(' ',' '), (' ',','), (' ',':'), (' ',';'), (' ','.'), (' ','?'), (' ','-'), (' ','\n'), (' ',')'), (' ','}'), (' ',']'), 
	('\n',' '), ('\n',','), ('\n',':'), ('\n',';'), ('\n','.'), ('\n','-'), 
	('-',' '), ('-',','), ('-',':'), ('-',';'), ('-','.'), ('-','?'), ('-','-'), ('-','\n'), ('-',')'), ('-','}'), ('-',']'), 
	('(',')'),('{','}'),('[',']')
]
def InitDic(dic_file='/home/heejin/work/WebServer/data/dic/NCIThesaurusDic.txt.sorted.noEnwords'):
	for line in codecs.open(dic_file, encoding='utf-8'):
		if line[0] == '#': continue
		dname, NCIid = line.strip().split('\t')
		dnames = [sCharBeg + dname + sCharEnd for sCharBeg, sCharEnd in SCHARPAIRS]
		tokenSet = set(' '.join(dnames).split())
		NCIDic.append((dname, NCIid, dnames, tokenSet))
	print >> sys.stderr, "DicInitilization Completed"

def getMatches(text):
	# matches: [ ( dname, offsetS, offsetE, dID), ... ]
	textTokens = set(text.split(' '))
	matches = []
	for dnameOrg, NCIid, dnames, tokenSet in NCIDic:
		if len(textTokens.intersection(tokenSet)) >= len(set(dnameOrg.split())):
			for dname in dnames:
				index = 0
				while(index < len(text) and index != -1):
					index = text.find(dname, index)
					if index != -1:
						e = index+len(dname)-3
						if not any(map(lambda x: x[1] <= index and e <= x[2], matches)):  
							matches.append((dname[1:-1], index, e, NCIid))
						index = e + 3
	return matches


def Matcher(filename):
	pmid = os.path.split(filename)[1].split('.')[0]
	matchFile = os.path.join(OUTDIR, pmid+'.diseaseOff')
#	if os.path.exists(matchFile): return

	fin = codecs.open(filename, encoding='utf-8')
	text = fin.read().strip()
	fin.close()
	text = ' ' + text.lower()
	matches = getMatches(text)

#	"""
	if matches:
		fout = codecs.open(matchFile, mode='w', encoding='utf-8')
		for match in matches: print >> fout, '%s\t%s\t%s\t%s'%match
		fout.close()
	"""
	conn = MySQLdb.connect(host='localhost', user='heejin', passwd='skscjswo', db='WebSearchEngine')
	cursor = conn.cursor()
	#cursor.execute("SET AUTOCOMMIT=1")	
	if matches:
		data = ','.join(['(%s,%s,%s,"%s","%s")'%(pmid, match[1], match[2], match[3], match[0]) for match in matches])
		cursor.execute("INSERT INTO cancerTerm (pmid, sIndex, eIndex, NCIID, term) values " + data)
	cursor.close()
	conn.close()
	"""	

if __name__=="__main__":
	import argparse	
	import timeit
	import glob
	import multiprocessing
	arg_parser = argparse.ArgumentParser(description="NCIDic matching")
	arg_parser.add_argument('inDir', help="directory with input txt files to match NCIDic")
	arg_parser.add_argument('outDir', help="directory for out .diseaseOff files")
	args = arg_parser.parse_args()
	InitDic()
	OUTDIR = args.outDir
	TXTs = glob.glob(os.path.join(args.inDir, "*.txt"))
	#TXTs = TXTs[:10]

	#def run():	
	workerPool = multiprocessing.Pool(processes=16)
	workerPool.map(Matcher, TXTs)

#	print timeit.timeit("run()", setup="from __main__ import run", number=1)
