# -*- coding: UTF-8 -*-
""""
Created on 04.09.20
Modul pro práci s jazykem.

:author:     Martin Dočekal
"""
import os
from typing import Optional, Set

from namegenPack.Grammar import Grammar, Lex


class Language(object):
    """
    Načítá struktury pro práci s daným jazykem.

    :ivar code: kód jazyka (cs)
    :vartype code: str
    :ivar gTimeout: timeout pro gramatiky
    :vartype gTimeout: int
    :ivar gFemale: gramatika pro ženy
    :vartype gFemale: Grammar
    :ivar gMale:  gramatika pro muže
    :vartype gMale: Grammar
    :ivar gLocations: gramatika pro lokace
    :vartype gLocations: Grammar
    :ivar gEvents: gramatika pro události
    :vartype gEvents: Grammar
    :ivar titles: množina titulů
    :vartype titles: Set[str]
    :ivar lex: lexikální analyzátor pro tento jazyk
    :vartype lex: Lex
    """

    def __init__(self, langFolder: str, gFemale: str, gMale: str, gLocations: str, gEvents: str, titles: str,
                 gTimeout: Optional[int]):
        """
        Načte jazyk z jeho složky.

        :param langFolder: Cesta ke složce s jazykem.
        :type langFolder: str
        :param gFemale: Nazev soubor s gramatikou pro ženy.
        :type gFemale: str
        :param gMale: Název souboru s gramatikou pro muže.
        :type gMale: str
        :param gLocations: Název souboru s gramatikou pro lokace.
        :type gLocations: str
        :param gEvents: Název souboru s gramatikou pro události.
        :type gEvents: str
        :param titles: Název souboru s tituly.
        :type titles: str
        :param gTimeout: Timeout pro gramatiky.
        :type gTimeout: Optional[int]
        """

        self.code = os.path.split(langFolder)[-1]
        self.gTimeout = gTimeout

        grammarsPath = os.path.join(langFolder, "grammars")

        self.gFemale = Grammar(os.path.join(grammarsPath, gFemale), gTimeout)
        self.gMale = Grammar(os.path.join(grammarsPath, gMale), gTimeout)
        self.gLocations = Grammar(os.path.join(grammarsPath, gLocations), gTimeout)
        self.gEvents = Grammar(os.path.join(grammarsPath, gEvents), gTimeout)
        self.titles = self._readTitles(os.path.join(langFolder, titles))
        self.lex = Lex(self.titles)

    @staticmethod
    def _readTitles(pathT) -> Set[str]:
        """
        Získá tituly ze souboru s tituly.

        :param pathT: Cesta k souboru
        :type pathT: str
        :return: Množina se všemi tituly.
        :rtype: Set[str]
        """
        titles = set()
        with open(pathT, "r") as titlesF:
            for line in titlesF:
                content = line.split("#", 1)[0].strip()
                if content:
                    for t in content.split():
                        titles.add(t)

        return titles



