#!/usr/bin/env python
import re

class DiseaseDic:
	def __init__(self, dic_file):
		self.dic_file_name = dic_file
		self.dic = []

		for line in open(self.dic_file_name):
			dname, index1, index2 = line.strip().rsplit(' ',2)
			self.dic.append((unicode(dname, encoding='utf-8'), int(index1), int(index2)))

	def __getMatchWithSpecialChar(self, dname, sentence, sCharBeg, sCharEnd):
		matches = []
		index = 0
		newSent = sCharBeg + sentence + sCharEnd
		while(index < len(newSent) and index != -1):
			index = newSent.find(sCharBeg+dname+sCharEnd, index)
			if index != -1:
				matches.append((dname, index, index+len(dname)))
				index = index + len(sCharBeg) + len(dname) + len(sCharEnd)
		return matches

	def getMatches(self, sentence):
		# matches: [ ( diseas_name, char_offset_disease_name_s, char_offset_disease_name_e), ... ]
		sCharPairs = [(' ',' '), (' ',','), (' ',':'), (' ',';'), (' ','.'), (' ','!'), (' ','?'), ('(',')'),('{','}'),('[',']')]
		matches = []
		for dname, _, _ in self.dic:
			for sCharBeg, sCharEnd in sCharPairs:
				matches.extend(self.__getMatchWithSpecialChar(dname, sentence, sCharBeg, sCharEnd))
			if (sentence[0].lower()+sentence[1:]).startswith(dname+' '):
				matches.append((dname, 0, len(dname)))
		return matches

"""
	def match(self, sentence):
		matches = self.getMatches(sentence)
		if len(matches) == 0:
			return "None"

		return ', '.join(map(lambda x: x[0], matches))		
		

if __name__=="__main__":
	import argpasrse

	arg_parser = argparse.ArgumentParser(description="contructing DiseaseDic class")
	arg_parser = argparser.add_argument('dic_file', help="dictionary file")
	args = arg_parser.parse_args()

	for item in DiseaseDic(args.dic_file):
		print item, item[0][item[1]:item[2]+1]
"""			
