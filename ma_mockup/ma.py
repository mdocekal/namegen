#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""""
Created on 08.09.20
Mockup of ma.
:author:     Martin Dočekal
"""
import os
import sys
from typing import Set

DICT_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dictionaries")


def loadSet(pathTo: str) -> Set[str]:
    """
    Loading of str set from the file on givne path. Each item on single line.

    :param pathTo: Path to data file.
    :return: Set[str]
    """

    with open(pathTo, "r") as f:
        return set(x.strip().lower() for x in f)


def main():
    femaleNames = loadSet(os.path.join(DICT_FOLDER, "names_female.txt"))
    maleNames = loadSet(os.path.join(DICT_FOLDER, "names_male.txt"))
    determiners = loadSet(os.path.join(DICT_FOLDER, "determiners.txt"))
    prepositions = loadSet(os.path.join(DICT_FOLDER, "prepositions.txt"))
    conjunctions = loadSet(os.path.join(DICT_FOLDER, "conjunctions.txt"))
    adjectives = loadSet(os.path.join(DICT_FOLDER, "adjectives.txt"))

    for word in sys.stdin:
        word = word.strip()
        wordLower = word.lower()
        if len(word) > 0:
            possibleG = {"M", "F"}
            note = ""

            if (wordLower in femaleNames) or (wordLower in maleNames):

                note = ";jG"

                if (wordLower in femaleNames) != (wordLower in maleNames):  # XOR
                    # 00
                    #   we know nothing about the gender let's put both of them
                    # 01
                    #   the word is male gender
                    # 10
                    #   the word is female gender
                    # 11
                    #   the word is G and M

                    if wordLower in femaleNames:
                        possibleG = {"F"}

                    else:
                        possibleG = {"M"}

            if wordLower in determiners:
                k = "D"
            elif wordLower in prepositions:
                k = "7"
            elif wordLower in conjunctions:
                k = "8"
            elif wordLower in adjectives:
                k = "2"
            else:
                k = "1"

            print("ma>", end="")

            for g in possibleG:
                print(f"<s> {word}")
                print(f"  <l>{word}")
                print(f"  <c>k{k}g{g}c1{note}")
                print(f"  <f>[k{k}g{g}c1{note}] {word}")


if __name__ == "__main__":
    main()
