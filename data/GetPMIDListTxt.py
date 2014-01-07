#!/usr/bin/env python
import glob
import os
import re

def process(input_dir, output_file):
	fout = open(output_file, 'w')
	pattern = re.compile('<Id>(\d+)</Id>')
	for file in glob.glob(os.path.join(input_dir, '*.out')):
		for line in open(file):
			p = pattern.search(line)
			if p: print >> fout, p.group(1)


if __name__ == "__main__":
	import argparse
	arg_parser = argparse.ArgumentParser(description="Generate a txt file with pmids")
	arg_parser.add_argument('input_dir', help="directory with pubmed downloaded xml files, *.out")
	arg_parser.add_argument('output_filename', help="output file name")

	args = arg_parser.parse_args()

	process(args.input_dir, args.output_filename)
