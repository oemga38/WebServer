#!/usr/bin/env python
import codecs
import os
import sys
import argparse

#dictFile = open("./dic/breast_cancer_terms_with_head.txt")
absDir = "./Medline/txt/"
sentDir = "./Medline/sentsOffset/"
diseaseDir = "./Medline/cTerms/"
rangeFile = codecs.open("./Medline/medline_gene_expression_change_ranges.txt",encoding='utf-8')
outFile = codecs.open("./Medline/medline_annotation_units.txt",'w',encoding='utf-8')
adjIndx = lambda x, front_index: str(int(x)-front_index) if x.isdigit() else x

def GetSentRanges(pmid, textLenth):
	rangeFile = open(os.path.join(sentDir, pmid+'.sentOff'))
	sentRanges = map(lambda x: (int(x[0]), int(x[1])), [line.strip().split('\t') for line in rangeFile.readlines()])
	rangeFile.close()
	return sentRanges + [(str(int(sentRanges[-1][1])+1), textLenth)]

def GetDiseaseRanges(pmid):  
	# diseaseRanges: [ (diseaseTerm, OffBeg, OffEnd, NCIid) ]
	rangeFile = codecs.open(os.path.join(diseaseDir, pmid+'.diseaseOff'), encoding='utf8')
	diseaseRanges = map(lambda x: (x[0], int(x[1]), int(x[2])+1, x[3]), [line.strip().split('\t') for line in rangeFile.readlines()])
	rangeFile.close()
	return diseaseRanges
def GetDiseaseMatches(diseaseRanges, front, end):
	# return value: [ (NCIid, [ (diseaseTerm, OffBeg, OffEnd) ] ) ]
	diseaseDict = dict()
	for diseaseRange in diseaseRanges:
		if front <= diseaseRange[1] and diseaseRange[2] <= end:
			try: diseaseDict[diseaseRange[3]].append((diseaseRange[0], diseaseRange[1], diseaseRange[2]))
			except KeyError: diseaseDict[diseaseRange[3]] = [(diseaseRange[0], diseaseRange[1], diseaseRange[2])]
	return diseaseDict.items()
		
	

cnt = 0
for line in rangeFile:
	pmid, Eid, Etype, Econf, Estr, EoffBeg, EoffEnd, E2id, E2str, E2offBeg, E2offEnd, Gid, Gstr, GoffBeg, GoffEnd =  line.strip().split('\t')
	indexes = map(lambda x: int(x), filter(lambda x: x!='\\N',[EoffBeg, EoffEnd, E2offBeg, E2offEnd, GoffBeg, GoffEnd]))
	min_index, max_index = min(indexes), max(indexes)

	absText = codecs.open(os.path.join(absDir, pmid+'.txt'), encoding='utf-8').read()
	sentRanges = GetSentRanges(pmid, len(absText))
	diseaseRanges = GetDiseaseRanges(pmid)
	
	for front_index, end_index in sentRanges:
		if front_index <= min_index and max_index <= end_index: 
			#pmid, sentence, SoffBeg, SoffEnd, Eid, Etype, Econf, Estr, EoffBeg, EoffEnd, E2id, E2str, E2offBeg, E2offEnd, Gid, Gstr, GoffBeg, GoffEnd, NCIid, (Cstr, CoffBeg, CoffEnd)+
			diseaseMatches = GetDiseaseMatches(diseaseRanges, front_index, end_index)
			for diseaseMatch in diseaseMatches:  
				output = [pmid, absText[front_index:end_index], str(front_index), str(end_index), 
				Eid, Etype, Econf, Estr, adjIndx(EoffBeg,front_index), adjIndx(EoffEnd,front_index), 
				E2id, E2str, adjIndx(E2offBeg,front_index), adjIndx(E2offEnd,front_index), 
				Gid, Gstr, adjIndx(GoffBeg,front_index), adjIndx(GoffEnd,front_index), 
				diseaseMatch[0]]
				output += sum(map(lambda x: [x[0], str(x[1]-front_index), str(x[2]-front_index)], diseaseMatch[1]),[])
				print >> outFile, '\t'.join(output)
			break
			
	cnt = cnt + 1
	if cnt % 1000 == 0: print >> sys.stderr, cnt
	#if cnt > 100: break
