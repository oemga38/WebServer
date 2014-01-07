#!/usr/bin/env python
import codecs

NCIIDprostate="C4863"
NCIIDovarian="C7341"
NCIIDbreast="C4872"

fin = codecs.open('./breast_cancer/breast_cancer_result_for_webserver.txt.human',encoding='utf8')
fout = codecs.open('./breast_cancer/breast_cancer_result_for_webserver.txt.human.nciid',mode='w',encoding='utf8')

for line in fin:
	items = line.strip().split('\t')
	print >> fout, '\t'.join(items[:19]+[NCIIDbreast]+items[19:])
	
