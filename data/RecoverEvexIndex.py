#!/usr/bin/env python
import MySQLdb as mdb
import codecs

con = mdb.connect("localhost", "heejin", "skscjswo", "evex")
with con:
	cur = con.cursor()
	cur.execute('set names "utf8"')
	cur.execute("select id, string, offsetBeg, offsetEnd from occurrence_ggp")
	ggpInfo = cur.fetchall()
	
ggpDict = dict(map(lambda x: (x[0], x[1:]), ggpInfo))
print ggpDict.items()[0]

def check_equaltiy(term1, term2):
    if term1 == term2: return True
    if (term1[0].lower()+term1[1:]) == (term2[0].lower()+term2[1:]): return True
    return False

if __name__ == "__main__":
	import argparse
	import os
	import re
	argParser = argparse.ArgumentParser()
	argParser.add_argument("infile", help="annotation_units.txt")
	argParser.add_argument("txtDir", help="dir with abstract txt files")
	argParser.add_argument("outfile", help="output file")
	args = argParser.parse_args()

	fin = codecs.open(args.infile, encoding="utf-8")
	fout = codecs.open(args.outfile, mode='w', encoding="utf-8")
	for line in fin:
		items = line.strip().split('\t')
		pmid, line, geneId, geneStr = items[0], items[1], int(items[12]), items[13]
		#geneStr, orgOffBeg, orgOffEnd = ggpDict[geneId]
		_, orgOffBeg, orgOffEnd = ggpDict[geneId]
	
		abstract = codecs.open(os.path.join(args.txtDir, pmid+".txt"), encoding="utf-8").read()
		if not check_equaltiy(abstract[int(orgOffBeg):int(orgOffEnd)], geneStr):
			offsets = set([int(orgOffBeg) - m.start() for m in re.finditer(geneStr, abstract)])
			if not offsets: offsets = set([0])
			offset = min(list(offsets), key=lambda x: abs(x))
			orgOffBeg, orgOffEnd = int(orgOffBeg) - offset, int(orgOffEnd) - offset	
		print >> fout, '\t'.join([pmid, line, unicode(str(geneId), 'utf-8'), geneStr, unicode(str(orgOffBeg), 'utf-8'), unicode(str(orgOffEnd), 'utf-8')])
	
