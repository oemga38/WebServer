#!/usr/bin/env python
import os
import codecs
import re
import sys

DiseaseDir = "/home/heejin/work/WebServer/data/Medline/cTerms"

#collect pmids
InFile = codecs.open("/home/heejin/work/WebServer/data/Medline/medline_all_merged.txt",encoding="utf8")
pmids = set()
for line in InFile:
    pmids.add(line.strip().split('\t')[0])
InFile.close()
print len(pmids)

outFile = codecs.open("/home/heejin/work/WebServer/data/Medline/cancerIndexAbstract.txt",mode="w",encoding="utf8")

cnt = 0
for pmid in pmids:
	cnt += 1
	dFile = codecs.open(os.path.join(DiseaseDir,pmid+'.diseaseOff'), encoding="utf8")
	cDic = dict()
	for line in dFile:
		cStr, Sindx, Eindx, Cid = line.strip().split('\t')
		try:
			cDic[Cid][0] += ';'+Sindx
			cDic[Cid][1] += ';'+Eindx
		except KeyError:
			cDic[Cid] = [Sindx, Eindx]
	dFile.close()

	for cID, Indexes in cDic.items():
		print >> outFile, '\t'.join([pmid, cID, Indexes[0], Indexes[1]])

	if cnt % 1000 == 0: print cnt

outFile.close()


