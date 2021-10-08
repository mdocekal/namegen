#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""""
Created on 08.10.21
Creates min datasets from deriv_classes.tsv.

Arguments:
    1. path to the deriv_classes.tsv
    2. path to folder where results will be saved into files with names in format: min_[LANGUAGE]_[GRAMMAR].tsv:
        Example:
            min_cs_grammar_female.tsv
:author:     Martin Dočekal
"""
import sys
from pathlib import Path

import pandas

df = pandas.read_csv(sys.argv[1], sep="\t")

for lng in df["language"].unique():
    lng_df = df[df["language"] == lng]
    for gram_t in lng_df["grammar type"].unique():
        representatives = lng_df[lng_df["grammar type"] == gram_t]["class representative"]
        with open(Path(sys.argv[2]).joinpath("min_"+lng+"_"+Path(gram_t).stem+".tsv"), "w") as f:
            for r in representatives:
                print(r, file=f)
