#!/usr/bin/env python
import glob
import os
import MySQLdb

files = glob.glob('./Medline/cTerms/*.diseaseOff')
fpmids = map(lambda x: os.path.split(x)[1].split('.')[0], files)
fpmids = map(lambda x: long(x), fpmids)
print len(fpmids)
print fpmids[0]
print type(fpmids[0])
fpmids = set(fpmids)

con = MySQLdb.connect('localhost','heejin','skscjswo','evex')
with con:
	cur = con.cursor()
	cur.execute('select pmid from occurrence_ggp')
	epmids = cur.fetchall()
epmids = map(lambda x: x[0], epmids)
print epmids[0]
print type(epmids[0])
epmids = set(epmids)
print len(epmids)

unprecessedPmids = fpmids - epmids
print len(unprecessedPmids)
fout = open('pmidsWithCTermNotinEVEX.txt', mode='w')
for pmid in unprecessedPmids: print >> fout, pmid
fout.close()

pmidsInEVEX = fpmids & epmids
print len(pmidsInEVEX)
fout = open('pmidsWithCTerminEVEX.txt', mode='w')
for pmid in pmidsInEVEX: print >> fout, pmid
fout.close()

