#!/usr/bin/env python
import codecs

if __name__ == "__main__":
	import argparse
	argP = argparse.ArgumentParser(description="split a txt file into N files")
	argP.add_argument('infile', help="input file to split")
	argP.add_argument('n', type=int, help="number of files to be splitted")
	args = argP.parse_args()

	fin = codecs.open(args.infile, encoding='utf8')
	lines = fin.readlines()
	fin.close()
	print len(lines)
	size = len(lines)//args.n
	items = [lines[t:t+size] for t in range(0,len(lines), size)]
	cnt = 0
	for index in range(0, args.n):
		fout = codecs.open(args.infile+'.'+str(index), mode='w', encoding='utf8')
		for item in items[index]: 
			print >> fout, item.strip()
			cnt += 1
		if index == args.n-1: 
			for item in lines[(index+1)*size:]: 
				print >> fout, item.strip()
				cnt += 1
		fout.close()
	
	print cnt	
	
	
