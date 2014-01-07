#!/usr/bin/env pyyhon
import xml.dom.minidom
import Matrix
from UnifiedData import *

#########################
# Annotation_Unit Class #
#########################
class Annotation_Unit(UnifiedData):

	def __init__(self, id_str, phase, cancer_type, string, pmid, gene, gene_range, event_1, event_1_range, event_1_type, event_2, event_2_range, event_2_type, cancer_terms, CGE, CCS, PT, IGE, GeneClass):
		UnifiedData.__init__(self, string)

		self.id_str = id_str
		self.phase = phase
		self.cancer_type = cancer_type
		self.pmid = pmid
		self.CGE = CGE
		self.CCS = CCS
		self.PT = PT
		self.IGE = IGE
		self.GeneClass = GeneClass

		self.gene = (gene, tuple(map(lambda x: int(x), gene_range.split('-'))))
	
		try:
			self.event_1 = (event_1, tuple(map(lambda x: int(x), event_1_range.split('-'))), event_1_type)
		except ValueError:
			self.event_1 = (event_1, (-1, -1), event_1_type)

		try:
			self.event_2 = (event_2, tuple(map(lambda x: int(x), event_2_range.split('-'))), event_2_type)
		except ValueError:
			self.event_2 = (event_2, (-1, -1), event_2_type)

		self.cancer_terms =  map(lambda x: (x[0], tuple(map(lambda y: int(y), x[1].split('-')))), cancer_terms)

	def get_indexes(self, term_range): return self.__get_indexes(term_range)
	def __get_indexes(self, term_range):
		start, end = None, None
		for index, (i, j)  in enumerate(self.parseResult.get_row(RANGE)):
			if i <= term_range[0] <= j: start = index
			if i <= term_range[1] <= j: end = index
		if (start == None) or (end == None): #return []
			raise IndexError('\n'.join([self.pmid, self.orgSent, str(term_range), self.orgSent[term_range[0]:term_range[1]], str(self.parseResult.get_row(0))]))
		return range(start, end+1)

	def get_CCS(self):
		return self.CCS
	def get_PT(self):
		return self.PT
	def get_GeneClass(self):
		return self.GeneClass

	def set_CCS(self, CCS):
		self.CCS = CCS

	def get_words(self):
		return self.parseResult.get_row(TOKEN)

	def get_gene(self):
		return self.gene[0]
	def get_gene_indexes(self):
		return self.__get_indexes(self.gene[1])

	def get_event_1(self):
		return self.event_1[0]
	def get_event_1_indexes(self):
		return self.__get_indexes(self.event_1[1])

	def get_event_2(self):
		return self.event_2[0]
	def get_event_2_indexes(self):
		return self.__get_indexes(self.event_2[1])

	def get_cancer_terms(self):
		terms = []
		for cancer_term in self.cancer_terms:
			terms.append(cancer_term[0])
		return terms

	def get_cancer_terms_indexes_list(self):
		indexes_list = []
		for cancer_term, cancer_term_index in self.cancer_terms:
			indexes_list.append(self.__get_indexes(cancer_term_index))
		return indexes_list


###########
# Readers #
###########
def get_annotation_units(xml_file):
	"""input: the xml file of gene_cancer corpus
	output: aus, a list of preliminarily instantiated aus (only the information in the corpus are loaded)""" 
	aus = []
	
	dom = xml.dom.minidom.parse(xml_file)
	for xml_annotation_unit in dom.getElementsByTagName("annotation_unit"):

		au_id = xml_annotation_unit.getAttribute("id")
		au_phase = xml_annotation_unit.getAttribute("phase")
		au_cancer_type = xml_annotation_unit.getAttribute("cancer_type")

		au_string = xml_annotation_unit.getElementsByTagName("sentence")[0].firstChild.data.strip()
		au_pmid = xml_annotation_unit.getElementsByTagName("sentence")[0].getAttribute("pmid")

		au_gene = xml_annotation_unit.getElementsByTagName("gene")[0].firstChild.data.strip()
		au_gene_range = xml_annotation_unit.getElementsByTagName("gene")[0].getAttribute("range")

		au_event_1 = xml_annotation_unit.getElementsByTagName("expression_change_keyword_1")[0].firstChild.data.strip()
		au_event_1_range = xml_annotation_unit.getElementsByTagName("expression_change_keyword_1")[0].getAttribute("range")
		au_event_1_type = xml_annotation_unit.getElementsByTagName("expression_change_keyword_1")[0].getAttribute("type")
		
		au_event_2 = xml_annotation_unit.getElementsByTagName("expression_change_keyword_2")[0].firstChild.data.strip()
		au_event_2_range = xml_annotation_unit.getElementsByTagName("expression_change_keyword_2")[0].getAttribute("range")
		au_event_2_type = xml_annotation_unit.getElementsByTagName("expression_change_keyword_2")[0].getAttribute("type")

		au_cancer_terms = []
		for xml_cancer_term in xml_annotation_unit.getElementsByTagName("cancer_term"):
			au_cancer_terms.append((xml_cancer_term.firstChild.data.strip(), xml_cancer_term.getAttribute("range")))
		
		au_CGE = xml_annotation_unit.getElementsByTagName("CGE")[0].getAttribute("value")
		au_CCS = xml_annotation_unit.getElementsByTagName("CCS")[0].getAttribute("value")
		au_PT = xml_annotation_unit.getElementsByTagName("PT")[0].getAttribute("value")
		au_IGE = xml_annotation_unit.getElementsByTagName("IGE")[0].getAttribute("value")
		au_GeneClass = xml_annotation_unit.getElementsByTagName("GeneClass")[0].getAttribute("value")

		aus.append(Annotation_Unit(au_id, au_phase, au_cancer_type, au_string, au_pmid, au_gene, au_gene_range, au_event_1, au_event_1_range, au_event_1_type, au_event_2, au_event_2_range, au_event_2_type, au_cancer_terms, au_CGE, au_CCS, au_PT, au_IGE, au_GeneClass))

	return aus

def __ProduceRanges(OffBeg, OffEnd):
	return OffBeg+'-'+str(int(OffEnd)-1)

def get_annotation_units_from_txt(txt_file):
	import codecs
	aus = []
	fin = codecs.open(txt_file, encoding='utf-8')
	cnt = 1
	for line in fin:
		#print line
		items = line.strip().split('\t')
		pmid, sentence, SoffBeg, SoffEnd, Eid, Etype, Econf, Estr, EoffBeg, EoffEnd, E2id, E2str, E2offBeg, E2offEnd, Gid, Gstr, GoffBeg, GoffEnd, NCIid = items[0:19]
		cancer_terms = items[19:]

		au_id = 'au' + str(cnt)
		au_phase = 'no_phase'
		au_cancer_type = NCIid
		au_string = sentence
		au_pmid = pmid
		au_gene = Gstr
		au_gene_range = __ProduceRanges(GoffBeg, GoffEnd)
		if E2str != "\\N":
			au_event_1 = E2str
			au_event_1_range = __ProduceRanges(E2offBeg, E2offEnd) 
			au_event_1_type = 'Gene_expression'
		else:
			au_event_1, au_event_1_range, au_event_1_type = "None", "None", "None"
		au_event_2 = Estr
		au_event_2_range = __ProduceRanges(EoffBeg, EoffEnd)
		au_event_2_type = Etype
		au_cancer_terms = map(lambda x: (x[0], __ProduceRanges(x[1], x[2])), [cancer_terms[i:i+3] for i in range(0, len(cancer_terms), 3)])  
		au_CGE, au_CCS, au_PT, au_IGE, au_GeneClass = None, None, None, None, None
		aus.append(Annotation_Unit(au_id, au_phase, au_cancer_type, au_string, au_pmid, au_gene, au_gene_range, au_event_1, au_event_1_range, au_event_1_type, au_event_2, au_event_2_range, au_event_2_type, au_cancer_terms, au_CGE, au_CCS, au_PT, au_IGE, au_GeneClass))
		cnt = cnt + 1

	fin.close()
	return aus



if __name__ == "__main__":
	import random
	import codecs
	#aus =  get_annotation_units_from_txt("../data/prostate_cancer/prostate_cancer_annotation_units.txt", 'prostate cancer' )
	aus =  get_annotation_units("../corpus/CoMAGC.xml")
	#aus = UnifiedReader(aus, "../data/prostate_cancer/prostate_cancer_sents_parsed.con", "../data/prostate_cancer/prostate_cancer_sents_parsed.dep")
	aus = UnifiedReader(aus, "../corpus/sents_parsed.con", "../corpus/sents_parsed.dep")
	#index = random.randint(0,len(aus)-1)
	#au = aus[index]
	outfile = codecs.open("AnnotationUnit.result",mode='w',encoding='utf-8')	

	for au in aus:
		print >> outfile, "id_str", au.id_str
		print >> outfile, "phase", au.phase
		print >> outfile, "cancer_type", au.cancer_type
		print >> outfile, "pmid", au.pmid
		print >> outfile, "CGE", au.CGE
		print >> outfile, "CCS", au.CCS
		print >> outfile, "PT", au.PT
		print >> outfile, "IGE", au.IGE
		print >> outfile, "gene", au.gene
		print >> outfile, "event_1", au.event_1
		print >> outfile, "event_2", au.event_2
		print >> outfile, "cancer_terms", au.cancer_terms

		print >> outfile, "get_CCS", au.get_CCS()
		print >> outfile, "get_words", au.get_words()
		print >> outfile, "get_ranges", au.parseResult.get_row(RANGE)
		print >> outfile, "get_gene", au.get_gene()
		print >> outfile, "get_gene_indexes", au.get_gene_indexes()

		print >> outfile, "get_event_1", au.get_event_1()
		print >> outfile, "get_event_1_indexes", au.get_event_1_indexes()

		print >> outfile, "get_event_2", au.get_event_2()
		print >> outfile, "get_event_2_indexes", au.get_event_2_indexes()

		print >> outfile, "get_cancer_terms", au.get_cancer_terms()
		print >> outfile, "get_cancer_terms_indexes_list", au.get_cancer_terms_indexes_list()

