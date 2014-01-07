#!/usr/bin/env python
import codecs
import pickle

CGEdic = {"Positive_regulation":"increased", "Negative_regulation":"decreased"}
termDic = {"normalTOcancer":"progression", "cancerTOnormal":"regression", "unidentifiable":"unidentifiable"}
AllSpecies = ['human', 'mouse', 'fly', 'yeast']
picklef = open('/home/heejin/resources/CancerGenesETC/EntrezId-Sym-Dic.pickle', 'rb')
EntrezSymDic = pickle.load(picklef)
OncoDic = pickle.load(picklef)
TSDic = pickle.load(picklef)
picklef.close()

def getGeneClass(CGE, CGEscore, CCS, CCSscore, PT, PTscore):
	if CCS == "unidentifiable": GeneClass = "NRC"
	elif PT == "observation": GeneClass = "Biomarker"
	elif CGE == "increased":
		if CCS == "normalTOcancer": GeneClass = "Oncogene"
		else: GeneClass = "Tumor suppressor gene"
	elif CGE == "decreased":
		if CCS == "normalTOcancer": GeneClass = "Tumor suppressor gene"
		else: GeneClass = "Oncogene"
	return (GeneClass, PTscore)

if __name__ == "__main__":
	import argparse
	argparser = argparse.ArgumentParser()
	argparser.add_argument("au_file", help="txt file with annotation units")
	argparser.add_argument("CCS_file", help="txt file with CCS results")
	argparser.add_argument("PT_file", help="txt file with PT results")
	argparser.add_argument("GN_file", help="txt file with gene normalization results")
	argparser.add_argument("Cancer_file", help="txt file with NCIid expansion results")
	argparser.add_argument("outfile", help="outfile")
	args = argparser.parse_args()
	
	annotationf = codecs.open(args.au_file, encoding="utf-8")
	CCSf = codecs.open(args.CCS_file, encoding="utf-8")
	PTf = codecs.open(args.PT_file, encoding='utf-8')
	GNFile = codecs.open(args.GN_file, encoding='utf-8')
	CancerFile = codecs.open(args.Cancer_file, encoding="utf-8")
	outf = codecs.open(args.outfile, mode='w', encoding='utf-8')

	cnt = 0
	for line in annotationf:
		items = line.strip().split('\t')
		pmid, sentence, SoffBeg, SoffEnd, Eid, Etype, Econf, Estr, EoffBeg, EoffEnd, E2id, E2str, E2offBeg, E2offEnd, Gid, Gstr, GoffBeg, GoffEnd, NCIid = items[0:19]
		cancers = items[19:]
	
		CGE = CGEdic[Etype]
		CGEprob = Econf
		CCS, CCSprob = CCSf.readline().strip().split('\t')
		PT, PTprob = PTf.readline().strip().split('\t')
		try: GNID = GNFile.readline().strip().split('\t')[4]
		except IndexError: GNID = ""
		try: GNsymbol = EntrezSymDic[GNID]
		except KeyError: GNsymbol = ""
		GeneClass, GeneClassProb = getGeneClass(CGE, CGEprob, CCS, CCSprob, PT, PTprob)

		CGEresult = CGE + '\t' + Econf
		CCSresult = '\t'.join([termDic[CCS], str(CCSprob)])
		GeneClassresult = '\t'.join([GeneClass, str(GeneClassProb)])

		NCIidExpanded = CancerFile.readline().strip()
		if not NCIidExpanded: print args.au_file, args.Cancer_file, cnt
		
		CancerGeneDBs = "\\N\t\\N\t\\N"
		if GeneClass == "Oncogene": 
			try: CancerGeneDBs = "%s\t%s\t%s" % OncoDic[GNID][1:]
			except KeyError: pass
		elif GeneClass == "Tumor suppressor gene": 
			try: CancerGeneDBs = "%s\t%s\t%s" % TSDic[GNID][1:]
			except KeyError: pass
		cnt += 1
		print >> outf, '\t'.join([pmid, sentence, SoffBeg, SoffEnd, Estr, EoffBeg, EoffEnd, E2str, E2offBeg, E2offEnd, Gstr, GoffBeg, GoffEnd, GNID, GNsymbol, CGEresult, CCSresult, GeneClassresult, CancerGeneDBs, NCIidExpanded] + cancers)

	outf.close()
	fin = codecs.open(args.outfile, encoding='utf8')
	for line in fin:
		if len(line.strip().split('\t')) <= 28: print line
	fin.close()
