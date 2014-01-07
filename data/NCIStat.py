#!/usr/bin/env python
import codecs
import glob

fs = glob.glob("./Medline/cTerms/*.diseaseOff")
conceptDic = dict()

for f in fs:
	fin = codecs.open(f, encoding="utf8")
	for line in fin:
		NCIid = line.strip().split('\t')[3]
		try: conceptDic[NCIid] += 1
		except KeyError: conceptDic[NCIid] = 1


