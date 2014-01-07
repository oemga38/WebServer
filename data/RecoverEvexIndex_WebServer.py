#!/usr/bin/env python
import codecs

if __name__ == "__main__":
	import argparse
	import os
	import re
	argParser = argparse.ArgumentParser()
	argParser.add_argument("infile", help="annotation_units.txt")
	#argParser.add_argument("txtDir", help="dir with abstract txt files")
	argParser.add_argument("outfile", help="output file")
	args = argParser.parse_args()

	fin = codecs.open(args.infile, encoding="utf-8")
	fout = codecs.open(args.outfile, mode='w', encoding="utf-8")
	for line in fin:
		items = line.strip().split('\t')
		pmid, line, SoffBeg, SoffEnd, Gid, Gstr, GoffBeg, GoffEnd = items[0], items[1], int(items[2]), int(items[3]), items[14], items[15], int(items[16]), int(items[17])
		orgOffBeg = SoffBeg + GoffBeg
		orgOffEnd = SoffBeg + GoffEnd
	
		print >> fout, '\t'.join([pmid, line, Gid, Gstr, unicode(str(orgOffBeg), 'utf-8'), unicode(str(orgOffEnd), 'utf-8')])
	
