#!/usr/bin/env python
import codecs
import re
import sys

def check_equaltiy(term1, term2):
	if term1 == term2: return True
	#try:
	#	if (term1[0].lower()+term1[1:]) == (term2[0].lower()+term2[1:]): return True 
	#except IndexError: return True
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
	parser.add_argument("mode", help="check or fix", choices=['check','fix'])
	parser.add_argument("--outfile", help="out file to write new annotation_inits file with adjusted indexes", default="temp.txt")
	args = parser.parse_args()
	if args.mode == "fix":
		fout = codecs.open(args.outfile, mode="w", encoding="utf-8")
	fin = codecs.open(args.infile, encoding="utf-8")

	for line in fin:
		items = line.strip().split('\t')
		pmid, sentence, SoffBeg, SoffEnd, Eid, Etype, Econf, Estr, EoffBeg, EoffEnd, E2id, E2str, E2offBeg, E2offEnd, Gid, Gstr, GoffBeg, GoffEnd = items[:18]
		cancers = items[19:]

		errors = list()
		error_on_E, error_on_E2, error_on_G = False, False, False
		if not check_equaltiy(sentence[int(EoffBeg):int(EoffEnd)], Estr): 
			error_on_E = True
			errors.append((Estr, EoffBeg, EoffEnd))
		if E2str != '\N' and not check_equaltiy(sentence[int(E2offBeg):int(E2offEnd)], E2str): 
			error_on_E2 = True
			errors.append((E2str, E2offBeg, E2offEnd))
		if not check_equaltiy(sentence[int(GoffBeg):int(GoffEnd)], Gstr): 
			error_on_G = True
			errors.append((Gstr, GoffBeg, GoffEnd))
		#for Cstr, CoffBeg, CoffEnd in [cancers[i:i+3] for i in range(0, len(cancers), 3)]:
		#	if not check_equaltiy(sentence[int(CoffBeg):int(CoffEnd)], Cstr): errors.append((Cstr, CoffBeg, CoffEnd))

		if errors:
			if args.mode == "check": print_errors(pmid, sentence, errors)
			indexes = list()
			for error in errors:
				text = error[0].replace('(','\(').replace(')','\)')
				indexes.append([int(error[1]) - m.start() for m in re.finditer(text, sentence)])
			indexes = filter(lambda x: len(x)>0, indexes)
			if not indexes: 
				#print_errors(pmid, sentence, errors)
				offsets = set([0])
			else:
				offsets = reduce(lambda x, y: x.intersection(y), map(lambda x: set(x), indexes))
				#if len(offsets) != 1: 
					#print_errors(pmid, sentence, errors)
					#print offsets
			offset = min(list(offsets), key=lambda x: abs(x))

			if error_on_E: 
				EoffBeg, EoffEnd = int(EoffBeg) - offset, int(EoffEnd) - offset
			if error_on_E2: 
				E2offBeg, E2offEnd = int(E2offBeg) - offset, int(E2offEnd) - offset 
			if error_on_G: 
				GoffBeg, GoffEnd = int(GoffBeg) - offset, int(GoffEnd) - offset
	
		if args.mode == "fix": print >> fout, '\t'.join([pmid, sentence, SoffBeg, SoffEnd, Eid, Etype, Econf, Estr, str(EoffBeg), str(EoffEnd), E2id, E2str, str(E2offBeg), str(E2offEnd), Gid, Gstr, str(GoffBeg), str(GoffEnd)]+cancers)
