#!/usr/bin/env python
import codecs
import glob

files = glob.glob("./Medline/medline_merged.txt.[0-9]")
files += glob.glob("./Medline/medline_merged.txt.[0-9][0-9]")

outfile = codecs.open("./medline_all_merged.txt",mode='w',encoding='utf8')

cnt = 0
for orgfile in files:
	print orgfile
	fin = codecs.open(orgfile, encoding='utf8')
	for line in fin:
		cnt += 1
		print >> outfile, line.strip()
	fin.close()

print cnt
