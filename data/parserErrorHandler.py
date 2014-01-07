#!/usr/bin/env python
import os
import shutil
import codecs

for i in range(16):
	orgFileName = "./Medline/medline_sents_parsed.con."+str(i)
	fin = codecs.open(orgFileName, encoding="utf8")
	fout = codecs.open("temp", encoding="utf8", mode="w")
		
	for line in fin:
		if line.startswith("("):
			print >> fout, line.strip()

	fin.close()
	fout.close()
	shutil.copy("temp", orgFileName)
