#!/usr/bin/env python
import FeatureGenerator
from AnnotationUnit import *
import re


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


def ARFFPrinter(aus, concept, outFile):
    #fss_n_lists = map(lambda x: FeatureGenerator.get_featuresets(x, concept), [aus])
    featuresets = FeatureGenerator.get_featuresets(aus, concept)

    # calculation for header
    attDict = dict()
    for featureset in featuresets:
        for key, value in featureset[0].items():
            try: attDict[key].add(value)
            except KeyError: attDict[key] = set([value])

    attributes = attDict.keys()

    fout = open(outFile, 'w')
    
    # print header 
    print >> fout, "@relation %s"%concept
    for attribute in attributes: 
        if attribute.startswith('contain-'): dataType = '{True, False}'
        else: dataType = 'string'
        print >> fout, '@attribute "%s" %s'%(re.sub('"','\\"',attribute), dataType)
    if concept is 'CCS': classes = 'unidentifiable normalTOcancer cancerTOnormal'
    elif concpet is 'PT': classes = 'observation causality'
    else: raise ValueError
    print >> fout, '@attribute %s {%s}'%(concept, classes)

    #print data
    print >> fout, "@data"
    for featureset in featuresets:
        dataLine = ""
        for attribute in attributes:
            try: dataLine += '"'+re.sub('"','\\"',unicode(featureset[0][attribute]).encode('ascii','ignore'))+'"'+','
            except KeyError: dataLine += 'False'+','
        dataLine += featureset[1]
        print >> fout, dataLine
        

    fout.close()
    

if __name__ == "__main__":
    import argparse

    arg_parser = argparse.ArgumentParser(description="Cross validation experiment for CCS classification")
    arg_parser.add_argument('-x','--xml', help="input corpus xml file", default="/home/heejin/work/Event_Disease/corpus/CoMAGC.xml.old")
    arg_parser.add_argument('--con', help="input con file", default="/home/heejin/work/Event_Disease/corpus/sents_parsed.con")
    arg_parser.add_argument('--dep', help="input dep file", default="/home/heejin/work/Event_Disease/corpus/sents_parsed.dep")
    arg_parser.add_argument('-c', '--concept', help="concept to classfy, CCS, PT or GeneClass", default="CCS")
    arg_parser.add_argument('-m','--multiple_cancer', help="use annotation units with multiple cancer terms", default=True, action="store_false")
    arg_parser.add_argument('--classification_scheme', help="choose classification scheme: 1)None, 2)2WI_NI, 3)2WCN_NC", default="1", choices="123")
    arg_parser.add_argument('--output', help="output file for classification results")
    args = arg_parser.parse_args()

    # mapping of classification scheme
    cs_dic = {"1":None, "2":"2WI_NI", "3":"2WCN_NC"}    
    args.classification_scheme = cs_dic[args.classification_scheme]

    aus = get_annotation_units(args.xml)
    aus = UnifiedReader(aus, args.con, args.dep)
    aus = instance_filter(aus, args.classification_scheme, args.multiple_cancer, args.concept)
    ARFFPrinter(aus, args.concept, args.output)

