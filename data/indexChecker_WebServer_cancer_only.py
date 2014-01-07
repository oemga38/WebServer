#!/usr/bin/env python
import codecs
import re
import sys

def check_equaltiy(term1, term2):
	if term1 == term2: return True
	try:
		if (term1[0].lower()+term1[1:]) == (term2[0].lower()+term2[1:]): return True 
	except IndexError: return True
	if term1.lower() == term2.lower(): return True
	return False

def print_errors(pmid, sentence, errors):
	print >> sys.stderr, "###", pmid
	print >> sys.stderr, sentence
	print >> sys.stderr, errors


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("infile", help="annotation_units file to check index")
	parser.add_argument("outfile", help="out file to write new annotation_inits file with adjusted indexes")
	args = parser.parse_args()
	
	fout = codecs.open(args.outfile, mode="w", encoding="utf-8")
	fin = codecs.open(args.infile, encoding="utf-8")

	for line in fin:
		items = line.strip().split('\t')
		pmid, sentence, SoffBeg, SoffEnd, Eid, Etype, Econf, Estr, EoffBeg, EoffEnd, E2id, E2str, E2offBeg, E2offEnd, Gid, Gstr, GoffBeg, GoffEnd, NCIid = items[:19]
		cancers = items[19:]

		errors = list()
		for Cstr, CoffBeg, CoffEnd in [cancers[i:i+3] for i in range(0, len(cancers), 3)]:
			if not check_equaltiy(sentence[int(CoffBeg):int(CoffEnd)], Cstr): errors.append((Cstr, CoffBeg, CoffEnd))

		if errors:
			print_errors(pmid, sentence, errors)

		if not errors:
			print >> fout, '\t'.join([pmid, sentence, SoffBeg, SoffEnd, Eid, Etype, Econf, Estr, str(EoffBeg), str(EoffEnd), E2id, E2str, str(E2offBeg), str(E2offEnd), Gid, Gstr, str(GoffBeg), str(GoffEnd), NCIid]+cancers)
