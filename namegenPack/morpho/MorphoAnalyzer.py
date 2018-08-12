"""
Created on 14. 7. 2018

Tento modul obsahuje třídy pro morfologickou analýzu.

:author:     Martin Dočekal
:contact:    xdocek09@stud.fit.vubtr.cz
"""

from abc import ABC, abstractmethod, abstractclassmethod, abstractproperty
from subprocess import Popen, PIPE
from ..Errors import ExceptionMessageCode, ErrorMessenger
from namegenPack.morpho.MorphCategories import *
    
from typing import Set, Dict, Tuple

class MARule(dict):
    """
    Reprezentace pravidla tvaru z morfologické analýzy.
    Pravidlo reprezentuje mluvnické kategorie, které ma dané slovo.
    """
    
    def lntrf(self):
        """
        Ve formátu lntrf.
        """

        return self[MorphCategories.POS].lntrf+{
            #podstané jméno zjistím rod, číslo, pád
            POS.NOUN: self[MorphCategories.GENDER].lntrf \
                +self[MorphCategories.NUMBER].lntrf \
                +self[MorphCategories.CASE].lntrf, 
            #přídavné jméno zjistím negaci,rod, číslo, pád, stupeň
            POS.ADJECTIVE: self[MorphCategories.NEGATION].lntrf \
                +self[MorphCategories.GENDER].lntrf \
                +self[MorphCategories.NUMBER].lntrf \
                +self[MorphCategories.CASE].lntrf \
                +self[MorphCategories.DEGREE_OF_COMPARISON].lntrf,
            #zájméno zjistime rod, číslo, pád
            POS.PRONOUN: self[MorphCategories.GENDER].lntrf \
                +self[MorphCategories.NUMBER].lntrf \
                +self[MorphCategories.CASE].lntrf, 
            #číslovka rod, číslo, pád
            POS.NUMERAL: self[MorphCategories.GENDER].lntrf \
                +self[MorphCategories.NUMBER].lntrf \
                +self[MorphCategories.CASE].lntrf, 
            #sloveso negace, osoba, číslo
            POS.VERB: self[MorphCategories.NEGATION].lntrf \
                +self[MorphCategories.PERSON].lntrf \
                +self[MorphCategories.NUMBER].lntrf, 
            #příslovce negace stupeň
            POS.ADVERB: self[MorphCategories.NEGATION].lntrf \
                +self[MorphCategories.DEGREE_OF_COMPARISON].lntrf, 
            #předložka pád
            POS.PREPOSITION: self[MorphCategories.CASE].lntrf, 
            #spojka, nic
            POS.CONJUNCTION: "",
            #částice, nic
            POS.PARTICLE: "",
            #citoslovce, nic
            POS.INTERJECTION: "",
            }[self[MorphCategories.POS]]


class MorphoAnalyze(ABC):
    """
    Interface pro výsledky morfologické analýzy slova.
    """
    
    @abstractproperty
    def word(self):
        """
        Slovo pro nějž je tato morfologická analýza.
        """
        pass
    
    @abstractmethod
    def getAll(self, valFilter: Set[MorphCategory] =set()) -> Dict[MorphCategories,Set[MorphCategory]]:
        """
        Vrácení všech možných hodnot mluvnických kategorií.
        
        :param valFilter: (Volitelný) Filtr, který určuje pevně stanovené 
            hodnoty, které musí mít dané pravidlo, aby se bralo v úvahu.
            Tedy není-li v daném pravidle vůbec zmíněná kategorie obsažena, tak pravidlo neprojde přes filtr.
            Příklad: Chci získat všechny rody jakých může nabývat slovo pokud je podstatným jménem.
            Nastavím filtr na: set(POS.NOUN)
        :type valFilter: Set[MorphCategory]
        :return: Hodnoty mluvnických kategorií.
        :rtype: Dict[MorphCategories, Set[MorphCategory]]
        """
        pass
    
    @abstractmethod
    def getAllForCategory(self, morphCategory: MorphCategories, valFilter: Set[MorphCategory] =None) -> Set[MorphCategory]:
        """
        Vrácení všech možných hodnot dané mluvnické kategorie.
        
        :param morphCategory: Mluvnická kategorie.
        :type morphCategory: MorphCategories
        :param valFilter: (Volitelný) Filter, který určuje pevně stanovené 
            hodnoty, které musí mít dané pravidlo, aby se bralo v úvahu.
            Tedy není-li v daném pravidle/rozboru vůbec zminěná kategorie obsažena, tak pravidlo neprojde přes filtr.
            Příklad: Chci získat všechny rody jakých může nabývat slovo pokud je podstatným jménem.
            Nastavím filtr na: set(POS.NOUN)
        :type valFilter: Set[MorphCategory]
        :return: Hodnoty dané mluvnické kategorie.
        :rtype: Set[MorphCategory]
        """
        pass
    
    @abstractmethod
    def getMorphs(self, valFilter: Set[MorphCategory] =set(), notValFilter: Set[MorphCategory] =set())->Set[Tuple[MARule,str]]:
        """
        Získání tvarů.
        
        :param valFilter: (Volitelný) Filtr, který určuje pevně stanovené 
            hodnoty, které musí mít pravidlo tvaru, aby se bral v úvahu daný tvar.
            Tedy není-li v daném pravidle tvaru vůbec zminěná kategorie obsažena, tak tvar neprojde přes filtr.
            Příklad: Chci získat všechny tvary, které jsou podstatným jménem, tak
            nastavím filtr na: set(POS.NOUN)
        :type valFilter: Set[MorphCategory]
        :param notValFilter: Stejné jako valFilter s tím rozdílem, že dané hodnoty nesmí pravidlo tvaru obsahovat.
        :type notValFilter:Set[MorphCategory]
        :return: Množinu dvojic (pravidlo, tvar).
        :rtype: Set[Tuple[MARule,str]]
        """
        pass
    
class MorphoAnalyzer(ABC):
    """
    Interface morfologického analyzátoru.
    """
    
    @abstractmethod
    def analyze(self, word:str) -> MorphoAnalyze:
        """
        Získání morfologické analýzy slova.
        
        :param word: slovo pro analýzu
        :type word: str
        :return: Analýza slova. None při neúspěchu.
        :rtype: MorphoAnalyze 
        """
        pass

    

class MorphoAnalyzerException(ExceptionMessageCode):
    """
    Vyjímka pro problémy s morfologickým analyzátorem
    """
    pass
    
class MorphoAnalyzerLibma(object):
    """
    Obálka pro Morfologický analyzátor postavený na knihovně libma
    .. _ma: http://knot.fit.vutbr.cz/wiki/index.php/Morfologický_slovník_a_morfologický_analyzátor_pro_češtinu
    
    """
    
    class MAWordGroup():
        """
        Třída reprezentující skupinu slov k nějakému slovu.
        Obsahuje lemma a vzor daného slova. Také značko-pravidla pro dané slovo
        a různé tvary společně s jejich značko pravidly.
        
        Libma dělí analýzu slova na více skupin. Tato třída reprezentuje jednu ze skupin.
        Zkrácený příklad pro slovo Velké (skupina začíná <s>):
        ma><s> Velké (Sedláčková_nF)
          <l>Velká
          <c>k1gFnPc1
          <c>k1gFnPc4
          ...
          <f>[k1gFnSc7] Velkou 
          <f>[k1gFnSc4] Velkou 
          <f>[k1gFnSc5] Velká 
          <f>[k1gFnSc1] Velká 
          <f>[k1gFnSc6] Velké 
          <f>[k1gFnSc3] Velké 
          ...
        <s> Velké (Široký_nM)
          <l>Velký
          <c>k1gMnPc4
          <f>[k1gMnPc5] Velcí 
          <f>[k1gMnPc1] Velcí 
          <f>[k1gMnPc4] Velké 
          ...
        <s> Velké (velký)
          <l>velký
          <c>k2eAgFnPc1d1
          <c>k2eAgFnPc4d1
          <c>k2eAgFnPc5d1
          ...
          <f>[k2eNgNnPc4d3wH] nejnevětši 
          ...

        """
        
        def __init__(self, word):
            """
            Vytvoření skupiny pro slovo. 
            
            :param word: Slovo pro nějž je tato skupina vytvořena.
            :type word: str
            """
            
            self._word=word
            self._lemma=None
            self._paradigm=None
            self._tagRules=[]   #značko pravidla pro slovo
            self._morphs=[] #tvary k danému slovu ve formátu dvojic (tagRule, tvar)
            
        def addMorph(self, tagRule, morph):
            """
            Přidání tvaru.
            
            :param tagRule: Značko pravidlo pro tvar (příklad k1gFnSc7)
            :type tagRule: str
            :param morph: Tvar slova.
            :type morph: str
            """
            self._morphs.append((self._convTagRule(tagRule), morph))
            
        def getMorphs(self, valFilter: Set[MorphCategory] =set(), notValFilter: Set[MorphCategory] =set())->Set[Tuple[MARule,str]]:
            """
            Získání tvarů.
            
            :param valFilter: (Volitelný) Filtr, který určuje pevně stanovené 
                hodnoty, které musí mít dané pravidlo tvaro, aby se bral v úvahu daný tvar.
                Tedy není-li v daném pravidle tvaru vůbec zminěná kategorie obsažena, tak tvar neprojde přes filtr.
                Příklad: Chci získat všechny tvary, které jsou podstatným jménem, tak
                nastavím filtr na: set(POS.NOUN)
            :type valFilter: Set[MorphCategory]
            :param notValFilter: Stejné jako valFilter s tím rozdílem, že dané hodnoty nesmí pravidlo tvaru obsahovat.
            :type notValFilter:Set[MorphCategory]
            :return: Množinu dvojic (pravidlo, tvar).
            :rtype: Set[Tuple[MARule,str]]
            """
            
            morphs=set()
            
            for r, m in self._morphs:
                try:
                    if all( r[f.category()]==f.lntrfValue for f in valFilter) \
                        and all( f.category() not in r or r[f.category()]!=f.lntrfValue for f in notValFilter):

                        #úprava velikosti počátečního písmene tvaru na základě původního slova
                        if self._word[0].isupper():
                            newM=m[0].upper()+m[1:]
                        else:
                            newM=m[0].lower()+m[1:]
                        
                        morphs.add((r,newM))
                except KeyError:
                    #neobsahuje danou mluvnickou kategorii
                    pass

            return morphs  
            
        @staticmethod
        def _convTagRule(tagRule):
            """
            Převod značko pravidla ze str do MARule
            
            :param tagRule: Značko pravidlo (příklad k1gFnPc1)
            :type tagRule: str
            :return: Převedené pravidlo z morfologické analýzy.
            :rtype: MARule
            """
            #Příklad převodu: k1gFnPc1
            #    
            #    {"k":"1","g":"F","n":"P","c":"1"}
            
            
            res=MARule
            for i in range(0, len(tagRule)-1, 2):
                mCategory=MorphCategories.fromLntrf(tagRule[i])
                res[mCategory]=mCategory.createCategoryFromLntrf(tagRule[i+1])
                
            return res
            
        def addTagRule(self, tagRule):
            """
            Přidání značko pravidla.
            
            :param tagRule: Značko pravidlo (příklad k1gFnPc1)
            :type tagRule: str
            """
            
            self._tagRules.append(self._convTagRule(tagRule))
            
        def getAll(self, valFilter: Set[MorphCategory] =set()) -> Dict[MorphCategories,Set[MorphCategory]]:
            """
            Vrácení všech možných hodnot mluvnických kategorií.
            
            :param valFilter: (Volitelný) Filtr, který určuje pevně stanovené 
                hodnoty, které musí mít dané pravidlo, aby se bralo v úvahu.
                Tedy není-li v daném pravidle vůbec zmíněná kategorie obsažena, tak pravidlo neprojde přes filtr.
                Příklad: Chci získat všechny rody jakých může nabývat slovo pokud je podstatným jménem.
                Nastavím filtr na: set(POS.NOUN)
            :type valFilter: Set[MorphCategory]
            :return: Hodnoty mluvnických kategorií.
            :rtype: Dict[MorphCategories, Set[MorphCategory]]
            """
            values={}
            
            for r in self._tagRules:
                try:
                    if all( r[f.category()]==f for f in valFilter):
                        for morphCat, morphCatVal in r:
                            try:
                                values[morphCat].add(morphCatVal)
                            except KeyError:
                                #první vložení hodnoty dané kategorie
                                values[morphCat]=set(morphCatVal)
                                
                except KeyError:
                    #neobsahuje danou mluvnickou kategorii
                    pass

            return values  
        
        def getAllForCategory(self, morphCategory: MorphCategories, valFilter: Set[MorphCategory] =set()) -> Set[MorphCategory]:
            """
            Vrácení všech možných hodnot mluvnické kategorie.
            
            :param morphCategory: Mluvnická kategorie.
            :type morphCategory: MorphCategories
            :param valFilter: (Volitelný) Filtr, který určuje pevně stanovené 
                hodnoty, které musí mít dané pravidlo, aby se bralo v úvahu.
                Tedy není-li v daném pravidle vůbec zminěná kategorie obsažena, tak pravidlo neprojde přes filtr.
                Příklad: Chci získat všechny rody jakých může nabývat slovo pokud je podstatným jménem.
                Nastavím filtr na: set(POS.NOUN)
            :type valFilter: Set[MorphCategory]
            :return: Hodnoty dané mluvnické kategorie.
            :rtype: Set[MorphCategory]
            """
            
            values=set()
            
            for r in self._tagRules:
                try:
                    if all( r[f.category()]==f for f in valFilter):
                        values.add(r[morphCategory])
                except KeyError:
                    #neobsahuje danou mluvnickou kategorii
                    pass

            return values  
            
        @property
        def word(self):
            """
            Slovo pro nějž je tato skupina vytvořena.
            """
            return self._word

        @word.setter
        def word(self, value):
            """
            Nastavení slova pro nějž je tato skupina vytvořena.
            
            :param value: Slovo pro nějž je tato skupina vytvořena.
            :type value: str
            """
            self._word = value
                
        @property
        def lemma(self):
            """
            Lemma slova.
            """
            return self._lemma

        @lemma.setter
        def lemma(self, value):
            """
            Nastavení nového lemma slova.
            
            :param value: Lemma slova.
            :type value: str
            """
            self._lemma = value
            
        @property
        def paradigm(self):
            """
            Vzor slova.
            """
            return self._paradigm

        @paradigm.setter
        def paradigm(self, value):
            """
            Nastavení nového vzoru slova.
            
            :param value: Vzor slova.
            :type value: str
            """
            self._paradigm = value
            
        def __str__(self):
            s="Lemma: "+self._lemma+"\n"
            s+="Paradigm: "+self._paradigm+"\n"
            
            s+="Tag rules:\n"
            for tr in self._tagRules:
                s+="\t"+str(tr)+"\n"
            
            s+="Morphs:\n"
            for m in self._morphs:
                s+="\t"+str(m)+"\n"
                
            return s
                
                
    class MAWord(MorphoAnalyze):
        """
        Obsahuje data z morfologické analýzy slova.
        """
        
        def __init__(self, word):
            """
            Vytvoření instance morfologícké analýzy slova.
            
            :param word: Slovo pro nějž je morfologická analýza vytvořena.
            :type word: str
            """
            self._word=word
            self._groups=[]
            
        
        def addGroup(self, group):
            """
            Přidání skupiny z morfoligické analýzy.
            
            :param group: Skupina z analýzy obsahující vzor, lemma, tvary, značko-pravidla
            :type group: MorphoAnalyzerLibma.MAWordGroup
            """
            self._groups.append(group)
            
        def getAll(self, valFilter: Set[MorphCategory] =set()) -> Dict[MorphCategories,Set[MorphCategory]]:
            """
            Vrácení všech možných hodnot mluvnických kategorií. Ve všech skupinách
            získaných při analýze slova.
            
            :param valFilter: (Volitelný) Filtr, který určuje pevně stanovené 
                hodnoty, které musí mít dané pravidlo, aby se bralo v úvahu.
                Tedy není-li v daném pravidle vůbec zmíněná kategorie obsažena, tak pravidlo neprojde přes filtr.
                Příklad: Chci získat všechny rody jakých může nabývat slovo pokud je podstatným jménem.
                Nastavím filtr na: set(POS.NOUN)
            :type valFilter: Set[MorphCategory]
            :return: Hodnoty mluvnických kategorií.
            :rtype: Dict[MorphCategories, Set[MorphCategory]]
            """
            values={}
            
            for g in self._groups:
                
                for morphCat, morphCatValues in g.getAll(valFilter):
                    try:
                        values[morphCat]=values[morphCat] | morphCatValues
                    except KeyError:
                        #první vložení hodnoty dané kategorie
                        values[morphCat]=morphCatValues

            return values

        
        def getAllForCategory(self, morphCategory: MorphCategories, valFilter: Set[MorphCategory] =set()) -> Set[MorphCategory]:
            """
            Vrácení všech možných hodnot dané mluvnické kategorie. Ve všech skupinách
            získaných při analýze slova.
            
            :param morphCategory: Mluvnická kategorie.
            :type morphCategory: MorphCategories
            :param valFilter: (Volitelný) Filter, který určuje pevně stanovené 
                hodnoty, které musí mít dané pravidlo, aby se bralo v úvahu.
                Tedy není-li v daném pravidle vůbec zminěná kategorie obsažena, tak pravidlo neprojde přes filtr.
                Příklad: Chci získat všechny rody jakých může nabývat slovo pokud je podstatným jménem.
                Nastavím filtr na: set(POS.NOUN)
            :type valFilter: Set[MorphCategory]
            :return: Hodnoty dané mluvnické kategorie.
            :rtype: Set[MorphCategory]
            """
            
            values=set()
            
            for g in self._groups:
                values |= g.getAllForCategory(morphCategory, valFilter)

            return values
        
        def getMorphs(self, valFilter: Set[MorphCategory] =set(), notValFilter: Set[MorphCategory] =set())->Set[Tuple[MARule,str]]:
            """
            Získání tvarů.
            
            :param valFilter: (Volitelný) Filtr, který určuje pevně stanovené 
                hodnoty, které musí mít pravidlo tvaru, aby se bral v úvahu daný tvar.
                Tedy není-li v daném pravidle tvaru vůbec zminěná kategorie obsažena, tak tvar neprojde přes filtr.
                Příklad: Chci získat všechny tvary, které jsou podstatným jménem, tak
                nastavím filtr na: set(POS.NOUN)
            :type valFilter: Set[MorphCategory]
            :param notValFilter: Stejné jako valFilter s tím rozdílem, že dané hodnoty nesmí pravidlo tvaru obsahovat.
            :type notValFilter:Set[MorphCategory]
            :return: Množinu dvojic (pravidlo, tvar).
            :rtype: Set[Tuple[MARule,str]]
            """
            morphs=set()
            
            for g in self._groups:
                morphs |= g.getMorphs(valFilter, notValFilter)
    
            return morphs  
            
        
        @property
        def groups(self):
            """
            Skupiny z morfologické analýzy.
            
            :rtype: List(MAWordGroup)
            """
            
            return self._groups
            
        @property
        def word(self):
            """
            Slovo pro nějž je tato morfologická analýza.
            """
            return self._word
        
        def __str__(self):
            s=self._word+"\n"
            for g in self._groups:
                s+=str(g)
            s+="----------"
            return s
            
    
    def __init__(self, pathToMa, words):
        """
        Provede vytvoření objektu Morfologického analyzátoru.
        Spustí nad všemy slovy z words morfologický analyzátor s parametry:
            -F vrací všechny možné tvary.
            -m Na výstup se vypíše flektivní analýza zadaného slova.
        Výsledek si poté načte a bude sloužit jako databáze, která bude použita pro získávání informací
        o slovech.
        
        :param pathToMa: Cesta/ příkaz pro spuštění morfologického analyzátoru.
        :type pathToMa: str
        :param resultsFilePath: Cesta k souboru, kde bude uložen výsledek z morfologického analyzátoru
        :type resultsFilePath: str
        :param words: Slova, která budou předložena analyzátoru a vysledek budou sloužit jako databáze
            pro tuto obálku. Objekt bude tedy znát nanejvýše tato slova.
        :type words: set(str)
        """
        
        #získání informací o slovech
        
        
        p = Popen([pathToMa, "-F", "-m"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, _ = p.communicate(str.encode(("\n".join(words))+"\n")) #vrací stdout a stderr
        
        #zkontrolujeme návratový kód
        rc = p.returncode
        
        if rc!=0:
            #selhání analyzátoru
            raise MorphoAnalyzerException(ErrorMessenger.CODE_MA_FAILURE)
        
        self._parseMaOutput(output.decode())
        
        
    def _parseMaOutput(self, output):
        """
        Provede analýzu výstupu z ma a uloží získané informace do databáze.
        
        :param output: Výstup z analyzátoru.
        :type output: str
        """
        
        #vytvoříme novou prázdnou databázi slov
        self._wordDatabase={}
        
        actWordGroup=None   #obsahuje data k aktuálně parsované skupině
        
        for line in output.splitlines():
            #rozdělení řádku
            parts=line.strip().split()
            
            if parts[0][-3:]=="<s>":
                #začínáme číst novou skupinu slova
                #<s> vstupní slovo (vzor 1)
                    
                #vytvoříme skupinu
                actWordGroup=self.MAWordGroup(parts[1])
                
                #nastavíme vzor
                actWordGroup.paradigm=parts[2][1:-1]
                
                try:
                    #vložíme skupinu do analýzy slova
                    self._wordDatabase[parts[1]].addGroup(actWordGroup)
                except KeyError:
                    #nové slovo
                    #vytvoříme objekt pro uložení morfologické analýzy slova
                    self._wordDatabase[parts[1]]=self.MAWord(parts[1])
                    #a znovu vložíme
                    self._wordDatabase[parts[1]].addGroup(actWordGroup)
                    
                

            elif parts[0][:3]=="<l>":
                #lemma
                actWordGroup.lemma=parts[0][3:]
                
            elif parts[0][:3]=="<c>":
                #značko pravidlo, které sedí pro dané slovo
                actWordGroup.addTagRule(parts[0][3:])
                
            elif parts[0][:3]=="<f>":
                #Přidání tvaru slova
                actWordGroup.addMorph((parts[0][3:])[1:-1], parts[1])
                
            
    def analyze(self, word):
        """
        Získání kompletních znalostí o slově. Slovo by mělo být 
        jedním ze slov předaných v konstruktoru.
        
        :param word:
        :type word:
        :return: Analýza slova. None pokud není slovo v databázi.
        :rtype: MAWord 
        """
        
        if word not in self._wordDatabase:
            return None
        
        return self._wordDatabase[word]

        
        
        
        
    