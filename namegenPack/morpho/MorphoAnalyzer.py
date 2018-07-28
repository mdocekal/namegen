"""
Created on 14. 7. 2018

Tento modul obsahuje třídy pro morfologickou analýzu.

:author:     Martin Dočekal
:contact:    xdocek09@stud.fit.vubtr.cz
"""

from abc import ABC, abstractmethod, abstractclassmethod
from subprocess import Popen, PIPE
from ..Errors import *
from _dbus_bindings import ErrorMessage
from .MorphCategories import *
from namegenPack.morpho.MorphCategories import MorphCategory
from typing import Set


class MorphoAnalyzer(ABC):
    """
    Abstraktní třída morfologického analyzátoru.
    """
    
    @abstractmethod
    def lemmatize(self, word):
        """
        Vrátí lemma daného slova.
        
        :param word: Slovo pro lemmatizaci.
        :type word: String
        """
        pass
    
    @abstractmethod
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
        pass
    
    D
    def getWordInfo(self, word):
        """
        Získá informaci o daném slovu.
        
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
        pass
    
    @abstractclassmethod
    def transInfoToLNTRF(cls, info):
        """
        Převod informací (z getWordInfo) do formátu lntrf.
        
        :param info: Informace o slově z getWordInfo.
        :type info: dict
        """
        pass
    
    @abstractclassmethod
    def getWordInfoLntrf(self, word):
        """
        Získá informace o daném slovu ve formátu vhodném v lntrf.
        
        :param word: Slovo pro analýzu.
        :returns: String -- s informacemi o daném slově.
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
        
        def __init__(self):
            """
            Vytvoření skupiny pro slovo. 
            """
            
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
            
        @staticmethod
        def _convTagRule(tagRule):
            """
            Převod značko pravidla ze str do dict
            
            :param tagRule: Značko pravidlo (příklad k1gFnPc1)
            :type tagRule: str
            """
            #Příklad převodu: k1gFnPc1
            #    
            #    {"k":"1","g":"F","n":"P","c":"1"}
            
            return {tagRule[i]:tagRule[i+1] for i in range(0, len(tagRule)-1, 2)}
            
        def addTagRule(self, tagRule):
            """
            Přidání značko pravidla.
            
            :param tagRule: Značko pravidlo (příklad k1gFnPc1)
            :type tagRule: str
            """
            
            self._tagRules.append(self._convTagRule(tagRule))
            
        def getAll(self, morphCategory: MorphCategories) -> Set[MorphCategory]:
            """
            Vrácení všech možných hodnot dané mluvnické kategorie.
            
            :param morphCategory: Mluvnická kategorie.
            :type morphCategory: MorphCategories
            """
            
            for r in self._tagRules:
                if M
            
            
            
            
            
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
                
                
    class MAWord():
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
            :type group: MAWordGroup
            """
            self._groups.append(group)
            
        def getAllPOS(self):
            """
            Získání všech slovních druhů, kterých může slovo nabývat.
            """
            
            return {  for g in self._groups }
            
            
            
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
                actWordGroup=self.MAWordGroup()
                
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

    def 
        
        
        
        
        
        
    