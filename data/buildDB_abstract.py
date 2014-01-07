#!/usr/bin/env python
import os
import glob
import codecs
#import MySQLdb

dataDir = "/home/heejin/work/WebServer/data/Medline"
absDir = "/home/heejin/work/WebServer/data/Medline/txt"

mergedFiles = glob.glob(os.path.join(dataDir, "medline_merged.txt.[0-9]"))
mergedFiles += glob.glob(os.path.join(dataDir, "medline_merged.txt.[0-9][0-9]"))
pmids = set()
for mergedFile in mergedFiles:
	print mergedFile
	fin = codecs.open(mergedFile,encoding='utf8')
	for line in fin:
		pmids.add(line.strip().split('\t')[0])
	fin.close()

print len(pmids)

fout = codecs.open("dearCuong.txt",mode='w',encoding="utf8")
#con = MySQLdb.connect('localhost', 'heejin', 'skscjswo', 'WebSearchEngine')
#with con:
#	cur = con.cursor()
#	cur.execute('set names "utf8"')
#	cur.execute('set charset "utf8"')

	#test = 0
if True:
	for pmid in pmids:
		#test += 1
		txtFile = codecs.open(os.path.join(absDir, pmid+'.txt'),encoding="utf8")
		#		cur.execute("insert into abstracts (pmid) values ('%s')"%pmid)	
		#		cur.execute("update abstracts set abstract=load_file('%s') where pmid='%s'"%(txtFile,pmid))
		#if test > 10: break
		print >> fout, pmid+'\t'+txtFile.read().strip().replace('\n','<CUONG>')
		txtFile.close()
