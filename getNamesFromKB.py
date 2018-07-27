#!/usr/bin/env python3
# encoding: utf-8
"""
Created on 24. 6. 2018
Získávání jmen ze souboru ve formátu popsaném na: https://knot.fit.vutbr.cz/wiki/index.php/Entity_kb_czech3

Očekává jeden arugment s cestou ke vstupnímu souboru.

@author: xdocek09
"""

import sys

if __name__ == '__main__':
    
    getTypes={"geo", "geoplace"}
    
    with open(sys.argv[1], "r") as inpF:
        
        for line in inpF:
            typeWhole, name, *_=line.strip().split("\t")
            typeMain=typeWhole.split(":")[0].lower()
            name=name.strip()
            if typeMain in getTypes and len(name):
                print(name+"\tL")
            
            