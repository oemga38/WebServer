#!/usr/bin/env python
import MySQLdb as mdb
import codecs
import sys


con = mdb.connect('localhost', 'heejin', 'skscjswo', 'evex')
with con:
	cur = con.cursor()
	cur.execute('set names "utf8"')
	cur.execute("select oe.id, oe.type, oe.confidence_min, oet.string, oet.offsetBeg, oet.offsetEnd from occurrence_event_trigger oet, occurrence_event oe where (oe.type = 'Positive_regulation' or oe.type = 'Negative_regulation' or oe.type = 'Gene_expression') and oe.occurrence_event_trigger_id = oet.id")
	event_triggers = cur.fetchall()
	print >> sys.stderr, "event_triggers loaded"
	cur.execute("select id, string, offsetBeg, offsetEnd from occurrence_ggp")
	ggp_strings = cur.fetchall()
	print >> sys.stderr, "genes loaded"
	cur.execute("select oe.id, og.occurrence_ggp_id from occurrence_event oe, occurrence_eventargument_ggp og where oe.type = 'gene_expression' and og.occurrence_event_id = oe.id")
	GE_args = cur.fetchall()
	print >> sys.stderr, "expression arguments loaded"

event_trigger_dict = dict(map(lambda x: (x[0], x[1:]), event_triggers))
print >> sys.stderr, "event_trigger_dict constructed"
ggp_str_dict = dict(map(lambda x: (x[0], x[1:]), ggp_strings))
print >> sys.stderr, "ggp_str_dict constructed"
expression_arg_dict = dict(GE_args)
print >> sys.stderr, "expression_arg_dict constructed"


	
infile = open("./medline_gene_expression_changes.txt")
#PMID, Event_id, Event_type, Event_confidence_min, EventTriggerStr, EventTriggerOffsetBeg, EventTriggerOffsetEnd, Event_id, EventTriggerStr, EventTriggerOffsetBeg, EventTriggerOffsetEnd, Gene_id, GeneStr, GeneOffsetBeg, GeneOffsetEnd
outfile = codecs.open("./medline_gene_expression_change_ranges.txt",'w',encoding='utf-8')
cnt = 0
for line in infile:
	print >> sys.stderr, cnt
	event_id, theme_ggp_id, theme_event_id, pmid = line.strip().split('\t')
	event_type, confidence_min, Estr, EoffBeg, EoffEnd = event_trigger_dict[int(event_id)]
	if not (theme_ggp_id == '\\N'):
		E2str, E2offBeg, E2offEnd = ('\\N', '\\N', '\\N')
		Gstr, GoffBeg, GoffEnd = ggp_str_dict[int(theme_ggp_id)]
	elif not (theme_event_id == '\\N'):
		t, c, E2str, E2offBeg, E2offEnd = event_trigger_dict[int(theme_event_id)]
		theme_ggp_id = expression_arg_dict[int(theme_event_id)]
		Gstr, GoffBeg, GoffEnd = ggp_str_dict[int(theme_ggp_id)]

	#Estr = Estr.decode('latin-1').encode('utf-8')	
	#E2str = E2str.decode('latin-1').encode('utf-8')	
	#Gstr = Gstr.decode('latin-1').encode('utf-8')	
	print >> outfile, '\t'.join(map(lambda x: unicode(x, encoding='utf-8'),(str(pmid), str(event_id), event_type, str(confidence_min), Estr, str(EoffBeg), str(EoffEnd), str(theme_event_id), E2str, str(E2offBeg), str(E2offEnd), str(theme_ggp_id), Gstr, str(GoffBeg), str(GoffEnd))))
	cnt = cnt + 1
outfile.close()
print >> sys.stderr, "out file closed"
sys.exit(0)

