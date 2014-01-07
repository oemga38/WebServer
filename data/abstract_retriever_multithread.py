#!/usr/bin/env python
import urllib2
import os
import sys
import codecs
import threading
import time

eutils = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
efetch = "efetch.fcgi?"
OUTDIR = ''
retmode = ''
db = 'pubmed'
outfile = ''

class Downloader(threading.Thread):
	def __init__(self, pmid):
		threading.Thread.__init__(self)
		self.pmid = pmid
	def run(self):
		#print self.pmid
		outfilename = os.path.join(OUTDIR, self.pmid+'.'+retmode)
		if not os.path.exists(outfilename):
			if retmode == "xml": urlAddress = eutils+efetch+"db="+db+"&retmode="+retmode+"&id="+self.pmid
			elif retmode == "medline": urlAddress= eutils+efetch+"db="+db+"&retmode=text&id="+self.pmid+"&rettype="+retmode
			while True:
				try:
					content = urllib2.urlopen(urlAddress, timeout=5).read().strip()
				except BaseException, e:
					print >> sys.stderr, "error in %s"%self.pmid
					print >> sys.stderr, e
					time.sleep(60)
				else:
					fout = codecs.open(outfilename, mode='w', encoding="utf-8")
					fout.write(unicode(content, encoding='utf-8'))
					fout.close()
					break
	
if __name__ == "__main__":
	import argparse

	arg_parser = argparse.ArgumentParser(description="given a set of PMIDs, produce a set of txt files")
	arg_parser.add_argument('pmid_list', help="a file containing pmids separated by newline")
	arg_parser.add_argument('out_dir', help="output directory")
	arg_parser.add_argument('-t', '--type_document', default="medline", help="pubmed download type: medline or xml")
	args = arg_parser.parse_args()
	OUTDIR = args.out_dir	
	retmode = args.type_document

	MAX_THREAD = 32
	curr = 0
	threads=[None] * MAX_THREAD
	fin = open(args.pmid_list)
	cnt = 0
	for line in fin:
		threads[curr] = Downloader(line.strip())
		threads[curr].start()
		curr += 1
		cnt += 1
		if curr == MAX_THREAD:
			while curr>0:
				curr -= 1
				threads[curr].join()
			print cnt
