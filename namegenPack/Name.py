"""
Created on 17. 6. 2018
Modul se třídami pro reprezentaci jména/názvu.

:author:     Martin Dočekal
:contact:    xdocek09@stud.fit.vubtr.cz
"""

from enum import Enum
import sys

from namegenPack import Errors
from .morpho.Morphodita import Morphodita
from namegenPack import Grammar
import logging
from namegenPack.morpho.MorphoAnalyzer import MorphoAnalyze, MorphoAnalyzer
from namegenPack.morpho import MorphCategories
from typing import List
from namegenPack.morpho.MorphCategories import StylisticFlag, Case
from namegenPack.Grammar import Terminal


class WordTypeMark(Enum):
    """
    Značka druhu slova ve jméně.
    """
    GIVEN_NAME="G"                  #Křestní jméno. Příklad: Petra
    SURNAME="S"                     #Příjmení. Příklad: Novák
    LOCATION="L"                    #Lokace. Příklad: Brno
    ROMAN_NUMBER="R"                #Římská číslice. Příklad: IV
    PREPOSITION="7"                 #Předložka.
    DEGREE_TITLE="T"                #Titul. Příklad: prof.
    INITIAL_ABBREVIATION="I"        #Iniciálová zkratka. Příklad H. ve jméně John H. White
    UNKNOWN="U"                     #Neznámé

    def __str__(self):
        return self.value
    

class Word(object):
    """
    Reprezentace slova.
    """
    
    class WordException(Errors.ExceptionMessageCode):
        """
        Vyjímka se zprávou a kódem a slovem, který ji vyvolal.
        """
        def __init__(self, word, code, message=None):
            """
            Konstruktor pro vyjímku se zprávou a kódem.
            
            :param word: Pro toto slovo se generuje tato vyjímka
            :type word: Word
            :param code: Kód chyby. Pokud je uveden pouze kód, pak se zpráva automaticky na základě něj doplní.
            :param message: zpráva popisující chybu
            """
            self.word=word
            
            super().__init__(code, message)
    
    class WordCouldntGetInfoException(WordException):
        """
        Vyjímka symbolizující, že se nepovedlo získat mluvnické kategorie ke slovu.
        """
        pass
    
    class WordNoMorphsException(WordException):
        """
        Vyjímka symbolizující, že se nepovedlo získat ani jeden tvar slova.
        """
        pass
    
    class WordMissingCaseException(WordException):
        """
        Vyjímka symbolizující, že se nepovedlo získat některý pád.
        """
        pass
    
    ma=None
    
    def __init__(self, w):
        """
        Kontruktor slova.
        
        :param w: Řetězcová reprezentace slova.
        :type w: String
        """
        self._w=w
        
    @classmethod
    def setMorphoAnalyzer(cls, ma:MorphoAnalyzer):
        """
        Přiřazení morfologického analyzátoru.
        
        :param ma: Morfologický analyzátor, který se bude používat k získávání informací o slově.
        :type ma: MorphoAnalyzer
        """
        
        cls.ma=ma
        
    
    @property
    def info(self) -> MorphoAnalyze:
        """
        Vrací informace o slově. V podobě morfologické analýzy.
        
        :returns: Morfologická analýza slova.
        :rtype: MorphoAnalyze
        :raise WordCouldntGetInfoException: Problém při analýze slova.
        """
        if self.ma is None:
            #nemohu provést morfologickou analýzu bez analyzátoru
            raise self.WordCouldntGetInfoException(self, Errors.ErrorMessenger.CODE_WORD_ANALYZE,
                                                       Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_WORD_ANALYZE)+"\t"+self._w)
        
        #získání analýzy
        a=self.ma.analyze(self._w)
        if a is None:
            raise self.WordCouldntGetInfoException(self, Errors.ErrorMessenger.CODE_WORD_ANALYZE,
                                                       Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_WORD_ANALYZE)+"\t"+self._w)
                
        return a
    
    def morphs(self, analyzedToken: Grammar.AnalyzedToken):
        """
        Vygeneruje tvary slova s ohledem na výsledky ze syntaktické analýzy tohoto slova, které
        jsou uložené v analyzedToken.
        
        :param analyzedToken: Token uchovávající výsledky syntaktické analýzy.
        :type analyzedToken: Grammar.AnalyzedToken
        :return: Pokud se nemá ohýbat, tak pouze slovo. Jinak vrací možné tvary i s jejich pravidly.
                Set[Tuple[MARule,str]]    str je tvar
        :rtype: str | Set[Tuple[MARule,str]]
        :raise WordNoMorphsException: pokud se nepodaří získat tvary.
        """
        if analyzedToken.morph:
            #analýza řekla, že se má ohýbat
            #nejprve zjistíme zda-li jsme z analýzy dostali dalši informace o tvarech
            #v podobě filtrú, kterě použijeme pro získáni tvarů
            filters=set(a.value for a in analyzedToken.matchingTerminal.fillteringAttr)
            
            if analyzedToken.matchingTerminal.type.isPOSType():
                #pro práci s morfologickou analýzou musí byt POS type
                filters.add(analyzedToken.matchingTerminal.type.toPOS)    #vložíme požadovaný tvar do filtru
                
                #pro to abychom vybrali správné tvary, tak se pokusíme získat další filtry na
                #základě morfologické analýzy
                #Například pokud víme, že máme přídavné jméno rodu středního v jednotném čísle
                #a morf. analýza nám řekne, že přídavné jméno je prvního stupně, tak tuto informaci zařadíme
                #k filtrům pro výběr tvarů
                
                for _, morphCategoryValues in self.info.getAll(filters):
                    if len(morphCategoryValues):
                        #daná kategorie má pouze jednu možnou hodnotu použijeme ji jako filtr
                        filters.add(next(iter(morphCategoryValues)))
                
                #na základě filtrů získáme všechny možné tvary
                #nechceme hovorové tvary ->StylisticFlag.COLLOQUIALLY
                
                tmp=self.info.getMorphs(filters, set(StylisticFlag.COLLOQUIALLY))
                if tmp is None or len(tmp)<1:
                    raise self.WordNoMorphsException(self, Errors.ErrorMessenger.CODE_WORD_NO_MORPHS_GENERATED,
                        Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_WORD_NO_MORPHS_GENERATED)+"\t"+self._w)
                return tmp
                

            #pokud neni POS type nemůžeme ohýbat
            
        #neohýbáme, prostě jen vrátíme slovo
        return self._w
    
    def __repr__(self):
        return self._w
    
    def __str__(self):
        return self._w
    
    def __getitem__(self, key):
        return self._w[key]
    
    def __len__(self): 
        return len(self._w)


 
class Name(object):
    """
    Reprezentace celého jména osoby či lokace.
    """

    
    class NameCouldntCreateException(Errors.ExceptionMessageCode):
        """
        Nepodařilo se vytvořit jméno. Deatil ve zprávě
        """
        pass
    
  
    class Type(Enum):
        """
        Přípustné druhy jmen.
        """
        MALE="M"
        FEMALE="F"
        LOCATION="L"
        
        def __str__(self):
            return self.value

    def __init__(self, name, nType):
        """
        Konstruktor jména.
        
        :param name: Řetězec se jménem.
        :type name: String
        :param nType: Druh jména.
        :type nType: Name.Type
        :raise NameCouldntCreateException: Nelze vytvořit jméno.
        """
        self._type=nType
        
        if self._type is not None:
            #typ je určen nemusí se dělat odhad, pouze pokud se jedná o typ určující jméno osoby, tak může být dále případně změněn.
            try:
                #nejprve převedeme a validujeme druh jména
                self._type=self.Type(nType)
            except KeyError:
                raise self.NameCouldntCreateException(Errors.ErrorMessenger.CODE_INVALID_INPUT_FILE_UNKNOWN_NAME_TYPE,
                                                      Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_INVALID_INPUT_FILE_UNKNOWN_NAME_TYPE)+"\n\t"+name+"\t"+nType)
                    
        #rozdělíme jméno na jednotlivá slova a oddělovače
        words, self._separators = self._findWords(name)
        self._words=[Word(w) for w in words]
        
        #zpochybnění typu
        self._guessType()
        
    def __str__(self):
        n=""
        i=0
        for w in self._words:
            n+=str(w)
            if i < len(self._separators):
                n+=self._separators[i]
            i+=1
            
        return n
    
    def __iter__(self):
        for w in self._words:
            yield w
            
    def _guessType(self):
        """
        Provede odhad typu jména. Jedná se o jisté zpochybnění zda-li se jedná o mužské, či ženské jméno.
        Jména lokací nezpochybňujě. 
        Přepíše typ jména pokud si myslí, že je jiný.
        Pokud není typ jména uveden odhadne jej, ovšem pevně předpokládá, že se jedná o jméno osoby.
        Dle zadání má být automaticky předpokládána osoba, kde se může stát, že typ není uveden
        """
        if self._type==self.Type.LOCATION:
            #lokace -> ponecháváme
            return
        try:
            tokens=Grammar.Lex.getTokens(self)

            #zkusíme zpochybnit typ jména
            changeTo=None
            #najdeme první podstatné nebo přídavné jméno od konce (příjmení)
            #Příjmení jak se zdá může být i přídavné jméno (`Internetová jazyková příručka <http://prirucka.ujc.cas.cz/?id=320#nadpis3>`_.)
            
            for token in reversed(tokens):
                if token.type==Grammar.Token.Type.ANALYZE:
                    #získáme možné mluvnické kategorie
                    analyze=token.type.info()
                    posCat=analyze.getAllForCategory(MorphCategories.POS)
                    if MorphCategories.POS.NOUN in posCat or MorphCategories.POS.ADJECTIVE in posCat:
                        if token.word[-3:] == "ová":
                            #muž s přijmení končícím na ová, zřejmě není
                            #změníme typ pokud není ženský
                            changeTo=self.Type.FEMALE
                        break
                
            if changeTo is None:
                #příjmení nekončí na ová
                #zjistíme jakého rodu je první podstatné nebo přídavné jméno (křestní jméno)
                for token in tokens:
                    if token.type==Grammar.Token.Type.ANALYZE:
                        #získáme možné mluvnické kategorie
                        analyze=token.type.info()
                        posCat=analyze.getAllForCategory(MorphCategories.POS)
                        
                        if MorphCategories.POS.NOUN in posCat or MorphCategories.POS.ADJECTIVE in posCat:
                            #získáme možné rody
                            posGenders=analyze.getAllForCategory(MorphCategories.Gender)
                            if MorphCategories.Gender.FEMINE in posGenders and MorphCategories.Gender.MASCULINE_ANIMATE in posGenders and \
                                MorphCategories.Gender.MASCULINE_INANIMATE in posGenders:
                                #bohužel může být jak mužský, tak ženský
                                break
                            
                            if MorphCategories.Gender.FEMINE in posGenders:
                                #asi se jedná o ženské jméno
                                changeTo=self.Type.FEMALE
            
                            elif MorphCategories.Gender.MASCULINE_ANIMATE in posGenders and \
                                MorphCategories.Gender.MASCULINE_INANIMATE in posGenders:
                                #asi se jedná o mužské jméno
                                changeTo=self.Type.MALE
    
                            break
            if changeTo is not None:
                if self._type is None:
                    logging.info("Pro "+str(self)+" přiřazuji "+str(changeTo)+".")
                elif self._type is not changeTo:
                    logging.info("Pro "+str(self)+" měním "+str(self._type)+" na "+str(changeTo)+".")    
                self._type=changeTo
                return #hotovo
                
        except Word.WordCouldntGetInfoException:
            #nepovedlo se získat informace o slově, tak to prostě vynecháme
            return
        
        
            
        
    def markWords(self):
        """
        Provede značení typů slov ve jméně. (Křestní příjmení atd.)
        :raise Word.WordCouldntGetInfoException: Vyjímka symbolizující, že se nepovedlo získat mluvnické kategorie ke slovu.
        """
        
        #TODO: Jedna se jen o docasne reseni
        tokens=Grammar.Lex.getTokens(self)
        
        marks=[]
        
        lastGivenName=None
        for token in tokens:
            if token.type==Grammar.Token.Type.N or token.type==Grammar.Token.Type.A:
                #podstatné nebo přídavné jméno
                if self._type==self.Type.LOCATION:
                    marks.append(WordTypeMark.LOCATION)
                else:
                    marks.append(WordTypeMark.GIVEN_NAME)
                    #uchováváme se poslední pozici křestního jména, jelikož poslední se stane příjmením
                    lastGivenName=len(marks)-1
            elif token.type==Grammar.Token.Type.INITIAL_ABBREVIATION:
                marks.append(WordTypeMark.INITIAL_ABBREVIATION)
            elif token.type==Grammar.Token.Type.ROMAN_NUMBER:
                marks.append(WordTypeMark.ROMAN_NUMBER)
            elif token.type==Grammar.Token.Type.DEGREE_TITLE:
                marks.append(WordTypeMark.DEGREE_TITLE)
            elif token.type==Grammar.Token.Type.R:
                marks.append(WordTypeMark.PREPOSITION)
            else:
                marks.append(WordTypeMark.UNKNOWN)
        
        if lastGivenName is not None and marks.count(WordTypeMark.GIVEN_NAME)>1:   #máme více jak jedno křestní
            #poslední křestní se stane příjmením
            marks[lastGivenName]=WordTypeMark.SURNAME
        
        return marks
        
    @property
    def words(self):
        """
        Slova tvořící jméno.
        @return: Slova ve jméně
        @rtype: list
        """
        
        return self._words  
    
    @property
    def separators(self):
        """
        Oddělovače ve jméně.
        @return: Oddělovače ve jméně
        @rtype: list
        """
        
        return self._separators
    
    @staticmethod
    def _findWords(name):
        """
        Získání slov a oddělovačů v daném slově.
        
        :param name: Daný název.
        :type name: String
        :return: Dvojici se slovy a oddělovači.
        """
        
        words=[]
        separators=[]
        
        actWord=""
        actSeparator=""
        
        #Procházíme jméno a hledáme slova s jejich oddělovači.
        #Vynacháváme oddělovače na konci a začátku.
        for c in name:
            if (c.isspace() or c=='-'):
                #separátor
                
                if len(actWord)>0:
                    #počáteční vynecháváme
                    actSeparator+=c
            else:
                #znak slova
                if len(actSeparator)>0:
                    #již se má načítat další slovo
                    #uložíme to staré a příslušný separátor
                    words.append(actWord)
                    actWord=""
                    
                    separators.append(actSeparator)
                    actSeparator=""
                    
                actWord+=c
            
                
        if len(actWord)>0:
            words.append(actWord)
        
        return (words, separators)
    
    def genMorphs(self, analyzedTokens:List(Grammar.AnalyzedToken)):
        """
        Na základě odpovídajících analyzovaných tokenů slovům ve jméně vygeneruje tvary jména.
        
        :param analyzedTokens: Analyzované tokeny, získané ze syntaktické analýzy tohoto jména.
        :type analyzedTokens: List(Grammar.AnalyzedToken)
        :return:  Vygenerované tvary.
        :rtype: list(str)
        :raise Word.WordNoMorphsException: Pokud se nepodaří získat tvary u nějakého slova.
        :raise WordCouldntGetInfoException: Vyjímka symbolizující, že se nepovedlo získat mluvnické kategorie ke slovu.
        """
        
        #získáme tvary jednotlivých slov
        genMorphsForWords=[]
        for word, aToken in enumerate(zip(self._words, analyzedTokens)):
            genMorphsForWords.append(word.morphs(aToken))
        
        #z tvarů slov poskládáme tvary jména
        #Set[Tuple[MARule,str]]
        morphs=[]
        

        for c in [Case.NOMINATIVE, Case.GENITIVE, Case.DATIVE, Case.ACCUSATIVE, Case.VOCATIVE, Case.LOCATIVE, Case.INSTRUMENTAL]:#pády
            morph=""
            sepIndex=0
            for i, (word, aToken) in enumerate(zip(self._words, analyzedTokens)):
                if aToken.morph and isinstance(genMorphsForWords[i], set):
                    #ohýbáme
                    notMatch=True
                    for maRule, wordMorph in genMorphsForWords[i]:
                        #najdeme tvar slova pro daný pád
                        #TODO: více tvarů pro daný pád
                        if maRule[MorphCategories.Case]==c:
                            morph+=wordMorph+"["+maRule.lntrf+"]#"+aToken.matchingTerminal.getAttribute(Terminal.Attribute.Type.TYPE)
                            notMatch=False
                            break
                        
                    if notMatch:
                        #nepovedlo se získat některý pád
                        
                        raise Word.WordMissingCaseException(word, Errors.ErrorMessenger.CODE_WORD_MISSING_MORF_FOR_CASE,\
                                    Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_WORD_MISSING_MORF_FOR_CASE)+"\t"+c.value+"\t"+str(word))
                else:
                    #neohýbáme
                    morph+=str(word)+"#"+aToken.matchingTerminal.getAttribute(Terminal.Attribute.Type.TYPE)
                
                #přidání oddělovače slov
                if sepIndex < len(self._separators):
                    morph+=self._separators[sepIndex]
                sepIndex+=1
        
            morphs.append(morph)
            
        return morphs
            
        
    @property
    def type(self):
        """Getter pro druh jména."""
        return self._type
        
class NameReader(object):
    """
    Třída pro čtení vstupního souboru a převedení vstupu do posloupnosti objektů Name.

    """
    
    def __init__(self, inputFile):
        """
        Konstruktor 
        
        :param inputFile: Cesta ke vstupnímu souboru se jmény.
        :type inputFile: string

        """
        self.names=[]
        self._errorCnt=0 #počet chybných nenačtených jmen
        with open(inputFile, "r") as rInput:
            for line in rInput:
                line=line.strip()
                parts = line.split("\t")
                if len(parts) != 2:
                    if len(parts) > 2:
                        #nevalidní formát vstupu
                        print(Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_INVALID_NAME)+"\t"+line, file=sys.stderr)
                        self._errorCnt+=1
                        continue
                        
                    #Necháme provést odhad typu slova.
                    #Dle zadání má být automaticky předpokládána osoba, kde se může stát, že typ není uveden.
                    #Řešeno v Name
                    parts.append(None)
                    
                #provedeme analýzu jména a uložíme je 
                try:
                    self.names.append(Name(parts[0], parts[1]))
                except Name.NameCouldntCreateException as e:
                    #problém při vytváření jména
                    print(e.message, file=sys.stderr)
                    self._errorCnt+=1
                
    @property
    def errorCnt(self):
        """
        Počet chybných nenačtených jmen
        """
        return self._errorCnt
        
    def __iter__(self):
        """
        Iterace přes všechna jména.
        """
        
        for name in self.names:
            yield name
            