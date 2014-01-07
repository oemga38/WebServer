#!/usr/bin/env python
import codecs
import random

fin = codecs.open("/home/heejin/work/WebServer/data/medline_all_merged_ver1.txt",encoding='utf8')
fout = codecs.open("/home/heejin/work/WebServer/data/performance_test.txt",mode='w',encoding='utf8')

for line in fin:
	if random.randrange(0,527728) < 1000:
		print >> fout, line.strip()

fout.close()
fin.close()

