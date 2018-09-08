"""
Created on 5. 6. 2018

Tento modul obsahuje třídu (wrapper nad Morphoditou) pro získávání informací (mluvnických kategorií) o slovech.

[1]    Poziční formát tagu    -    http://ufal.mff.cuni.cz/pdt2.0/doc/manuals/en/m-layer/html/ch02s02s01.html

:author:     Martin Dočekal
:contact:    xdocek09@stud.fit.vubtr.cz
"""

from ufal.morphodita import *



class MorphoditaException(Exception):
    """
    Reprezentuje chybu při získávání informací o slově.
    """
    pass

class Morphodita(object):
    """
    Třída pro získání informací o slovech. Slovní druh rod...
    Jedná se o obálku pro nástroj MorphoDiTa.
    
    [1]    Poziční formát tagu    -    http://ufal.mff.cuni.cz/pdt2.0/doc/manuals/en/m-layer/html/ch02s02s01.html
    
    Značky slovních druhů:
        N - 1
        A - 2
        P - 3
        C - 4
        V - 5
        D - 6
        R - 7
        J - 8
        T - 9
        I - 10
        Z - Symboly
        X - Neznámé
        -   UNKNOWN
    """
    __POSLNTRFTranslator={
        "N": "1",
        "A": "2",
        "P": "3",
        "C": "4",
        "V": "5",
        "D": "6",
        "R": "7",
        "J": "8",
        "T": "9",
        "I": "10",
        "Z": ".",
        "X": ".",
        "-": "."
        }
    
    """
    F     Feminine
    H     {F, N} - Feminine or Neuter
    I     Masculine inanimate
    M     Masculine animate
    N     Neuter
    Q     Feminine (with singular only) or Neuter (with plural only); used only with participles and nominal forms of adjectives
    T     Masculine inanimate or Feminine (plural only); used only with participles and nominal forms of adjectives
    X     Any
    Y     {M, I} - Masculine (either animate or inanimate)
    Z     {M, I, N} - Not fenimine (i.e., Masculine animate/inanimate or Neuter); only for (some) pronoun forms and certain numerals
    -    UNKNOWN
    """
    __GenderLNTRFTranslator={
        "F": "F",
        "H": ".",
        "I": "I",
        "M": "M",
        "N": "N",
        "Q": ".",
        "T": ".",
        "X": ".",
        "Y": ".",
        "Z": ".",
        "-": "."
        }
    
    """
    D     Dual , e.g. nohama
    P     Plural, e.g. nohami
    S     Singular, e.g. noha
    W     Singular for feminine gender, plural with neuter; can only appear in participle or nominal adjective form with gender value Q
    X     Any
    -    UNKNOWN
    """
    __NumberLNTRFTranslator={
        "D": "D",
        "P": "P",
        "S": "S",
        "W": ".",
        "X": ".",
        "-": "."
        }

    """
    1-7    CASE
    X    ANY
    -    UNKNOWN
    """
    __CaseLNTRFTranslator={
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "X": ".",
        "-": "."
        }
    


    """
    Morfologické kategorie v pořadí odpovídajícím pozičnímu formátu [1]_:
        1     POS     Part of speech
        2     SubPOS     Detailed part of speech
        3     Gender     Gender
        4     Number     Number
        5     Case     Case
        6     PossGender     Possessor's gender
        7     PossNumber     Possessor's number
        8     Person     Person
        9     Tense     Tense
        10     Grade     Degree of comparison
        11     Negation     Negation
        12     Voice     Voice
        13     Reserve1     Reserve
        14     Reserve2     Reserve
        15     Var     Variant, style
        """
    morphCategories=["pos", "spos", "g", "n", "c", "pg", "pn", "p", "t", "d", "e", "vo", "re1", "re2", "va"]
    
    def __init__(self, taggerPath, dictPath):
        """
        Konstrukce objektu.
        
        :param taggerPath: Cesta k souboru pro tagger.
        :type taggerPath: String
        :param dictPath: Casta k dictionary pro morphoditu.
        :type dictPath: String
        :raises Morphodita: Když není definovaný tokenizer pro dodaný model. Nebo nevalidní slovník.
        """
        
        self._morpho = Morpho.load(dictPath)
        if self._morpho is None:
            raise MorphoditaException("Chybná dictionary pro morphoditu.")
        
        self.tagger = Tagger.load(taggerPath)
        if self.tagger is None:
            raise MorphoditaException("Chybný tagger.")
        self.tokenizer = self.tagger.newTokenizer()
        if self.tokenizer is None:
            raise MorphoditaException("Není definovaný tokenizer pro dodaný model.")
        
        self.forms = Forms()
        self.tokens = TokenRanges()
        self.lemmas = TaggedLemmas()
        self.converter=TagsetConverter.newPdtToConll2009Converter()
        
    def lemmatize(self, word):
        """
        Vrátí lemma daného slova.
        
        :param word: Slovo pro lemmatizaci.
        :type word: String
        """
        self.tokenizer.setText(word)
        while self.tokenizer.nextSentence(self.forms, self.tokens):
            self.tagger.tag(self.forms, self.lemmas)
            self.converter.convert(self.lemmas[0])
            return self.lemmas[0].lemma

        return None
        
    def genMorphs(self, lemma, tagWildcard=None):
        """
        Vygeneruje tvary pro dané lemma.
        
        :param lemma: Lemma pro generování
        :type lemma: String
        :param tagWildcard: Maska pro filtrování tvarů.
        :type tagWildcard: String
        :return: Tvary daného lemmatu ve dvojici s informací o slově. 
        :rtype: list dvojic
        """
        
        lemmasForms = TaggedLemmasForms()
        self._morpho.generate(lemma, tagWildcard, self._morpho.GUESSER, lemmasForms)
        morphs=[]
        for lemma_forms in lemmasForms:
            for form in lemma_forms.forms:
                morphs.append((form.form, self.tagToWordInfo(form.tag)))

        return morphs
    
    def analyze(self, word):
        """
        Provede analýzu daného slova.
        
        :param word: Slovo pro analýzu.
        :type word: str
        :return info: Informace o slově.
        :rtype info: list of dict
        """
        
        self._morpho.analyze(word, self._morpho.GUESSER, self.lemmas)
        
        info=[]
        for x in self.lemmas:
            info.append(self.tagToWordInfo(x.tag))
                
        return info
        

    def infoToPosFormat(self, info):
        """
        Převede info formát(z getWordInfo) do pozičního formátu z Morphodity [1]_.
        
        :param info: Informace o slově.
        :type info: dict
        """
        newInfo=""
        
        for mC in self.morphCategories:
            if mC in info:
                newInfo+=info[mC]
            else:
                #nepoužíváme
                newInfo+="?"
        
        return newInfo.replace("-", "?")   #- neznámé na libovolné
        
    @classmethod
    def tagToWordInfo(cls, tag):
        """
        Převede tag do dict s informacemi o slově.
        
        :param tag: Tag z morphodity.
        :type tag: String
        """
        
        #Poziční formát tagu je popsán v [1]_
        info={}
        
        #slovní druh
        if tag[0] not in cls.__POSLNTRFTranslator:
            #nerozeznal
            return info
        
        for i, mC in enumerate(cls.morphCategories):
            info[mC]=tag[i]

        return info
    
    @classmethod
    def wordInfoToWildcard(cls, info):
        """
        Převede info do wildcard pro použití v genMorphs.
        Chybějící položky v info budou označeny ve wildcard jako volitelné: ?.
        
        :param info: Informace o slově (získatelné z tagToWordInfo).
        :type info: dict
        :return: wildcard
        :rtype: string
        """
        
        wildcard=""
        for mC in cls.morphCategories:
            if mC in info:
                wildcard+=info[mC]
            else:
                #libovolně
                wildcard+="?"
        
        return wildcard
    
    def getWordInfo(self, word):
        """
        Získá informací o daném slovu.
        
        :param word: Slovo pro analýzu.
        :returns: dict -- s informacemi o daném slově.
            pos - slovní druh
            g - rod
            n - číslo
            c - pád
            e - negace
            d - stupeň
            p - osoba
        """
        
        self.tokenizer.setText(word)
        while self.tokenizer.nextSentence(self.forms, self.tokens):
            self.tagger.tag(self.forms, self.lemmas)
            return self.tagToWordInfo(self.lemmas[0].tag)
        
        return {}
    
    def getMultipleWordsLemmaAndInfo(self, words):
        """
        Použije tagger na daná slova a vratí lemmata společně s infem.
        
        :param words: Slova pro analýzu.
        :type words: str
        :returns: list((lemma, dict)) -- list s lemmatem a informacemi o daném slově.
            pos - slovní druh
            g - rod
            n - číslo
            c - pád
            e - negace
            d - stupeň
            p - osoba
        """
    
        self.tokenizer.setText(words)
        lemmInfo=[]
        while self.tokenizer.nextSentence(self.forms, self.tokens):
            self.tagger.tag(self.forms, self.lemmas)
            for lemm in self.lemmas:
                info=self.tagToWordInfo(lemm.tag)
                self.converter.convert(lemm)
                lemmInfo.append((lemm.lemma,info))
        
        return lemmInfo
    
    def lemmaAndInfo(self, word):
        """
        Použije tagger na dané slovo a vratí lemma společně s infem.
        
        :param word: Slovo pro analýzu.
        :type word: str
        :returns: dvojici s lemmatem a info(getWordInfo formát)
        """
        
        
        self.tokenizer.setText(word)
        while self.tokenizer.nextSentence(self.forms, self.tokens):
            self.tagger.tag(self.forms, self.lemmas)
            info=self.tagToWordInfo(self.lemmas[0].tag)
            self.converter.convert(self.lemmas[0])
            return (self.lemmas[0].lemma, info)
        
    
    @classmethod
    def transInfoToLNTRF(cls, info):
        """
        Převod informací (z getWordInfo) do formátu lntrf.
        
        :param info: Informace o slově z getWordInfo.
        :type info: dict
        """
        infoLNTRF=""
        if "pos" in info:
            infoLNTRF+="k"+cls.__POSLNTRFTranslator[info["pos"]]
            gender=cls.__GenderLNTRFTranslator[info["g"]]
            number=cls.__NumberLNTRFTranslator[info["n"]]
            case=cls.__CaseLNTRFTranslator[info["c"]]
            
            if info["pos"]=="N":
                #podstané jméno zjistím rod, číslo, pád
                infoLNTRF+="g"+gender+"n"+number+"c"+case
            elif info["pos"]=="A":
                #přídavné jméno zjistím negaci,rod, číslo, pád, stupeň
                infoLNTRF+="e"+info["e"]+"g"+gender+"n"+number+"c"+case+"d"+info["d"]
            elif info["pos"]=="P":
                #zájméno zjistime rod, číslo, pád
                infoLNTRF+="g"+gender+"n"+number+"c"+case
            elif info["pos"]=="C":
                #číslovka rod, číslo, pád
                infoLNTRF+="g"+gender+"n"+number+"c"+case
            elif info["pos"]=="V":
                #sloveso negace, osoba, číslo
                infoLNTRF+="e"+info["e"]+"p"+info["p"]+"n"+number
            elif info["pos"]=="D":
                #příslovce negace stupeň
                infoLNTRF+="e"+info["e"]+"d"+info["d"]
            elif info["pos"]=="R":
                #předložka pád
                infoLNTRF+="c"+case
        
        return infoLNTRF.replace("-", ".")   #- neznámé na libovolné
        
    
    def getWordInfoLntrf(self, word):
        """
        Získá informace o daném slovu ve formátu vhodném v lntrf.
        
        :param word: Slovo pro analýzu.
        :returns: String -- s informacemi o daném slově.
        """

        return self.transInfoToLNTRF(self.getWordInfo(word))
