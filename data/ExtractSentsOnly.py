#!/usr/bin/env python
import glob
import codecs
import os

DIR = "./Medline/"
TXTFILE = "medline_annotation_units.txt.adjusted"
OUTFILE = "medline_sents_only.txt"

fin = codecs.open(os.path.join(DIR, TXTFILE), encoding='utf-8')
fout = codecs.open(os.path.join(DIR, OUTFILE), mode='w', encoding='utf-8')
for line in fin: print >> fout, line.strip().split('\t')[1]
fin.close()
fout.close()

"""
DIR = "./Medline/"
TXTFILE = "medline_annotation_units.txt.adjusted."
OUTFILE = "medline_sents_only.txt."

fs = glob.glob(os.path.join(DIR, TXTFILE+"*"))
print fs

for f in fs:
	fin = codecs.open(f, encoding='utf-8')
	index = f.split(".")[-1]
	fout = codecs.open(os.path.join(DIR, OUTFILE+index), mode='w', encoding='utf-8')

	for line in fin: print >> fout, line.strip().split('\t')[1]
	fin.close()
	fout.close()
"""
