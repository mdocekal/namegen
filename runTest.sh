#!/bin/bash
#Spuštění experimentů pro testování namegenu.

mkdir testRes/test/suggestions

./namegen.py -v -w -o testRes/test/res.txt testData/test -in -ew testRes/test/suggestions/suggested_additions.ln_source -gn testRes/test/given_names.lntrf -sn testRes/test/surnames.lntrf -l testRes/test/locations.lntrf 2> testRes/test/log.txt


cd testRes/test/suggestions/
grep -P "\tjG" suggested_additions.ln_source > suggested_additions_given_names.ln_source
grep -P "\tjL" suggested_additions.ln_source > suggested_additions_locations.ln_source
grep -P "\tjS" suggested_additions.ln_source > suggested_additions_surnames.ln_source

