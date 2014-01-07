#!/bin/sh
#echo "ProduceAnnotationUnits.py"
#./ProduceAnnotationUnits.py
#echo "indexChecker-1"
#./indexChecker.py ./breast_cancer/breast_cancer_annotation_units.txt fix --outfile ./breast_cancer/breast_cancer_annotation_units.txt.adjusted
#echo "indexChecker-2"
#./indexChecker.py ./breast_cancer/breast_cancer_annotation_units.txt.adjusted check
#echo "ExtractSentOnly.py"
#./ExtractSentsOnly.py
#cd ~/tools/McClosky/interfaces_heejin
#echo "GenerateTxtForMcClosky.py"
#./GenerateTxtForMcClosky.py ../../../work/WebServer/data/breast_cancer/breast_cancer_sents_only.txt -f ../../../work/WebServer/data/breast_cancer/breast_cancer_sents_only.txt.mcclosky
#cd ~/tools/McClosky
#echo "bioparse.sh"
#./bioparse.sh ~/work/WebServer/data/breast_cancer/breast_cancer_sents_only.txt.mcclosky > ~/work/WebServer/data/breast_cancer/breast_cancer_sents_parsed.con
#cd ~/work/WebServer/data
#echo "EnglishGrammaticalStructure"
#java -cp /home/heejin/tools/StanfordParser/stanford-parser.jar edu.stanford.nlp.trees.EnglishGrammaticalStructure -treeFile ./breast_cancer/breast_cancer_sents_parsed.con -CCprocessed > ./breast_cancer/breast_cancer_sents_parsed.dep
cd ~/work/Event_Disease/src
echo "Experiment.py PT"
#./Experiment.py --classify --txt ../../WebServer/data/breast_cancer/breast_cancer_annotation_units.txt.adjusted --con ../../WebServer/data/breast_cancer/breast_cancer_sents_parsed.con --dep ../../WebServer/data/breast_cancer/breast_cancer_sents_parsed.dep -c PT --output ../../WebServer/data/breast_cancer/breast_cancer_PT_classifications.txt --cancer_type breast -p ../../WebServer/src/nltk_maxent_PT.pkl
./Experiment.py --classify --txt ../../WebServer/data/breast_cancer/breast_cancer_annotation_units.txt.adjusted --con ../../WebServer/data/breast_cancer/breast_cancer_sents_parsed.con --dep ../../WebServer/data/breast_cancer/breast_cancer_sents_parsed.dep -c CCS --output ../../WebServer/data/breast_cancer/breast_cancer_CCS_classifications.txt --cancer_type breast -p ../../WebServer/src/nltk_maxent_CCS.pkl
