#!/usr/bin/env python
import codecs
import re
import os
import pickle
import sys
############################################################
#### dictionary file (txt) chracteristics ########################
#### forced to lowercases
#### the longest disease name is on top of the dic file
############################################################

SCHARPAIRS = [(' ',' '), (' ',','), (' ',':'), (' ',';'), (' ','.'), (' ','!'), (' ','?'), (' ','\n'), (' ',')'), (' ','}'), (' ',']'), (' ','-'), ('-',' '), ('-',','), ('-',':'), ('-','!'), ('-','?'), ('-','\n'), ('-',')'), ('-','}'), ('-',']'), ('(',')'),('{','}'),('[',']')]
SCHARPAIRSre = [(' ',' '), (' ',','), (' ',':'), (' ',';'), (' ','.'), (' ','!'), (' ','\?'), (' ','\n'), (' ','\)'), (' ','\}'), (' ','\]'), (' ','-'), ('-',' '), ('-',','), ('-',':'), ('-','!'), ('-','\?'), ('-','\n'), ('-','\)'), ('-','\}'), ('-','\]'), ('\(','\)'),('\{','\}'),('\[','\]')]

def InitDicStr(dic_file='/home/heejin/work/WebServer/data/dic/NCIThesaurusDic.txt.sorted'):
	NCIDic = list()
	for line in codecs.open(dic_file, encoding='utf-8'):
		dname, NCIid = line.strip().split('\t')
		dnames = [sCharBeg + dname + sCharEnd for sCharBeg, sCharEnd in SCHARPAIRS]
		tokenSet = set(' '.join(dnames).split())
		NCIDic.append((dname, NCIid, dnames, tokenSet))
	return NCIDic

def InitDicRe(dic_file='/home/heejin/work/WebServer/data/dic/NCIThesaurusDic.txt.sorted'):
	pin = open('/home/heejin/work/WebServer/data/dic/NCIDicStr.pickle','rb')
	NCIDic = pickle.load(pin)
	pin.close()

	index = 0
	tempDic = list()
	for line in codecs.open(dic_file, encoding="utf-8"):
		dname, NCIid = line.strip().split('\t')
		dnamesRe = [sCharBeg + dname + sCharEnd for sCharBeg, sCharEnd in SCHARPAIRSre]
		tokenSet = NCIDic[index][3]
		tempDic.append((dname, NCIid, tokenSet, dnamesRe))
		index += 1

	newDic = dict()
	for dname, NCIid, tokenSet, dnamesRe in tempDic:
		try: 
			newDic[NCIid][0].extend(dnamesRe)
			newDic[NCIid][1] = newDic[NCIid][1].union(tokenSet)
		except KeyError: 
			newDic[NCIid] =  [dnamesRe, tokenSet]
	for key, item in newDic.items():
		newDic[key][0] = [re.compile(r'%s'%('|'.join(l))) for l in [item[0][x:x+100] for x in xrange(0, len(item[0]), 100)]]
	return newDic


if __name__=="__main__":
	#pout = open('/home/heejin/work/WebServer/data/dic/NCIDicStr.pickle', 'wb')
	#pickle.dump(InitDicStr(), pout)
	#pout.close()

	pout = open('/home/heejin/work/WebServer/data/dic/NCIDicRe.pickle', 'wb')
	pickle.dump(InitDicRe(), pout)
	pout.close()
