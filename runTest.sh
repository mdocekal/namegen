#!/bin/bash
#Spuštění experimentů pro testování namegenu.

mkdir testRes/test/error_words

./namegen.py -o testRes/test/res.txt testData/test -in -ew testRes/test/error_words/error_words.lntrf -gn testRes/test/given_names.lntrf -sn testRes/test/surnames.lntrf -l testRes/test/locations.lntrf 2> testRes/test/log.txt


cd testRes/test/error_words/
grep -P "\tjG" error_words.lntrf > error_given_names.lntrf
grep -P "\tjL" error_words.lntrf > error_locations.lntrf
grep -P "\tjS" error_words.lntrf > error_surnames.lntrf

