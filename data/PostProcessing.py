#!/usr/bin/env python
import codecs
import pickle
import re

Sentence, Estr, Gid, CGE, CGEScore, GeneClass, UniProtID, VogelSym, TSGene, Cstr = 1, 4, 13, 15, 16, 19, 21, 22, 23, 30

infile = "/home/heejin/work/WebServer/data/Medline/medline_all_merged.txt"
outfile = "/home/heejin/work/WebServer/data/Medline/medline_all_merged_ver1.txt"
picklef = open('/home/heejin/resources/CancerGenesETC/EntrezId-Sym-Dic.pickle', 'rb')
EntrezSymDic = pickle.load(picklef)
OncoDic = pickle.load(picklef)
TSDic = pickle.load(picklef)
picklef.close()
HedgeKeywords = 'investigate|evaluate|examine|verify|determine|analyze|measure|understand|assess'
HedgeKeywordsPast = 'investigated|evaluated|examined|verified|determined|analyzed|measured|assessd'
HedgePattern = re.compile('objective:|aim:|methods:|study:|to (%s)|((we|authors) (%s))'%(HedgeKeywords, HedgeKeywordsPast))

fin = codecs.open(infile, encoding="utf8")
fout = codecs.open(outfile, mode='w', encoding="utf8")

for line in fin:
	OMITFLAG = False
	items = line.strip().split('\t')

	# deal with 'inactivation' keyword
	if items[Estr].lower()[:9] == 'inactivat':
		if items[CGE] == 'increased':
			#print items[0]
			items[CGE] = 'decreased'
			if items[GeneClass] == 'Oncogene': 
				items[GeneClass] = 'Tumor suppressor gene'
				if items[Gid] in TSDic.keys():
					items[UniProtID] = TSDic[items[Gid]][1]
					items[VogelSym] = TSDic[items[Gid]][1]
					items[TSGene] = TSDic[items[Gid]][1]
				else: 
					items[UniProtID] = '\\N'
					items[VogelSym] = '\\N'
					items[TSGene] = '\\N'
					
			elif items[GeneClass] == 'Tumor suppressor gene': 
				items[GeneClass] = 'Oncogene'
				if items[Gid] in OncoDic.keys():
					items[UniProtID] = OncoDic[items[Gid]][1]
					items[VogelSym] = OncoDic[items[Gid]][2]
					items[TSGene] = OncoDic[items[Gid]][3]
				else: 
					items[UniProtID] = '\\N'
					items[VogelSym] = '\\N'
					items[TSGene] = '\\N'

	for i in range(0,len(items)-2-30,3):
		if items[Cstr+i].lower() == "tumor":
			if items[Sentence][int(items[Cstr+i+1]):int(items[Cstr+i+1])+8].lower() == ' necrosis':
				OMITFLAG = True
		if items[Cstr+i].lower() in ["ras", 'ra']: 
				OMITFLAG = True

	if HedgePattern.search(items[Sentence].lower()):
		print items[Sentence]
		print HedgePattern.search(items[Sentence].lower()).group(0)
		print 'before', items[CGEScore]
		items[CGEScore] = str(float(items[CGEScore]) * 0.5)
		print 'after', items[CGEScore]
			
	if not OMITFLAG: print >> fout, '\t'.join(items)

fin.close()
fout.close()
				
