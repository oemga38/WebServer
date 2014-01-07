#!/usr/bin/env python
import nltk
import random
import pickle
import Timer
import time
import codecs
import sys
import threading
import FeatureGenerator
from AnnotationUnit import *



###############
# Experiments #
###############
def instance_filter(aus, classification_method, multiple_cancer_terms, concept):
	"""
	filters and alters annotation units based on the input options

	:param aus: a list of AnnotationUnits
	:type aus: list
	:param classification_method: one of the two strings '2WI_NI' (identifiable vs. nonidentifiable), '2WCN_NC' (cancer->noraml vs. normal->cancer), or None (default)
	:type classification_method: string
	:param multiple_cancer_terms: True if maintain AnnotationUnits with multiple cancer_terms, False if not
	:type multiple_cancer_terms: Boolean 
	:param concept: PT, CCS or GeneClass
	:type concept: string

	:returns: a list of AnnotationUnits after fitering and alterations
	:rtype: list
	"""
	if not multiple_cancer_terms:
		aus = filter(lambda x: len(x.get_cancer_terms()) == 1, aus)
		
	if classification_method == "2WI_NI":
		def c(x):
			if x.get_CCS() == 'cancerTOnormal' or x.get_CCS() == 'normalTOcancer':
				x.set_CCS('identifiable')
			return x

		aus = map(c, aus)

	if classification_method == "2WCN_NC" or concept == "PT":
		aus = filter(lambda x: x.get_CCS() != 'unidentifiable', aus)

	return aus

def fold_divider(n_folds, aus, unique_pmids, dup_pmids_in_one_fold):
	#print 'len(aus): %d' % len(aus)
	# initilizing
	n_lists = []
	for i in range(n_folds):
		n_lists.append([])
	pmids = set(map(lambda x:x.pmid, aus))
	#print 'len pmids: %d' % len(pmids)

	# determine set_size	
	if unique_pmids:
		set_size = int(len(pmids)/n_folds)
	else:
		set_size = int(len(aus)/n_folds)
	#print 'set_size: %d' % set_size

	# divide unique pmids and multiple pmids
	aus_group_by_pmid = [[au for au in aus if au.pmid == x] for x in pmids]
	aus_dup_pmid = filter(lambda x: len(x) > 1, aus_group_by_pmid)
	aus_dup_pmid.sort(key=lambda x: len(x), reverse=True)
	aus_unq_pmid = filter(lambda x: len(x) == 1, aus_group_by_pmid)
	#print 'aus_dup_pmid: %d' % len(aus_dup_pmid)
	#print 'aus_unq_pmid: %d' % len(aus_unq_pmid)
	
	# error checking for set size	
	if set_size < len(aus_dup_pmid[0]):
		print >> sys.stderr, 'data/n_folds (%d) is smaller than the size of largest set of annotation units from the same sentence (%d).\nTry with smaller n_folds value.' % (set_size, len(aus_dup_pmid[0]))
		sys.exit()

	# handle for unique_pmids option: choose one au for each duplicated pmids
	if unique_pmids:
		map(lambda x: random.shuffle(x), aus_dup_pmid)
		aus_unq_pmid.extend(map(lambda x: [x[0]], aus_dup_pmid))
		aus_dup_pmid = []

	# handler for au list of duplicated pmids
	if not unique_pmids:
		if dup_pmids_in_one_fold:
			for dup_aus in aus_dup_pmid:
				index = random.randint(0,n_folds-1)
				init_index = index
				while len(n_lists[index]) + len(dup_aus) > set_size:
					index = (index + 1) % n_folds 
					# error checking for infinite loops
					if index == init_index:
						print >> sys.stderr, 'failed to distribute duplicated pmid annotation units'
						sys.exit()
				n_lists[index].extend(dup_aus)
		else:
			aus_unq_pmid.extend(aus_dup_pmid)

	# flatten and shuffling au list of unique pmids	
	aus_unq_pmid = reduce(lambda x,y: x.extend(y) or x, aus_unq_pmid)
	random.shuffle(aus_unq_pmid)
	
	# distributing aus of unique pmids
	index = 0
	for l in n_lists:
		i = index + set_size - len(l)
		l.extend(aus_unq_pmid[index:i])
		index = i
	l_index = random.randint(0, n_folds-1)
	for au in aus_unq_pmid[index:]:
		n_lists[l_index%n_folds].append(au)
		l_index = l_index + 1

	# test
	for l in n_lists:
		print len(l)

	return n_lists

def performance(labels, results, gold):
	grpairs = [(l, r) for ((fs, l), r) in zip(gold, results)]
	#print grpairs
	correct = [l==r for ((fs, l),r) in zip(gold, results)]
	accuracy = float(sum([l==r for (l, r) in grpairs]))/len(grpairs)
	prs = list()
	for label in labels:
		tp = [l==r and r==label for (l, r) in grpairs]
		try: precision = float(sum(tp))/sum([r==label for (l, r) in grpairs])
		except ZeroDivisionError: precision = 0
		try: recall = float(sum(tp))/sum([l==label for (l, r) in grpairs])
		except ZeroDivisionError: recall = 0
		try: fmeasure = 2*(precision*recall)/(precision+recall)
		except ZeroDivisionError: fmeasure = 0
		prs.append((label, precision, recall, fmeasure))
	return (accuracy, prs)
	
def one_fold_test(index, fss_n_lists, results, classifiers, alg):
	# prepare test and training set
	print >> sys.stderr, 'starting one_fold_test with index %d ...' % index
	test_set, train_set = [], []
	for j in range(len(fss_n_lists)):
		if index == j:
			test_set.extend(fss_n_lists[j])
		else:
			train_set.extend(fss_n_lists[j])
	#print "train: %d, test: %d" % (len(train_set), len(test_set))

	with Timer.Timer() as timer_train:
		classifier = nltk.MaxentClassifier.train(train_set, alg, trace=0, max_iter=1000)
	classifiers[index] = classifier		

	with Timer.Timer() as timer_test:
		#accuracy = nltk.classify.accuracy(classifier, test_set)
		r = classifier.batch_classify([fs for (fs, l) in test_set])
		p = performance(classifier.labels(), r, test_set)
		
	#results[index] = (accuracy, timer_train.elapsed, timer_test.elapsed, p)
	results[index] = (p[0], timer_train.elapsed, timer_test.elapsed, p[1])
	print >> sys.stderr, 'success one_fold_test with index %d ...' % index
	return
 		
		
def n_fold_test(n_folds, xml_file, con_file, dep_file, alg, concept, classification_method, multiple_cancer_terms, unique_pmids, dup_pmids_in_one_fold, classifier_pickle):
	# instance filtering according to the options
	aus = get_annotation_units(xml_file)
	aus = UnifiedReader(aus, con_file, dep_file)
	aus = instance_filter(aus, classification_method, multiple_cancer_terms, concept)

	# divide into n sets
	n_lists = fold_divider(n_folds, aus, unique_pmids, dup_pmids_in_one_fold)

	# convert annotation units into feature sets
	fss_n_lists = map(lambda x: FeatureGenerator.get_featuresets(x, concept), n_lists)
	print fss_n_lists[0][0][1]

	# N-fold cross validation
	results = []
	classifiers = []
	#threads = []
	for i in range(n_folds):
		results.append(0)
		classifiers.append(0)

	start = time.time()
	for i in range(len(fss_n_lists)):
		one_fold_test(i, fss_n_lists, results, classifiers, alg)
		#threads.append(threading.Thread(target=one_fold_test, args=(i, fss_n_lists, results, classifiers, alg)))
		#threads[i].start()
	#for i in range(len(fss_n_lists)):
	#	threads[i].join()
	
	print '#fold\taccuracy\ttrain_time\ttest_time'
	for i in range(len(fss_n_lists)):
		print 'fold_%s\t%s\t%s\t%s'%(i, results[i][0], results[i][1], results[i][2]), results[i][3]

	acc_sum, t_train_sum, t_test_sum = reduce(lambda x, y: (x[0]+y[0],x[1]+y[1],x[2]+y[2]),results)
	print 'average\t%s\t%s\t%s\t' % (float(acc_sum/n_folds), float(t_train_sum/n_folds), float(t_test_sum/n_folds))
	print 'total elapsed time: %d' % (time.time()-start)

	# for excel
	print 'accuracy'
	for i in range(len(fss_n_lists)):
		print results[i][0]
	print float(acc_sum/n_folds)

	classes = list()
	for i in range(len(results[0][3])):
		classes.append(results[0][3][i][0])
	for clas in classes:
		print clas
		print 'precision'
		for i in range(len(fss_n_lists)):
			for numbers in results[i][3]:
				if numbers[0] == clas: print numbers[1]
		print 'recall'
		for i in range(len(fss_n_lists)):
			for numbers in results[i][3]:
				if numbers[0] == clas: print numbers[2]
		print 'f'
		for i in range(len(fss_n_lists)):
			for numbers in results[i][3]:
				if numbers[0] == clas: print numbers[3]
	
	
	pickle_out = open(classifier_pickle, 'wb')
	pickle.dump(classifiers, pickle_out)
	pickle_out.close()

	#classifier.show_most_informative_features(10)
	#classifier.explain(test_set[0][0])
	#return classifier

def test(xml_file="../corpus/gene_cancer_corpus_121017.xml"):
	aus = get_annotation_units(xml_file)
	#au = aus[421]
	#print ' '.join(au.get_words())
	#print au.cancer_terms
	#print au.get_indexes(au175.cancer_terms[1][1]

	return aus	


def train(xml_file, con_file, dep_file, alg, concept, classifier_pickle):
	aus = get_annotation_units(xml_file)
	aus = UnifiedReader(aus, con_file, dep_file)
	aus = instance_filter(aus, None, True, concept)
	fss_n_lists = map(lambda x: FeatureGenerator.get_featuresets(x, concept), [aus])
	print fss_n_lists[0][0][1]
	classifier = nltk.MaxentClassifier.train(fss_n_lists[0], alg, trace=0, max_iter=1000)
	print len(classifier.labels()), classifier.labels
	pickle_out = open(classifier_pickle, 'wb')
	pickle.dump(classifier, pickle_out)
	pickle_out.close()
	
def classify(txt_file, con_file, dep_file, concept, classifier_pickle, output_file):
	#print >> sys.stderr, "1"
	aus = get_annotation_units_from_txt(txt_file)
	aus = UnifiedReader(aus, con_file, dep_file)
	fss_n_lists = map(lambda x: FeatureGenerator.get_featuresets(x, concept), [aus])

	#print >> sys.stderr, "2"
	pickle_in = open(classifier_pickle, 'rb')
	classifier = pickle.load(pickle_in)
	pickle_in.close()
	#labels = classifier.labels()

	#print >> sys.stderr, "3"
	fout = codecs.open(output_file, mode='w', encoding='utf-8')
	for fs, l in fss_n_lists[0]:
		prob_dist = classifier.prob_classify(fs)
		label = prob_dist.max()
		#print >> fout, '\t'.join(['%s\t%f' % (x, prob_dist.prob(x)) for x in labels])
		print >> fout, '%s\t%f' % (label, prob_dist.prob(label))

if __name__ == "__main__":
	import argparse
	import os.path
	classifier_pickle_default_dir = "../classifiers/MaxEnt/"

	arg_parser = argparse.ArgumentParser(description="Cross validation experiment for CCS classification")
	arg_parser.add_argument('-x','--xml', help="input corpus xml file", default="../corpus/CoMAGC.xml")
	arg_parser.add_argument('--con', help="input con file", default="../corpus/sents_parsed.con")
	arg_parser.add_argument('--dep', help="input dep file", default="../corpus/sents_parsed.dep")
	arg_parser.add_argument('-n','--n_folds', help="'n' fold cross validation", default=10, type=int)
	arg_parser.add_argument('-c', '--concept', help="concept to classfy, CCS, PT or GeneClass", default="CCS")
	arg_parser.add_argument('-m','--multiple_cancer', help="use annotation units with multiple cancer terms", default=True, action="store_false")
	arg_parser.add_argument('--classification_scheme', help="choose classification scheme: 1)None, 2)2WI_NI, 3)2WCN_NC", default="1", choices="123")
	arg_parser.add_argument('--unique_pmids', help="unique pmid only", default=False, action="store_true")
	arg_parser.add_argument('--dup_pmids_in_one_fold', help="put duplicated pmids in one set", default=False, action="store_true")
	arg_parser.add_argument('-p','--pickle', help="pickle file for classifiers")
	# for classifier training
	arg_parser.add_argument('-t', '--train', help = "option to train a classifier", default=False, action="store_true")
	# for batch classification
	arg_parser.add_argument('--classify', help="option to classify ", default=False, action="store_true")
	arg_parser.add_argument('--txt', help="input txt file with annotation units")
	arg_parser.add_argument('--output', help="output file for classification results")
	#arg_parser.add_argument('--cancer_type', help="specify cancer type")
	args = arg_parser.parse_args()

	if args.train:
		train(args.xml, args.con, args.dep, 'GIS', args.concept, args.pickle)
		sys.exit()
	if args.classify:
		#classify(args.txt, args.con, args.dep, args.concept, args.pickle, args.output, args.cancer_type)
		classify(args.txt, args.con, args.dep, args.concept, args.pickle, args.output)
		sys.exit()

	# mapping of classification scheme
	cs_dic = {"1":None, "2":"2WI_NI", "3":"2WCN_NC"}	
	args.classification_scheme = cs_dic[args.classification_scheme]

	# pickle file name generation
	classifier_pickle_default_dir = os.path.join(classifier_pickle_default_dir,args.concept)
	args.pickle = os.path.join(classifier_pickle_default_dir, args.pickle+".pickle")

	print args
	#sys.exit()


	#test()
