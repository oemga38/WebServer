#!/usr/bin/env python
#
# 15.Nov.2012
#	- heejin
#
# class matrix 
# 	- simple matrix manipulation
#


import sys

class matrix():
	def __init__(self, items=[]):
		self.rows = [items]

	def __repr__(self): return repr(self.rows)

	def num_rows(self): return len(rows)
	def num_cols(self): return len(rows[0])

	def add_col(self, items):
		if len(self.rows)!= 0 and len(items) != len(self.rows):
			print >> sys.err, "matrix.add_col(), matrix_rows:%d, items:%d" % (len(self.rows), len(items))
		for i, item in enumerate(items):
			try:
				self.rows[i].append(item)
			except IndexError:
				self.rows.append([item])
				

	def add_row(self, items):
		if len(self.rows)!=0 and len(items) != len(self.rows[0]):
			print >> sys.stderr, "matrix.add_row(), matrix_row:%d, items:%d" % (len(self.rows[0]), len(items))
		self.rows.append(items)

	def get_col(self, i):
		col = []
		for row in self.rows:
			col.append(row[i])

		return col

	def get_row(self, i): return self.rows[i]
		
	def get_cell(self, i, j): return self.rows[i][j]
