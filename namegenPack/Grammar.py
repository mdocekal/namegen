"""
Created on 17. 6. 2018

Modul pro práci s gramatikou.

:author:     Martin Dočekal
:contact:    xdocek09@stud.fit.vubtr.cz
"""
from namegenPack import Errors
import re
from typing import Set
from namegenPack.morpho.MorphCategories import MorphCategory, Gender, Number,\
    MorphCategories, POS, StylisticFlag, Case
from enum import Enum
from builtins import isinstance
from namegenPack.Word import Word, WordTypeMark

class Terminal(object):
    """
    Reprezentace parametrizovaného terminálu.
    """
    
    class Type(Enum):
        """
        Druh terminálu.
        """
        EOF= 0 #konec vstupu
        
        N= "1"    #podstatné jméno
        A= "2"    #přídavné jméno
        P= "3"    #zájméno
        C= "4"    #číslovka
        V= "5"    #sloveso
        D= "6"    #příslovce
        R= "7"    #předložka
        J= "8"    #spojka
        T= "9"    #částice
        I= "10"   #citoslovce

        DEGREE_TITLE= "t"   #titul
        ROMAN_NUMBER= "r"   #římská číslice
        INITIAL_ABBREVIATION= "a"    #Iniciálová zkratka.
        X= "x"    #neznámé
        
        @property
        def isPOSType(self):
            """
            Určuje zda-li se jedná o typ terminálu odpovídajícím slovnímu druhu.
            
            :return: True odpovídá slovnímu druhu. False jinak.
            :rtype: bool
            """
            use=set([self.N, self.A,self.P,self.C,self.V,self.D,self.R,self.J,self.T, self.I])
            
            return self in use
            
        def toPOS(self):
            """
            Provede konverzi do POS.
            Pokud nelze vrací None
            
            :return: Mluvnická kategorie.
            :rtype: POS
            """
            if self.isPOSType:
                #lze převést pouze určité typy terminálu
                #a to pouze typy terminálu, které vyjadřují slovní druhy
                return {
                    self.N: POS.NOUN,           #podstatné jméno
                    self.A: POS.ADJECTIVE,      #přídavné jméno
                    self.P: POS.PRONOUN,        #zájméno
                    self.C: POS.NUMERAL,        #číslovka
                    self.V: POS.VERB,           #sloveso
                    self.D: POS.ADVERB,         #příslovce
                    self.R: POS.PREPOSITION,    #předložka
                    self.J: POS.CONJUNCTION,    #spojka
                    self.T: POS.PARTICLE,       #částice
                    self.I: POS.INTERJECTION    #citoslovce
                    }[self]
                
            return None
    
    class Attribute(object):
        """
        Terminálový atributy.
        """
        
        
        class Type(Enum):
            """
            Druh atributu.
            """
            
            GENDER="g"  #rod slova musí být takový    (filtrovací atribut)
            NUMBER="n"  #mluvnická kategorie číslo. Číslo slova musí být takové. (filtrovací atribut)
            CASE="c"    #pád slova musí být takový    (filtrovací atribut)
            TYPE="t"    #druh slova ve jméně Křestní, příjmení atd. (Informační atribut)
            #Pokud přidáte nový je třeba upravit Attribute.createFrom a isFiltering

            @property
            def isFiltering(self):
                """
                Určuje zda-li daný typ je filtrovacím (klade dodatečné restrikce).
                
                :return: True filtrovací. False jinak.
                :rtype: bool
                """
                #!POZOR filtrovací atributy musí mít value typu MorphCategory
                fil=set([self.GENDER, self.NUMBER, self.CASE])
                
                return self in fil
        
        def __init__(self, attrType, val):
            """
            Vytvoří atribut neterminálu.
            
            :param attrType: Druh attributu.
            :type attrType: self.Type
            :param val: Hodnota atributu.
            :raise InvalidGrammarException: Při nevalidní hodnotě atributu.
            """
            
            self._type=attrType
            if self.type.isFiltering and not isinstance(val, MorphCategory):
                #u filtrovacích atributů musí být hodnota typu MorphCategory
                raise InvalidGrammarException(Errors.ErrorMessenger.CODE_GRAMMAR_INVALID_FILE)
            self._val=val
            
        @classmethod
        def createFrom(cls, s):
            """
            Vytvoří atribut z řetězce.
            
            :param s: Řetezec reprezentující atribut a jeho hodnotu
                Příklad: "g=M"
            :type s: str
            :raise InvalidGrammarException: Při nevalidní hodnotě atributu.
            """
            
            aT, aV= s.strip().split("=")
            try:
                t=cls.Type(aT)
            except ValueError:
                #neplatný argumentu
                
                raise InvalidGrammarException(Errors.ErrorMessenger.CODE_GRAMMAR_INVALID_ARGUMENT, \
                                              Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_INVALID_ARGUMENT).format(s))
            v=None
            
            #vytvoříme hodnotu atributu
            if cls.Type.GENDER==t:
                v=Gender.fromLntrf(aV)
            elif cls.Type.NUMBER==t:
                v=Number.fromLntrf(aV)
            elif cls.Type.CASE==t:
                v=Case.fromLntrf(aV)   
            else:
                v=WordTypeMark(aV)
            
            return cls(t,v)
        
        @property
        def type(self):
            return self._type
        
        @property
        def value(self):
            """
            :return: Hodnota attributu.
            """
            return self._val
        
        def __str__(self):
            return str(self._type.value)+"="+str(self._val.value)
                        
        def __hash__(self):
            return hash((self._type, self._val))
        
        def __eq__(self, other):
            if self.__class__ is other.__class__:
                return self._type==other._type and self._val==other._val
            
            return False
        
    
    def __init__(self, terminalType, attr=set()):
        """
        Vytvoření terminálu.
        Pokud není předán atribut s typem slova ve jméně, tak je automaticky přidán
        attribut s hodnotou WordTypeMark.UNKNOWN
        
        :param terminalType: Druh terminálu.
        :type terminalType: Type
        :param attr: Attributy terminálu. Určují dodatečné podmínky/informace na vstupní slovo.
                Musí vždy obsahovat atribut daného druhu pouze jedenkrát. Jinak může způsobit nedefinované chování
                u nějakých metod.
        :type attr: Attribute
        """
        
        self._type=terminalType
        
        
        #zjistíme, zda-li byl předán word type mark
        if not any(a.type==self.Attribute.Type.TYPE for a in attr):
            #nebyl, přidáme neznámý
            attr=attr|set([self.Attribute(self.Attribute.Type.TYPE, WordTypeMark.UNKNOWN)])
        
        self._attributes=frozenset(attr)
        
    def getAttribute(self, t):
        """
        Vrací atribut daného druhu.
        
        :param t: druh attributu
        :type t: self.Attribute.Type
        :return: Atribut daného druhu a None, pokud takový atribut nemá.
        :rtype: self.Attribute | None
        """
        
        for a in self._attributes:
            if a.type==t:
                return a
        
        return None
    
    @property
    def type(self):
        """
        Druh terminálu.
        
        :rtype: self.Type
        """
        return self._type
        
    @property
    def fillteringAttr(self):
        """
        Získání všech attributů, které kladou dodatečné podmínky (např. rod musí být mužský).
        Všechny takové attributy mají value typu MorphCategory.
        Nevybírá informační atributy.
        
        :return: Filtrovací atributy, které má tento terminál.
        :rtype: Set[Attribute]
        """
    
        return set(a for a in self._attributes if a.type.isFiltering)
    
    def tokenMatch(self, t):
        """
        Určuje zda daný token odpovídá tomuto terminálu.
        
        :param t: Token pro kontrolu.
        :type t: Token
        :return: Vrací True, pokud odpovídá. Jinak false.
        :rtype: bool
        """

        if t.type!=Token.Type.ANALYZE:
            #jedná se o jednoduchý token bez nutnosti morfologické analýzy
            return t.type.value==self._type.value   #V tomto případě požívá terminála  token stejné hodnoty u typů
        else:
            if not self._type.isPOSType:
                #jedná se o typ terminálu nepoužívající analyzátor, ale token je jiného druhu.
                return False
            
            pos=t.word.info.getAllForCategory(MorphCategories.POS, set( a.value for a in self.fillteringAttr))  
            #máme všechny možné slovní druhy, které prošly atributovým filtrem 
       
            return self._type.toPOS() in pos

    def __str__(self):
        s=str(self._type.value)
        if self._attributes:
            s+="{"+", ".join( str(a) for a in self._attributes )+"}"
        return s
    
    def __hash__(self):
        return hash((self._type,self._attributes))
        
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self._type==other._type and self._attributes==other._attributes
        
        return False
class Token(object):
    """
    Token, který je získán při lexikální analýze.
    """
    
    class Type(Enum):
        """
        Druh tokenu
        """
        ANALYZE=1   #komplexní typ určený morfologickou analýzou slova
        DEGREE_TITLE= Terminal.Type.DEGREE_TITLE.value   #titul
        ROMAN_NUMBER= Terminal.Type.ROMAN_NUMBER.value   #římská číslice
        INITIAL_ABBREVIATION= Terminal.Type.INITIAL_ABBREVIATION.value   #Iniciálová zkratka.
        EOF= Terminal.Type.EOF.value #konec vstupu
        X= Terminal.Type.X.value    #neznámé
        #Pokud zde budete něco měnit je třeba provést úpravy v Token.terminals.

        def __str__(self):
            return str(self.value)
                
        def __hash__(self):
            return hash(self.value)
        
        def __eq__(self, other):
            if self.__class__ is other.__class__:
                return self.value==other.value
            
            return False
    
    def __init__(self, word:Word, tokenType):
        """
        Vytvoření tokenu.
        
        :param word: Slovo ze, kterého token vznikl.
        :type word: namegenPack.Name.Word
        :param tokenType: Druh tokenu.
        :type tokenType: self.Type
        """
        self._word=word
        self._type=tokenType
        
    @property
    def word(self):
        """
        Slovo ze vstupu, které má přiřazeno tento token.
        """
        
        return self._word;
    
    @property
    def type(self):
        """
        Druh tokenu.
        
        :rtype: Type 
        """
        return self._type
    
    def __str__(self):
        return str(self._type)+"("+str(self._word)+")"
    
    '''
    TODO: DELETE
    @property
    def terminals(self):
        """
        Získání všech přijatelných terminálů k danému slovu, které tento
        token reprezentuje.
        
        :return: Množina všech vhodných terminálů k tomuto tokenu.
        :rtype: Set[Terminal]
        """
        res=set()
        
        if self._type!=self.Type.ANALYZE:
            return set(Terminal(self._type.value))
        
        #rozgenerujeme terminály na základě morfologické analýzy slova
        
        
        
        return self._type.terminalRepr
    '''
    
class Lex(object):
    """
    Lexikální analyzátor pro jména.
    """

    ROMAN_NUMBER_REGEX=re.compile(r"^X{0,3}(IX|IV|V?I{0,3})\.?$", re.IGNORECASE)
    
    @classmethod
    def getTokens(cls, name):
        """
        Získání tokenů pro sémantický analyzátor.

        :param name: Jméno pro analýzu
        :type name: Name
        :return: List tokenů pro dané jméno.
        :rtype: [str]
        :raise Word.WordCouldntGetInfoException: Vyjímka symbolizující, že se nepovedlo získat morfologické kategorie ke slovu.
        """
        tokens=[]
        for w in name:
            if cls.ROMAN_NUMBER_REGEX.match(str(w)):
                #římská číslovka
                token=Token(w, Token.Type.ROMAN_NUMBER)
            elif w[-1] == ".":
                #předpokládáme titul nebo iniciálovou zkratku
                if len(w)==2:
                    #zkratka
                    token=Token(w, Token.Type.INITIAL_ABBREVIATION)
                else:
                    #titul
                    token=Token(w, Token.Type.DEGREE_TITLE)
            else:
                #ostatní
                token=Token(w, Token.Type.ANALYZE)
                
            tokens.append(token)
            
        tokens.append(Token(None, Token.Type.EOF)) 
    
        return tokens  
     
class AnalyzedToken(object):
    """
    Jedná se o analyzovaný token, který vzniká při syntaktické analýze.
    Přidává k danému tokenu informace získané analýzou. Informace jako je například zda se má
    dané slovo ohýbat, či nikoliv.
    """
    
    def __init__(self, token:Token, morph:bool=None, matchingTerminal:Terminal=None):
        """
        Pro běžný token vyrobí jaho analyzovanou variantu.
        
        :param token: Pro kterého budujeme analýzu.
        :type token: Token
        :param morph:Příznak zda se slovo, jenž je reprezentováno tímto tokenem, má ohýbat. True ohýbat. False neohýbat.
        :type morph: bool
        :param matchingTerminal: Získaný terminál při analýze, který odpovídal tokenu.
        :type matchingTerminal: Terminal
        """
        
        self._token=token
        self._morph=morph    #příznak zda-li se má dané slovo ohýbat
        self._matchingTerminal=matchingTerminal #Příslušný terminál odpovídající token (získaný při analýze).
        
    @property
    def morph(self):
        """
        Příznak zda se slovo, jenž je reprezentováno tímto tokenem, má ohýbat.
        
        :return: None neznáme. True ohýbat. False neohýbat.
        :rtype: bool
        """
        return self._morph
        
    @morph.setter
    def morph(self, val:bool):
        """
        Určení zda-li se má slovo, jenž je reprezentováno tímto tokenem, ohýbat.
        
        :param val: True ohýbat. False neohýbat.
        :type val: bool
        """
        self._morph=val
    
    @property
    def matchingTerminal(self)->Terminal:
        """
        Získaný terminál při analýze, který odpovídal tokenu.
        
        :return: Odpovídající terminál z gramatiky.
        :rtype: Terminal
        """
        
        return self._matchingTerminal
    
    @matchingTerminal.setter
    def matchingTerminal(self, t:Terminal):
        """
        Přiřazení terminálu.
        
        :param t: Odpovídající terminál.
        :type t: Terminal
        """
        
        self._matchingTerminal=t
    
    @property
    def morphCategories(self) -> Set[MorphCategory]:
        """
        Získání morfologických kategorií, které na základě analýzy má dané slovo patřící k tokenu mít.

        Příklad: Analýzou jsme zjistili, že se může jednat pouze o podstatné jméno rodu mužského v jednotném čísle.
        
        Pozor! Je zakázán výběr StylisticFlag.COLLOQUIALLY
        Tyto dodatečné podmínky jsou přímo uzpůsobeny pro použití výsledku ke generování tvarů.
        
        :rtype: Set[MorphCategory]
        """
        
        #nejprve vložíme filtrovací atributy
        categories=set(a.value for a in self.matchingTerminal.fillteringAttr)
        
        
        #můžeme získat další kategorie na základě morfologické analýzy
        if self.matchingTerminal.type.isPOSType:
            #pro práci s morfologickou analýzou musí byt POS type
            categories.add(self.matchingTerminal.type.toPOS())    #vložíme požadovaný tvar do filtru
        
            #Například pokud víme, že máme přídavné jméno rodu středního v jednotném čísle
            #a morf. analýza nám řekne, že přídavné jméno může být pouze prvního stupně, tak tuto informaci zařadíme
            #k filtrům
                
            for _, morphCategoryValues in self._token.word.info.getAll(categories).items():
                if len(morphCategoryValues)==1:
                    #daná kategorie má pouze jednu možnou hodnotu použijeme ji jako filtr
                    catVal=next(iter(morphCategoryValues))
                    if catVal!=StylisticFlag.COLLOQUIALLY:# hovorové a pády nechceme
                        categories.add(catVal)
    
        
        return categories

class InvalidGrammarException(Errors.ExceptionMessageCode):
    pass

class Rule(object):
    """
    Reprezentace pravidla pro gramatiku.
    """
    
    TERMINAL_REGEX=re.compile("^(.+?)(\{(.*)\})?$") #oddělení typu a attrbutů z terminálu
    
    def __init__(self, fromString, terminals, nonterminals):
        """
        Vytvoření pravidla z řetězce.
        formát pravidla: Neterminál -> Terminály a neterminály
        
        :param fromString: Pravidlo v podobě řetězce.
        :type fromString: str
        :param terminals: Zde bude ukládat nalezené terminály.
        :type terminals: set
        :param nonterminals: Zde bude ukládat nalezené neterminály.
        :type nonterminals: set
        :raise InvalidGrammarException: 
             pokud je pravidlo v chybném formátu.
        """
        try:
            self._leftSide, self._rightSide=fromString.split("->")
        except ValueError:
            #špatný formát pravidla
            raise InvalidGrammarException(Errors.ErrorMessenger.CODE_GRAMMAR_INVALID_FILE,
                                          Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_INVALID_FILE)+"\n\t"+fromString)
            
        self._leftSide=self._parseSymbol(self._leftSide)
        if isinstance(self._leftSide, Terminal) or self._leftSide==Grammar.EMPTY_STR:
            #terminál nebo prázdný řetězec
            #ovšem v naší gramatice může být na levé straně pouze neterminál
            raise InvalidGrammarException(Errors.ErrorMessenger.CODE_GRAMMAR_INVALID_FILE,
                                          Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_INVALID_FILE)+"\n\t"+fromString)
        
        #neterminál, vše je ok
        nonterminals.add(self._leftSide)

            
        self._rightSide=[x for x in self._rightSide.split()]

        #vytvoříme ze řetězců potřebné struktury a přidáváme nalezené neterminály do množiny neterminálů
        for i, x in enumerate(self._rightSide):
            try:
                self.rightSide[i]=self._parseSymbol(x)
                if isinstance(self.rightSide[i], Terminal):
                    # terminál
                    terminals.add(self.rightSide[i])
                else:
                    #neterminál nebo prázdný řetězec
                    if self.rightSide[i]!=Grammar.EMPTY_STR:
                        #neterminál
                        nonterminals.add(self.rightSide[i])
            except:
                #došlo k potížím s aktuálním pravidlem
                raise InvalidGrammarException(Errors.ErrorMessenger.CODE_GRAMMAR_INVALID_FILE, 
                                              Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_INVALID_FILE)+"\n\t"+x+"\t"+fromString)
        
    @classmethod
    def _parseSymbol(cls, s):
        """
        Získá z řetězce symbol z gramatiky.
        
        :param s: Řetězec, který by měl obsahovat neterminál, terminál či symbol prázdného řetězce.
        :type s: str
        :return: Symbol v gramatice
        :raise InvalidGrammarException: 
             pokud je symbol nevalidní
        """
        x=s.strip()
        
        if x==Grammar.EMPTY_STR:
            #prázdný řetězec není třeba dále zpracovávat
            return x
            
        mGroups=cls.TERMINAL_REGEX.match(x)
        #máme naparsovaný terminál/neterminál
        #příklad: rn{g=M,t=G}
        #Group 1.    0-2    `rn`
        #Group 2.    2-11    `{g=M,t=G}`
        #Group 3.    3-10    `g=M,t=G`

        termType=None
        try:
            termType=Terminal.Type(mGroups.group(1) )
            
        except ValueError:
            #neterminál, nemusíme nic měnit
            #stačí původní reprezentace
            return x
        
        #máme terminál
        attrs=set()
        attrTypes=set() #pro kontorolu opakujicich se typu
        if mGroups.group(3):
            #terminál má argumenty
            for a in mGroups.group(3).split(","):
                ta=Terminal.Attribute.createFrom(a)
                if ta.type in attrTypes:
                    #typ argumentu se opakuje
                    raise InvalidGrammarException(Errors.ErrorMessenger.CODE_GRAMMAR_ARGUMENT_REPEAT, \
                                                      Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_ARGUMENT_REPEAT).format(a))
                attrTypes.add(ta.type)
                attrs.add(ta)
            
        return Terminal(termType, attrs)
        
        
    def getSymbols(self):
        """
        Vrací všechny terminály a neterminály.
        
        :return: Množinu terminálů a neterminálů figurujících v pravidle.
        :rtype: set
        """
        
        return set(self._leftSide)+set(self._rightSide)
    
    @property
    def leftSide(self):
        """
        Levá strana pravidla.
        :return: Neterminál.
        :rtype: str
        """
        return self._leftSide
    
    @property
    def rightSide(self):
        """
        Pravá strana pravidla.
        :return: Terminály a neterminály (epsilon) na právé straně pravidla.
        :rtype: list
        """
        return self._rightSide
    
    
        
    def __str__(self):
        return self._leftSide+"->"+" ".join(str(x) for x in self._rightSide)
    
    def __repr(self):
        return str(self)
    
    def __hash__(self):
            return hash((self._leftSide, tuple(self._rightSide)))
        
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self._leftSide==other._leftSide and self._rightSide==other._rightSide
            
        return False


class Symbol(object):
        """
        Reprezentace symbolu na zásobníku
        """
        
        def __init__(self, s, isTerm=True):
            """
            Vytvoření symbolu s typu t.
            :param s: Symbol
            :param t: Druh terminál(True)/neterminál(False).
            :type t: bool
            """
            
            self._s=s
            self._isTerm=isTerm
            
        @property
        def val(self):
            return self._s
        
        @property
        def isTerm(self):
            """
            True jedná se o terminál. False jedná se neterminál.
            """
            return self._isTerm
        
        
class SyntaxTree(object):
    """
    TODO:DELETE
    Syntaktický strom.
    """
    
    
    
    def __init__(self, rules):
        """
        Vytvoření stromu
        :param rules: (MODIFIKUJE) Očekáva list pravidel, ze kterých vytvoří strom. 
        :type rules: list(Rule)
        """
        
        actRule=rules.pop()
        
        self._root=actRule.leftSide
        self._morph=self._root[0]!=self.NON_GEN_MORPH_SIGN  #příznak toho, že v tomto stromu na tomto místě se mají ohýbat slova

        self.morphMask=[]  #maska určující zda-li se má ohýbat. True znamená, že ano. 
        
        for x in actRule.rightSide:
            if any( x==r.leftSide for r in rules):
                #lze rozgenerovat dál
                childT=SyntaxTree(rules, self._morph)
                
                #přidáme masku od potomka
                self.morphMask+=childT.morphMask
                
            else:
                #nelze
                self.morphMask.append(self._morph)       
        
        
    

class Grammar(object):
    """
    Používání a načtení gramatiky ze souboru.
    Provádí sémantickou analýzu
    """
    EMPTY_STR="ε"   #Prázdný řetězec.
    
    #Má-li neterminál tuto značku na začátku znamená to, že všechny derivovatelné řetězce z něj
    #se nemají ohýbat.
    NON_GEN_MORPH_SIGN="!"   
    
    
    class NotInLanguage(Errors.ExceptionMessageCode):
        """
        Řetězec není v jazyce generovaným danou gramatikou.
        """
        pass
    
    class ParsingTableSymbolRow(dict):
        """
        Reprezentuje řádek parsovací tabulky, který odpovídá symbolu.
        Chová se jako dict() s tím rozdílem, že
        pokud je namísto běžného SymbolRow[Terminal] použito SymbolRow[Token], tak pro daný symbol na zásobníku
        vybere všechna pravidla (vrací množinu pravidel), která je možné aplikovat pro daný token (jeden token může odpovídat více terminálům).
    
        Vkládané klíče musí být Terminály.
        
        """
        
        def __getitem__(self, key):
            """
            Pokud je namísto běžného SymbolRow[Terminal] použito SymbolRow[Token], tak pro daný symbol na zásobníku
            vybere všechna pravidla (vrací množinu pravidel), která je možné aplikovat pro daný token (jeden token může odpovídat více terminálům).
            :param key: Terminal/token pro výběr.
            :type key: Terminal | Token
            :raise WordCouldntGetInfoException: Problém při analýze slova.
            """
            if isinstance(key, Token):
                #Nutné zjistit všechny terminály, které odpovídají danému tokenu.
                res=set()
                for k in self.keys():
                    if k.tokenMatch(key):
                        #daný terminál odpovídá tokenu, přidejme pravidla
                        res|=dict.__getitem__(self, k)
                return res
            else:
                #běžný výběr
                return dict.__getitem__(self, key)
            


    def __init__(self, filePath):
        """
        Inicializace grammatiky jejim načtením ze souboru.
        
        :param filePath: Cesta k souboru s gramatikou
        :type filePath: str
        :raise exception:
            Errors.ExceptionMessageCode pokud nemůže přečíst vstupní soubor.
            InvalidGrammarException pokud je problém se samotnou gramtikou.
        """
        self._terminals=set([Terminal(Terminal.Type.EOF)])  #implicitní terminál je konec souboru
        self._nonterminals=set()
        
        self.load(filePath)
        
    
    def load(self,filePath):
        """
        Načtení gramatiky ze souboru.
        
        :param filePath: Cesta k souboru s gramatikou.
        :type filePath: str
        :raise exception:
            Errors.ExceptionMessageCode pokud nemůže přečíst vstupní soubor.
            InvalidGrammarException pokud je problém se samotnou gramtikou.
            
        """
        try:
            with open(filePath, "r") as fG:
    
                firstNonEmptyLine=""
                for line in fG:
                    firstNonEmptyLine=self._procGFLine(line)
                    if len(firstNonEmptyLine)>0:
                        break
                
                #první řádek je startovací neterminál
                self._startS=self._procGFLine(firstNonEmptyLine)
                if len(self._startS) == 0:
                    raise InvalidGrammarException(code=Errors.ErrorMessenger.CODE_GRAMMAR_NO_START_SYMBOL)

                #Zbytek řádků představuje pravidla. Vždy jedno pravidlo na řádku.
                self._rules=set()
                for line in fG:
                    line=self._procGFLine(line)
                    if len(line)==0:
                        #prázdné přeskočíme
                        continue
                    #formát pravidla: Neterminál -> Terminály a neterminály
                    #přidáváme nová pravidla a zároveň tvoříme množinu terminálů a neterminálů
                    self._rules.add(Rule(line, self._terminals, self._nonterminals))
                    
                
                if len(self._rules) == 0:
                    raise InvalidGrammarException(code=Errors.ErrorMessenger.CODE_GRAMMAR_NO_RULES)

                if self._startS not in self._nonterminals:
                    #startovací symbol není v množině neterminálů
                    raise InvalidGrammarException(code=Errors.ErrorMessenger.CODE_GRAMMAR_START_SYMBOL)
            
        except IOError:
            raise Errors.ExceptionMessageCode(Errors.ErrorMessenger.CODE_COULDNT_READ_INPUT_FILE,
                                              Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_COULDNT_READ_INPUT_FILE)+"\n\t"+filePath)
            
        #vytvoříme si tabulku pro parsování
        self._makeTable()
        
    @staticmethod
    def _procGFLine(line):
        """
        Před zpracování řádku ze souboru s gramatikou. Odstraňuje komentáře a zbytečné bíle znaky.
        
        :param line: Řádek ze souboru s gramatikou.
        :type line: str
        """
        return line.split("#",1)[0].strip()
        
            
    def analyse(self, tokens):
        """
        Provede syntaktickou analýzu pro dané tokeny.
        Poslední token předpokládá EOF. Pokud jej neobsahuje, tak jej sám přidá na konec tokens.
        
        
        :param tokens: Tokeny pro zpracování.
        :type tokens: list
        :return: Dvojici s listem listu pravidel určujících všechny možné derivace a list listů analyzovaných tokenů.
        :rtype: (list(list(Rule)), list(list(AnalyzedToken)))
        :raise NotInLanguage: Řetězec není v jazyce generovaným danou gramatikou.
        :raise WordCouldntGetInfoException: Problém při analýze slova.
        """
        
        if tokens[-1].type!=Token.Type.EOF:
            tokens.append(Token(None,Token.Type.EOF))
            
        # Přidáme na zásoník konec vstupu a počáteční symbol
        stack=[Symbol(Terminal(Terminal.Type.EOF), True), Symbol(self._startS, False)]
        position=0
        
        #provedeme samotnou analýzou a vrátíme výsledek
        return self.crawling(stack, tokens, position, True)
        
    
    def crawling(self, stack, tokens, position, morph=True):
        """
        Provádí analýzu zda-li posloupnost daných tokenů patří do jazyka definovaného gramatikou.
        Vrací posloupnost použitých pravidel. Nezastaví se na první vhodné posloupnosti pravidel, ale hledá všechny možné.
        
        Tato metoda slouží především pro možnost implementace zpětného navracení při selhání, či hledání další vhodné posloupnosti
        pravidel.
        
        :param stack: Aktuální obsah zásobníku. (modifukuje jej)
        :type stack: list(Symbol)
        :param tokens: posloupnost tokenů na vstupu
        :type tokens: list(Token)
        :param position: Index aktuálního tokenu. Definuje část vstupní posloupnosti tokenů, kterou budeme procházet.
            Od předaného indexu do konce.
        :type position: integer
        :param morph: Flag, který určuje zda-li se nacházíme v části stromu, kde se slova mají ohýbat, či ne.
            Jedná se o zohlednění příznaku self.NON_GEN_MORPH_SIGN z gramatiky.
        :type morph: bool
        :return: Dvojici s listem listu pravidel určujících všechny možné derivace a list listů analyzovaných tokenů.
        :rtype: (list(list(Rule)), list(list(AnalyzedToken)))
        :raise NotInLanguage: Řetězec není v jazyce generovaným danou gramatikou.
        """
        rules=[]    #aplikovaná pravidla
        aTokens=[]  #analyzované tokeny
        
        while(len(stack)>0):
            s=stack.pop()
            token=tokens[position]
            
            if s.isTerm:
                #terminál na zásobníku
                if s.val.tokenMatch(token):
                    #stejný token můžeme se přesunout
                    #token odpovídá terminálu na zásobníku
                    position+=1
                    
                    #ještě vytvoříme analyzovaný token
                    aTokens.append(AnalyzedToken(token, morph, s.val))# s je odpovídající terminál
                    
                else:
                    #chyba rozdílný terminál na vstupu a zásobníku
                    raise self.NotInLanguage(Errors.ErrorMessenger.CODE_GRAMMAR_NOT_IN_LANGUAGE, \
                                             Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_NOT_IN_LANGUAGE).format(\
                                                s.val, str(token), ", ".join([str(r) for r in rules])))
            else:
                #neterminál na zásobníku
                
                

                #vybereme všechna možná pravidla pro daný token na vstupu a symbol na zásobníku
                
                actRules=self._table[s.val][token]  #díky použité třídě ParsingTableSymbolRow si můžeme dovolit použít přímo token
                
                if not actRules:
                    #v gramatice neexistuje vhodné pravidlo
                    
                    raise self.NotInLanguage(Errors.ErrorMessenger.CODE_GRAMMAR_NOT_IN_LANGUAGE, \
                                             Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_NOT_IN_LANGUAGE).format(\
                                                s.val, str(token), ", ".join([str(r) for r in rules])))
                
                #pro každou možnou derivaci zavoláme rekurzivně tuto metodu
                newRules=[]
                newATokens=[]

                for r in actRules:
                    try:
                        #prvně aplikujeme pravidlo
                        newStack=stack.copy()
                        self.putRuleOnStack(r, newStack)
                        
                        #zkusíme zda-li s tímto pravidlem uspějeme
                        resRules, resATokens=self.crawling(newStack, tokens, position, morph=s.val[0]!=self.NON_GEN_MORPH_SIGN)
                        
                        if resRules and resATokens:
                            #zaznamenáme aplikováná pravidla a analyzované tokeny
                            #může obsahovat i více různých derivací
                            for x in resRules:
                                #musíme předřadit aktuální pravidlo a pravidla předešlá
                                newRules.append(rules+[r]+x)
                                
                            for x in resATokens:
                                #musíme předřadit předešlé analyzované tokeny
                                newATokens.append(aTokens+x)
                                
                    except self.NotInLanguage:
                        #tato větev nikam nevede, takže ji prostě přeskočíme
                        pass
            
                if len(newRules) == 0:
                    #v gramatice neexistuje vhodné pravidlo
                    
                    raise self.NotInLanguage(Errors.ErrorMessenger.CODE_GRAMMAR_NOT_IN_LANGUAGE, \
                                             Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_NOT_IN_LANGUAGE).format(\
                                                s.val, str(token), ", ".join([str(r) for r in rules])))
                    
                #jelikož jsme zbytek prošli rekurzivním voláním, tak můžeme již skončit
                return (newRules,newATokens)
                    
        
        
        #Již jsme vyčerpali všechny možnosti. Příjmáme naši část vstupní pousloupnosti a končíme.
        #Zde se dostaneme pouze pokud jsme po cestě měli možnost aplikovat pouze jen jedno pravidlo.
        return ([rules], [aTokens])
     
    def putRuleOnStack(self, rule:Rule, stack):
        """
        Vloží pravou stranu pravidla na zásobník.
        
        :param rule: Pravidlo pro vložení.
        :type rule: Rule
        :param stack: Zásobník pro manipulaci. Obsahuje výsledek.
        :type stack:list
        """
        
        for rulePart in reversed(rule.rightSide):
            if rulePart!=self.EMPTY_STR: #prázdný symbol nemá smysl dávat na zásobník
                stack.append(Symbol(rulePart, rulePart in self._terminals or rulePart==self.EMPTY_STR))
                
    
    @classmethod
    def getMorphMask(cls, rules, morph=True):
        """
        Zjistí pro jaká slova má generovat tvary.
        Tím, že si tvoří z pravidel syntaktický strom.
        
        :param rules: (MODIFIKUJE TENTO PARAMETR!) Pravidla získaná z analýzy (metoda analyse).
        :type rules: list
        :param morph: Pokud je false znamená to, že v této části syntaktického stromu negenerujeme tvary.
        :type morph: boolean
        :return: Maska v podobě listu, kde pro každé slovo je True (generovat) nebo False (negenerovat).
        :rtype: list
        """

        actRule=rules.pop(0)

        if morph:
            #zatím jsme mohli ohýbat, ale to se může nyní změnit
            morph=actRule.leftSide[0]!=cls.NON_GEN_MORPH_SIGN  #příznak toho, že v tomto stromu na tomto místě se mají/nemají ohýbat slova

        morphMask=[]  #maska určující zda-li se má ohýbat. True znamená, že ano. 
        
        
        #máme levou derivaci, kterou budeme symulovat a poznamenáme si vždy
        #zda-li zrovna nejsme v podstromě, který má příznak pro neohýbání.
        #pravidlo je vždy pro první neterminál z leva
        
        for x in [p for p in  actRule.rightSide if p!=cls.EMPTY_STR]:
            if any( x==r.leftSide for r in rules):
                #lze dále rozgenerovávat
                #přidáme masku od potomka
                
                morphMask+=cls.getMorphMask(rules, morph)#rovnou odstraní použitá pravidla v rules
            else:
                #nelze
                morphMask.append(morph)  

        return morphMask
                
    def _makeTable(self):
        """
        Vytvoření parsovací tabulky.
        
        :raise exception: 
            InvalidGrammarException při nejednoznačnosti.
        """
        self._makeEmptySets()
        #COULD BE DELETED print("empty", self._empty)
        self._makeFirstSets()
        #COULD BE DELETED print("first", self._first)
        self._makeFollowSets()
        #COULD BE DELETED print("follow", self._follow)
        self._makePredictSets()
        #COULD BE DELETED print("predict", ", ".join(str(r)+":"+str(t) for r,t in self._predict.items()))
        
        """
        COULD BE DELETED
        print("predict")
        
        for i, l in enumerate([ str(k)+":"+str(x) for k,x in self._predict.items()]):
            print(i,l)
            
        """

        #inicializace tabulky
        self._table={ n:self.ParsingTableSymbolRow({t:set() for t in self._terminals}) for n in self._nonterminals}
        
        #zjištění pravidla pro daný terminál na vstupu a neterminál na zásobníku
        for r in self._rules:
            for t in self._terminals:
                if t in self._predict[r]:
                    #t může být nejlevěji derivován
                    self._table[r.leftSide][t].add(r)

        #Jen pro testovani self.printParsingTable()
                  
    '''
    Jen pro testovani
    Potřebuje importovat pandas.
    
    def printParsingTable(self):
        """
        Vytiskne na stdout tabulku pro analýzu.
        """
        inputSymbols=[Token.Type.EOF.terminalRepr]+list(sorted(self._terminals))
        
        ordeNon=list(self._nonterminals)
        data=[]
        for n in ordeNon:
            data.append([str(self._table[n][iS]) for iS in inputSymbols])
            
        print(pandas.DataFrame(data, ordeNon, inputSymbols))
    '''
    
    def _makeEmptySets(self):
        """
        Získání "množin" empty (v aktuální gramatice) v podobě dict s příznaky True/False,
         zda daný symbol lze derivovat na prázdný řetězec.
         
        Jedná se o Dict s příznaky: True lze derivovat na prázdný řetězec, či False nelze. 
        """

        self._empty={t:False for t in self._terminals} #terminály nelze derivovat na prázdný řetězec
        self._empty[self.EMPTY_STR]=True    #prázdný řetězec mohu triviálně derivovat na przdný řetězec
        
        for N in self._nonterminals:
            #nonterminály inicializujeme na false
            self._empty[N]=False
        
        
        #pravidla typu: N -> ε
        for r in self._rules:
            if r.rightSide == [self.EMPTY_STR]:
                self._empty[r.leftSide]=True
            else:
                self._empty[r.leftSide]=False
        
        #hledáme ty, které se mohou proderivovat na prázdný řetězec ve více krocích
        #procházíme pravidla dokud se mění nějaká množina empty
        change=True
        while change: 
            change=False
            
            for r in self._rules:
                if all(self._empty[rN] for rN in r.rightSide):
                    #všechny symboly na pravé straně pravidla lze derivovat na prázdný řetězec
                    if not self._empty[r.leftSide]:
                        #došlo ke změně
                        self._empty[r.leftSide]=True
                        change=True
   
    
    def _makeFirstSets(self):
        """
        Získání "množin" first (v aktuální gramatice) v podobě dict s množinami 
        prvních terminálů derivovatelných pro daný symbol.
        
        Před zavoláním této metody je nutné zavolat _makeEmptySets!
        """

        self._first={t:set([t]) for t in self._terminals} #terminály mají jako prvního samy sebe
        self._first[self.EMPTY_STR]=set()

        #inicializace pro neterminály
        for n in self._nonterminals:
            self._first[n]=set()
            
        #Hledáme first na základě pravidel
        change=True
        while change: 
            change=False
            for r in self._rules:
                #přidáme všechny symboly z first prvního symbolu, který se nederivuje na prázdný
                #také přidáváme first všech po cestě, kteří se derivují na prázdný
                for x in r.rightSide:
                    if self._empty[x]:
                        #derivuje se na prázdný budeme se muset podívat i na další
                        tmp=self._first[r.leftSide] | self._first[x]
                        if tmp!= self._first[r.leftSide]:
                            #došlo ke změně
                            self._first[r.leftSide] = tmp
                            change=True
                    else:
                        #nalezen první, který se nederivuje na prázdný
                        tmp=self._first[r.leftSide] | self._first[x]
                        if tmp!= self._first[r.leftSide]:
                            #došlo ke změně
                            self._first[r.leftSide] = tmp
                            change=True
                        break

    def _makeFollowSets(self):
        """
        Získání množiny všech terminálů, které se mohou vyskytovat vpravo od nějakého neterminálu A ve větné formě.
        
        Před zavoláním této metody je nutné zavolat _makeEmptySets, _makeFirstSets!

        """
        self._follow={ n:set() for n in self._nonterminals} #pouze pro neterminály
        #u startovacího neterminálu se ve větné formě na pravo od něj může vyskytovat pouze konec vstupu
        self._follow[self._startS]=set([Terminal(Terminal.Type.EOF)])
        
        #hledání follow na základě pravidel
        change=True
        while change: 
            change=False
            for r in self._rules:
                for i, x in enumerate(r.rightSide):
                    if x in self._nonterminals:
                        #máme neterminál
                        if i+1<len(r.rightSide):
                            #nejsme na konci
                            tmp=self._follow[x]|self._firstFromSeq(r.rightSide[i+1:])
                            if tmp!=self._follow[x]:
                                #zmena
                                self._follow[x]=tmp
                                change=True
                                
                        if i+1>=len(r.rightSide) or self._emptySeq(r.rightSide[i+1:]):
                            #v pravo je prázdno nebo se proderivujeme k prázdnu
                            
                            tmp=self._follow[x]|self._follow[r.leftSide]
                            if tmp!=self._follow[x]:
                                #zmena
                                self._follow[x]=tmp
                                change=True
                                    
       

        
    
    def _makePredictSets(self):
        """
        Vytvoření množiny Predict(A → x), která je množina všech terminálů, které mohou být aktuálně nejlevěji
        vygenerovány, pokud pro libovolnou větnou formu použijeme pravidlo A → x.
        
        Před zavoláním této metody je nutné zavolat _makeEmptySets, _makeFirstSets, _makeFollowSets!
        
        """
        
        self._predict={}
        
        for r in self._rules:
            if self._emptySeq(r.rightSide):
                self._predict[r]=self._firstFromSeq(r.rightSide)|self._follow[r.leftSide]
            else:
                self._predict[r]=self._firstFromSeq(r.rightSide)
    
    def _firstFromSeq(self,seq):
        """
        Získání množiny first z posloupnosti terminálů a neterminálů
        
        Před zavoláním této metody je nutné zavolat _makeEmptySets, _makeFirstSets!
        
        :param seq: Posloupnost terminálů a neterminálů.
        :type seq: list
        :return: Množina first.
        :rtype: set|None
        """
        
        first=set()
        
        for x in seq:
            if self._empty[x]:
                #derivuje se na prázdný budeme se muset podívat i na další
                first=first|self._first[x]
            else:
                #nalezen první, který se nederivuje na prázdný
                first=first|self._first[x]
                break
        
        return first
    
    def _emptySeq(self,seq):
        """
        Určení množiny empty pro posloupnost terminálů a neterminálů
        
        Před zavoláním této metody je nutné zavolat _makeEmptySets!
        
        :param seq: Posloupnost terminálů a neterminálů.
        :type seq: list
        :return: True proderivuje se k prázdnému řetězce. Jinak false.
        :rtype: bool
        """
        
        return all(self._empty[s] for s in seq)


                
                