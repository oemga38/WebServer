#!/usr/bin/env python
import codecs
import os
import sys
import DiseaseDic
import nltk

#dictFile = open("./dic/breast_cancer_terms_with_head.txt")
absDir = "./breast_cancer/txt/"
rangeFile = codecs.open("./breast_cancer/breast_cancer_gene_expression_change_ranges.txt",encoding='utf-8')
outFile = codecs.open("./breast_cancer/breast_cancer_annotation_units.txt",'w',encoding='utf-8')
diseaseDic = DiseaseDic.DiseaseDic("./dic/breast_cancer_terms_with_head.txt")
nltk_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

cnt = 0
for line in rangeFile:
	pmid, event_id, event_type, confidence_min, Estr, EoffBeg, EoffEnd, theme_event_id, E2str, E2offBeg, E2offEnd, theme_ggp_id, Gstr, GoffBeg, GoffEnd =  line.strip().split('\t')
	indexes = map(lambda x: int(x), filter(lambda x: x!='\\N',[EoffBeg, EoffEnd, E2offBeg, E2offEnd, GoffBeg, GoffEnd]))
	min_index = min(indexes)
	max_index = max(indexes)

	absText = codecs.open(os.path.join(absDir, pmid+'.txt'), encoding='utf-8').read()
	sentRanges = list()
	prev_index = 0
	for line in absText.split('\n'):
		spans = nltk_tokenizer.span_tokenize(line.strip())
		sentRanges.extend(map(lambda x: (x[0]+prev_index, x[1]+prev_index), spans))
		prev_index = prev_index + len(line) + 1
	
	for front_index, end_index in sentRanges:
		adjIndx = lambda x: x == '\\N' and x or str(int(x)-front_index)
		if min_index in range(front_index, end_index+1) and max_index in range(front_index, end_index+1):
			#pmid, sentence, event_id, event_type, confidence_min, Estr, EoffBeg, EoffEnd, theme_event_id, E2str, E2offBeg, E2offEnd, theme_ggp_id, Gstr, GoffBeg, GoffEnd, (Cstr, CoffBeg, CoffEnd)+
			diseaseMatches = diseaseDic.getMatches(absText[front_index:end_index])
			if diseaseMatches:
				output = [pmid, absText[front_index:end_index], event_id, event_type, confidence_min, Estr, adjIndx(EoffBeg), adjIndx(EoffEnd), theme_event_id, E2str, adjIndx(E2offBeg), adjIndx(E2offEnd), theme_ggp_id, Gstr, adjIndx(GoffBeg), adjIndx(GoffEnd)] + map(lambda x: str(x), sum(map(lambda x: list(x), diseaseMatches),[]))
				print >> outFile, '\t'.join(output)
			break
			
	cnt = cnt + 1
	print >> sys.stderr, cnt
	#if cnt > 10: break
