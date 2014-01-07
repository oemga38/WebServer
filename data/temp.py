#!/usr/bin/env python
import argparse

parser= argparse.ArgumentParser()
parser.add_argument('--o',action='append')
args = parser.parse_args()
print args.o
	
