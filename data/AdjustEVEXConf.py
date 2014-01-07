#!/usr/bin/env python
import codecs

fin = codecs.open("./Medline/medline_annotation_units.txt.adjusted", encoding="utf8")
lines = fin.readlines()
fin.close()

confs = [float(line.strip().split('\t')[6]) for line in lines]
print confs[0]
min_conf = min(confs)
max_conf = max(confs)
print min_conf, max_conf
width = max_conf - min_conf

fout = codecs.open("./Medline/medline_annotation_units.txt.adjusted.confNormed", mode='w', encoding="utf")
for line in lines:
	items = line.strip().split('\t')

	new_conf = (float(items[6])-min_conf)/width
	if new_conf < 0 or new_conf > 1: print "error", new_conf, width, min_conf, max_conf, items[6]
	items[6] = str(new_conf)
	
	print >> fout, '\t'.join(items)





