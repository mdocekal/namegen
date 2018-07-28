"""
Created on 28. 7. 2018

Tento modul obsahuje výčet morfologických kategorií a jejich hodnot.
Také obsahuje metody pro převod mezi formáty (lntrf).

@author: windionleaf
"""

from enum import Enum
from abc import ABC, abstractmethod, abstractclassmethod, abstractproperty,\
    abstractstaticmethod
from os.path import stat


class MorphoCategoriesUnknownLntrf():
    pass

class MorphCategories(Enum):
    """
    Morfologické kategorie.
    """
    POS=0
    """slovní druh"""
    
    GENDER=1
    """rod"""
    
    NUMBER=2
    """číslo"""
    
    CASE=3
    """pád"""
    
    NEGATION=4
    """negace"""
    
    DEGREE_OF_COMPARISON=5
    """stupeň"""
    
    PERSON=6
    """osoba"""
    
    @classmethod
    def _mappingLntrf(cls):
        """
        Mapování pro lntrf konverzi.
        """
        return{
            cls.POS:"k",
            cls.GENDER:"g",
            cls.NUMBER:"n",
            cls.CASE:"c",
            cls.NEGATION:"e",
            cls.DEGREE_OF_COMPARISON:"d",
            cls.PERSON:"p"
            }

    @property
    def lntrf(self):
        """
        V lntrf formátu.
        """
        return self._mappingLntrf()[self]
        
    @classmethod    
    def fromLntrf(cls, val):
        """
        Vytvoří z lntrf formátu.

        :param val: Vstupní hodnota v lntrf formátu.
        :type val: str
        :return: Odpovídající mluvnickou kategorii.
        :rtype: MorphCategories
        """
        
        return {v: k for k, v in cls._mappingLntrf().items()}[val]
        

class MorphCategory(Enum):
    """
    Bázová třída pro morfologickou kategorii.
    """
    

    @classmethod
    def _mappingLntrf(cls):
        """
        Mapování pro konverzi. Dict
        """
        
        #implicitní mapování
        return {e:str(e.value) for e in cls}
    
    @property
    def _category(self):
        """
        Morfologická kategorie.
        Používá se pro metodu lntrf k získání označení kategorie.
        """
        raise NotImplementedError

    def lntrf(self):
        """
        V lntrf formátu i s označením kategorie.
        Příklad:    k1
        """
        return self._category.lntrf+self.lntrfValue
    
    
    def lntrfValue(self):
        """
        V lntrf formátu, pouze hodnota.
        """
        return self._mappingLntrf()[self]
        
    @classmethod    
    def fromLntrf(cls, val):
        """
        Vytvoří z lntrf formátu.
        Použije k převodu reverzní mapování z _mappingLntrf.

        :param val: Vstupní hodnota v lntrf formátu.
        :type val: str
        :return: Odpovídající mluvnickou kategorii.
        :rtype: MorphCategory
        """
        
        return {v: k for k, v in cls._mappingLntrf().items()}[val]
    
class POS(MorphCategory):
    """
    Slovní druhy.
    """
    NOUN=1
    """podstatné jméno"""
    
    ADJECTIVE=2
    """přídavné jméno"""
    
    PRONOUN=3
    """zájméno"""
    
    NUMERAL=4
    """číslovka"""
    
    VERB=5
    """sloveso"""

    ADVERB=6
    """příslovce"""

    PREPOSITION=7
    """předložka"""

    CONJUNCTION=8
    """spojka"""
    
    PARTICLE=9
    """částice"""

    INTERJECTION=10
    """citoslovce"""
    
    @property
    def _category(self):
        return MorphCategories.POS
        
    
class Gender(MorphCategory):
    """
    Rod
    """
    
    MASCULINE_ANIMATE="M"
    """mužský životný"""
    
    MASCULINE_INANIMATE="I"
    """mužský neživotný"""
    
    NEUTER="N"
    """střední"""
    
    FEMINE="F"
    """ženský"""
    
    FAMILY="R"
    """rodina (příjmení) [asi něco navíc v libma?]"""
    
    
    @property
    def _category(self):
        return MorphCategories.GENDER

    
class Number(MorphCategory):
    """
    Číslo
    """
    
    SINGULAR="S"
    """jednotné"""
    
    PLURAL="P"
    """množné"""
    
    DUAL="D"
    """duál"""
    
    R="R"
    """hromadné označení členů rodiny (Novákovi)"""
    
    @property
    def _category(self):
        return MorphCategories.NUMBER

            
class Case(MorphCategory):
    """
    Pád
    """
    
    NOMINATIVE=1
    """1. pád: Nominativ s pádovými otázkami (kdo, co)"""
    
    GENITIVE=2
    """2. pád: Genitiv (koho, čeho)"""
    
    DATIVE=3
    """3. pád: Dativ (komu, čemu)"""
    
    ACCUSATIVE=4
    """4. pád: Akuzativ (koho, co)"""
    
    VOCATIVE=5
    """5. pád: Vokativ (oslovujeme, voláme)"""
    
    LOCATIVE=6
    """6. pád: Lokál (kom, čem)"""
    
    INSTRUMENTAL=7
    """7. pád: Instrumentál (kým, čím)"""
    
    
    @property
    def _category(self):
        return MorphCategories.CASE

    
class Negation(MorphCategory):
    """
    Negace
    """
    
    AFFIRMATIVE="A"
    """afirmace"""
    
    NEGATED="N"
    """negace"""
   
    
    _category=MorphCategories.NEGATION

    
class DegreeOfComparison(MorphCategory):
    """
    Stupeň
    """
    
    POSITIVE=1
    """pozitiv (příklad: velký)"""
    
    COMPARATIVE=2
    """komparativ (příklad: větší)"""
    
    SUPERLATIVE=3
    """superlativ (příklad: největší)"""
   
    
    @property
    def _category(self):
        return MorphCategories.DEGREE_OF_COMPARISON
    
class Person(MorphCategory):
    """
    Osoba
    """
    
    FIRST=1
    """první osoba"""
    
    SECOND=2
    """druhá osoba"""
    
    THIRD=3
    """třetí osoba"""
    
    ANY="X"
    """první nebo druhá nebo třetí"""

    @property
    def _category(self):
        return MorphCategories.PERSON


            