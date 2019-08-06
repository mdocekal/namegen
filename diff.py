#!/usr/bin/env python3
# encoding: utf-8
"""
Created on 10. 2. 2019
Compares two results of namegen.py and determines if they are the same.

@author: xdocek09
"""
import sys
import re
import os

class Morphs(object):
    def __init__(self, s):
        self.cases=[self.parseCase(c) for c in s.split("|")]
        self._origRepr=s
        self._hash=hash(''.join(sorted(s)))

    def parseCase(self, c):
        words=[]
        for w in re.split("-|–|,|\s|"+u'\u200b',c):
            variants=set()
            for variant in w.split("/"):
                try:
                    wordTagRule, wType=variant.rsplit("#", 1)
                except ValueError:
                    wordTagRule, wType=variant, ""
                match = re.match( r'(.+)\[(.+)\]', wordTagRule, re.MULTILINE)
                if match is None:
                    #probably without tag rule
                    variants.add((wordTagRule,"",wType))
                else:
                    #word, tagRule,type
                    variants.add((match.group(1),match.group(2),wType))
            words.append(variants)

        return words

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return self._origRepr
    def __str__(self):
        return repr(self)

    def __eq__(self, other):

        if isinstance(other, Morphs):
            if len(self.cases)!=len(other.cases):
                return False

            for wordsS,wordsO in zip(self.cases, other.cases):
                if len(wordsS)!=len(wordsO):
                    #their do not have same number of words
                    return False

                for variantsF, variantsO in zip(wordsS,wordsO):
                    #ok, finally we have two sets, that we can compare
                    if variantsF!=variantsO:
                        return False

            return True
        return False

def loadFile(fileName):
    names={}
    with open(fileName, "r") as f:
        for line in f:
            parts=line.split("\t")


            name=parts[0]
            nameType=parts[2]

            if len(parts[3])==0:
                res=(nameType, parts[3])
            else:
                res=(nameType, Morphs(parts[3]), parts[4])

            try:
                names[name].add(res)
            except KeyError:
                names[name]=set([res])

    return names

first=loadFile(sys.argv[1])
firstName=os.path.basename(sys.argv[1])

second=loadFile(sys.argv[2])
secondName=os.path.basename(sys.argv[2])

numberOfDiff=0
numberOfNoMorphs=0

for name in set(first.keys())|set(second.keys()):

    noMorphs=0
    try:
        for v in first[name]:
            if len(v)==2 or len(v[1].cases)==0:
                noMorphs=1
                break
    except KeyError:
        print(name+"\t"+"is not in "+sys.argv[1]+".")
        continue

    try:
        for v in second[name]:
            if len(v)==2 or len(v[1].cases)==0:
                noMorphs= 0 if noMorphs>0 else 2
                break
    except KeyError:
        print(name + "\t" + "is not in " + sys.argv[2] + ".")
        continue

    if noMorphs>0:
        numberOfNoMorphs+=1
        print(name+"\t"+"No morphs in "+[sys.argv[1],sys.argv[2]][noMorphs-1]+".")
    else:
        for fileName, diffX, diffY in [(sys.argv[1],first[name],second[name]),(sys.argv[2],second[name],first[name])]:
            diffVar=diffX - diffY
            if len(diffVar)>0:
                numberOfDiff+=len(diffVar)

                for x in diffVar:
                    print(fileName+"\t"+str(x))

print("Number of no morphs at one and some morphs at other:\t"+str(numberOfNoMorphs))
print("Number of different name variants:\t"+str(numberOfDiff))
