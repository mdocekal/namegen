#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""""
Created on 08.09.20
Mockup of ma.
:author:     Martin Dočekal
"""
import os
import sys

from morphodita import Morphodita


def main():
    actFolder = os.path.dirname(os.path.realpath(__file__))
    morphodita = Morphodita(os.path.join(actFolder, "english-morphium-wsj-140407.tagger"),
                            os.path.join(actFolder, "english-morphium-140407.dict"))

    for word in sys.stdin:
        word = word.strip()
        if len(word) > 0:
            lemma = morphodita.lemmatize(word)

            print(f"ma><s> {word}")
            print(f"  <l>{lemma}")
            print(f"  <c>k1")
            print(f"  <f>[k1c1] {word}")


if __name__ == "__main__":
    main()
