#!/usr/bin/env python
import xml.dom.minidom
import urllib
import nltk
import os
import sys
import codecs
import re

eutils = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
efetch = "efetch.fcgi?"


def abstract_retriever(pmid, retmode="text", db="pubmed"):
	print >> sys.stderr, "#retrieving abstract from PUBMED, %s" % pmid
	#return (pmid, unicode(urllib.urlopen(eutils+efetch+"db="+db+"&retmode="+retmode+"&id="+pmid).read(), encoding='utf-8'))
	if retmode == "xml": return (pmid, urllib.urlopen(eutils+efetch+"db="+db+"&retmode="+retmode+"&id="+pmid).read())
	elif retmode == "text": return (pmid, urllib.urlopen(eutils+efetch+"db="+db+"&retmode="+retmode+"&id="+pmid+"&rettype=medline").read())


def xml2txt(xml_data):
	out_string = str()

	dom = xml.dom.minidom.parseString(xml_data)

	ArtcTtl = dom.getElementsByTagName("ArticleTitle")
	try:
		out_string = ArtcTtl[0].firstChild.data.strip()+"\n"
	except IndexError:
		pass

	Abst = dom.getElementsByTagName("AbstractText")
	abstract = str()
	try:
		abstract = Abst[0].firstChild.data.strip()
	except IndexError:
		pass

	out_string += abstract

	return out_string

def medline2txt(medline_str):
	out_string = str()

	ti_marker = "TI  - "
	ab_marker = "AB  - "
	oab_marker = "OAB - "
	ti_index = medline_str.find(ti_marker) + len(ti_marker) 
	ab_index = medline_str.find(ab_marker) + len(ab_marker)
	oab_index = medline_str.find(oab_marker) + len(oab_marker)
	end_pattern = '\n[A-Z]+'
	line_pattern = '[ ]*\n[ ]+'

	ti_end = re.search(end_pattern, medline_str[ti_index:]).start()
	ti = re.sub(line_pattern, ' ', medline_str[ti_index:ti_index+ti_end])
	ab, oab = '', ''
	if ab_index != -1:
		ab_end = re.search(end_pattern, medline_str[ab_index:]).start()
		ab = '\n' + re.sub(line_pattern, ' ', medline_str[ab_index:ab_index+ab_end])
	elif oab_index != -1:
		print "oab"
		oab_end = re.search(end_pattern, medline_str[oab_index:]).start()
		oab = '\n' + re.sub(line_pattern, ' ', medline_str[oab_index:oab_index+oab_end])

	return ti + ab + oab


def GetTxtFromPmid(pmid, type_document):
	"""input: pmid (str)
	output: txt (str) of abstract"""

	(pmid, content) = abstract_retriever(pmid, retmode=type_document)
	if type_document == "xml": return xml2txt(content)
	elif type_document == "text": return medline2txt(content)

	
def sent_tokenizer(string):
	nltk_tool = nltk.data.load('tokenizers/punkt/english.pickle')
	return '\n'.join(nltk_tool.tokenize(string))

def CreateTxtFileFromPmid(out_dir, pmid, type_document):
	txt = GetTxtFromPmid(pmid, type_document)
	fout = codecs.open(os.path.join(out_dir,pmid+".txt"), encoding='utf-8',mode='w')
	#fout.write(sent_tokenizer(txt))
	fout.write(txt)
	fout.close()

if __name__ == "__main__":
	import argparse

	arg_parser = argparse.ArgumentParser(description="given a set of PMIDs, produce a set of txt files")
	arg_parser.add_argument('pmid_list', help="a file containing pmids separated by newline")
	arg_parser.add_argument('out_dir', help="output directory")
	arg_parser.add_argument('-f', '--from_cnt', default=1, help="line count of PMID file to start processing")
	arg_parser.add_argument('-t', '--type_document', default="text", help="pubmed download type: text or xml")
	args = arg_parser.parse_args()

	fin = open(args.pmid_list)
	count = 1
	for line in fin:	
		if count >= int(args.from_cnt): 
			#print "wow"
			CreateTxtFileFromPmid(args.out_dir, line.strip(), args.type_document)
		print count
		count = count + 1

