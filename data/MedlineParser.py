#!/usr/bin/env python
import os
import threading
import codecs
import re
import sys

OUTDIR = ''

def medline2txt(pmid, medline_str):
	out_string = str()

	ti_marker = "TI  - "
	ab_marker = "AB  - "
	oab_marker = "OAB - "
	ti_index = medline_str.find(ti_marker) + len(ti_marker)
	ab_index = medline_str.find(ab_marker) + len(ab_marker)
	oab_index = medline_str.find(oab_marker) + len(oab_marker)
	end_pattern = '\n[A-Z]+'
	line_pattern = '[ ]*\n[ ]+'

	try:
		ti_end = re.search(end_pattern, medline_str[ti_index:]).start()
	except AttributeError, e:
		print >> sys.stderr, pmid
		print >> sys.stderr, e
		raise
	ti = re.sub(line_pattern, ' ', medline_str[ti_index:ti_index+ti_end])
	ab, oab = '', ''
	if ab_index != -1:
		ab_end = re.search(end_pattern, medline_str[ab_index:]).start()
		ab = '\n' + re.sub(line_pattern, ' ', medline_str[ab_index:ab_index+ab_end])
	elif oab_index != -1:
		print "oab"
		oab_end = re.search(end_pattern, medline_str[oab_index:]).start()
		oab = '\n' + re.sub(line_pattern, ' ', medline_str[oab_index:oab_index+oab_end])

	return ti + ab + oab


class MedlineParser(threading.Thread):
	def __init__(self, infile):
		threading.Thread.__init__(self)
		self.infile = infile
	def run(self):
		pmid = os.path.split(self.infile)[1].split('.')[0]
		outfile = os.path.join(OUTDIR, pmid+'.txt')
		if not os.path.exists(outfile):
			fin = codecs.open(self.infile, encoding='utf-8')
			abstract = medline2txt(pmid, fin.read().strip())
			fin.close()
			fout = codecs.open(outfile, mode='w', encoding="utf-8")
			fout.write(abstract)
			fout.close()
	
if __name__ == "__main__":
	import argparse
	import glob

	arg_parser = argparse.ArgumentParser(description="given INDIR with .medline files, produce .txt files with abstracts to OUTDIR")
	arg_parser.add_argument('inDir', help="a directory with .medline files")
	arg_parser.add_argument('outDir', help="output directory")
	args = arg_parser.parse_args()

	OUTDIR = args.outDir

	MAX_THREAD = 32
	curr = 0
	threads=[None] * MAX_THREAD
	cnt = 0
	for infile in glob.glob(os.path.join(args.inDir, '*.medline')):
		threads[curr] = MedlineParser(infile)
		threads[curr].start()
		curr += 1
		cnt += 1
		if curr == MAX_THREAD:
			while curr>0:
				curr -= 1
				threads[curr].join()
			print cnt
