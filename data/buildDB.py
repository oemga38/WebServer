#!/usr/bin/env python
import os
import glob
import codecs

dataDir = "/home/heejin/work/WebServer/data/Medline"
diseaseOffDir = "/home/heejin/work/WebServer/data/Medline/cTerms"

mergedFiles = glob.glob(os.path.join(dataDir, "medline_merged.txt.[0-9]*"))
pmids = set()
for mergedFile in mergedFiles:
	print mergedFile
	fin = codecs.open(mergedFile,encoding='utf8')
	for line in fin:
		pmids.add(line.strip().split('\t')[0])
	fin.close()

print len(pmids)

fout = codecs.open(os.path.join(dataDir, 'medline_diseaseOff_merged.txt'),mode='w',encoding='utf8')
for pmid in pmids:
	fin = codecs.open(os.path.join(diseaseOffDir, pmid+'.diseaseOff'))
	for line in fin:
		# pmid, cname, offS, offE, cid
		print >> fout, pmid+'\t'+line.strip()
	fin.close()
fout.close()
