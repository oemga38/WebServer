#!/usr/bin/env python
import codecs
import os

#fadditional = codecs.open("/home/heejin/work/WebServer/data/Medline/abstract_additional_infos.txt",encoding="utf8")
fadditional = codecs.open("/home/heejin/work/WebServer/data/Medline/temp.txt",encoding="utf8")
#fout = codecs.open("/home/heejin/work/WebServer/data/tcdang.txt",mode='w',encoding='utf8')
fout = codecs.open("/home/heejin/work/WebServer/data/tcdang_2.txt",mode='w',encoding='utf8')
txtDir = "/home/heejin/work/WebServer/data/Medline/txt"
for line in fadditional:
	pmid = line.strip().split('\t')[0]
	if pmid in ['10667208', '17072648']:
		fin = codecs.open(os.path.join(txtDir, pmid+'.txt'), encoding="utf8")
		text = fin.read()
		fin.close()

		print len(line.strip().split('\t'))
		assert len(line.strip().split('\t')) == 9
		print >> fout, line.strip() + '\t' + text.replace('\n','<CUONG>')

fadditional.close()
fout.close()

