#!/usr/bin/env python
import os
import codecs
import re
import sys

MedlineDir = "/home/heejin/work/WebServer/data/Medline/medline"
dataDir = "/home/heejin/work/WebServer/data/Medline"
end_pattern = '\n[A-Z]+'
line_pattern = '[ ]*\n[ ]+'
"""
#collect pmids
InFile = codecs.open("/home/heejin/work/WebServer/data/Medline/medline_all_merged.txt",encoding="utf8")
pmids = set()
for line in InFile:
	pmids.add(line.strip().split('\t')[0])
InFile.close()
print len(pmids)
"""
pmids = ['10667208', '17072648']

def GetInfo(pmid, medline_str, marker):
	index = medline_str.find(marker) + len(marker)
	if index == -1:
		raise ValueError(pmid+': '+marker)

	try:
		end_index = re.search(end_pattern, medline_str[index:]).start()
	except AttributeError, e:
		print >> sys.stderr, pmid
		print >> sys.stderr, e
		raise
	item = re.sub(line_pattern, ' ', medline_str[index:index+end_index])

	return item

#OutFile = codecs.open("/home/heejin/work/WebServer/data/Medline/abstract_additional_infos.txt",mode='w',encoding="utf8")
OutFile = codecs.open("/home/heejin/work/WebServer/data/Medline/temp.txt",mode='w',encoding="utf8")

for pmid in pmids:
	#print pmid
	medlineF = codecs.open(os.path.join(MedlineDir, pmid+".medline"), encoding="utf8")
	medline_str = medlineF.read()
	medlineF.close()

	jt_marker = "JT  - " # full journal title
	ta_marker = "TA  - " # journal title (abbreviation)
	titles = map(lambda x: GetInfo(pmid, medline_str, x), [jt_marker, ta_marker])

	date = re.search('DP  - (.*?)\n', medline_str).group(1)
	try: volume = re.search('VI  - (.*?)\n', medline_str).group(1)
	except AttributeError: volume = '\N'
	try: issue = re.search('IP  - (.*?)\n', medline_str).group(1)
	except AttributeError: issue = '\N'
	pages = re.search('PG  - (.*?)\n', medline_str).group(1)
	authors = re.findall('AU  - (.*?)\n', medline_str)
	citation = re.search('SO  - (.*)', medline_str, re.S).group(1).strip()
	#if '  - ' in citation: raise ValueError(pmid)
	#citation = re.sub(line_pattern, ' ', citation)


	if len(authors) == 0: authors = ["No authors listed"]
	items = [pmid, citation, '|'.join(authors)] + titles + [date, volume, issue, pages] 
	#print pmid
	#print items
	#print citation
	assert len(items) == 9

	print >> OutFile, '\t'.join(items)
	if '\n' in '\t'.join(items):
		print pmid
		print '\t'.join(items)

OutFile.close()
