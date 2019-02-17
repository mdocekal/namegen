#!/bin/bash
#Spuštění experimentů pro testování namegenu.

mkdir testRes/exp/suggestions

./namegen.py -o testRes/exp/res.txt testData/newest_entities_with_typeflags_20181201-1547631899 -in -ew testRes/exp/suggestions/suggested_additions.ln_source -gn testRes/exp/given_names.lntrf -sn testRes/exp/surnames.lntrf -l testRes/exp/locations.lntrf 2> testRes/exp/log.txt


cd testRes/exp/suggestions/
grep -P "\tjG" suggested_additions.ln_source > suggested_additions_given_names.ln_source
grep -P "\tjL" suggested_additions.ln_source > suggested_additions_locations.ln_source
grep -P "\tjS" suggested_additions.ln_source > suggested_additions_surnames.ln_source

