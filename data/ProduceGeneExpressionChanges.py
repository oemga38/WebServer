#!/usr/bin/env python
import MySQLdb as mdb
import sys
import pickle

con = mdb.connect('localhost', 'heejin', 'skscjswo', 'evex')
with con:
	cur = con.cursor()
	cur.execute("select id, pmid from occurrence_event where type = 'positive_regulation' or type = 'negative_regulation'")
	regulation_events = cur.fetchall()
	cur.execute("select id from occurrence_event where type = 'Gene_expression'")
	expression_events = cur.fetchall()
	cur.execute("select * from occurrence_causal_events")
	causal_events = cur.fetchall()

regulation_event_dict = dict(regulation_events)
print regulation_event_dict.items()[0]
expression_event_dict = dict(zip(map(lambda x: x[0], expression_events), [True]*len(expression_events)))
print expression_event_dict.items()[0]

pmidf = open("./ovarian_cancer/ovarian_cancer_pmid.txt")
pmid_dict = dict()
for line in pmidf:
	pmid_dict[int(line.strip())]=True

outf = open("./ovarian_cancer/ovarian_cancer_gene_expression_changes.txt",'w')

new_pmids = set()
for causal_event in causal_events:
	event_id, cause_ggp_id, cause_event_id, theme_ggp_id, theme_event_id = causal_event
	#print causal_event
	flag = False	
	try:	# if event_type is 'Positive_regulation' or 'Negative_regulation'
		pmid = regulation_event_dict[event_id]
		#print pmid
		# if event is from an abstract retrived via 'cancer' term
		if pmid_dict[pmid]:
			#print "hey"
			if theme_ggp_id: # if 'theme' argument is ggp
				#print "wow"
				flag = True
			elif theme_event_id: # if 'theme' argument is ggp
				#print "up?"
				if expression_event_dict[theme_event_id]: flag = True

	except KeyError: pass


	if flag: 
		print >> outf, '\t'.join(map(lambda x: not x and '\N' or str(x), (event_id, theme_ggp_id, theme_event_id, pmid)))
		new_pmids.add(pmid)
outf.close()


pmidf = open("./ovarian_cancer/ovarian_cancer_evex_pmids.txt",'w')
for pmid in new_pmids:
	print >> pmidf, pmid
pmidf.close()
