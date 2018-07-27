"""
Created on 17. 6. 2018

Modul pro práci s LL gramatikou.

:author:     Martin Dočekal
:contact:    xdocek09@stud.fit.vubtr.cz
"""
from namegenPack import Errors
import re
from .Name import *


class Token(object):
    """
    Token, který je získán při lexikální analýze.
    """
    
    class Type(Enum):
        """
        Druh tokenu
        """
        N= 1    #podstatné jméno
        A= 2    #přídavné jméno
        P= 3    #zájméno
        C= 4    #číslovka
        V= 5    #sloveso
        D= 6    #příslovce
        R= 7    #předložka
        J= 8    #spojka
        T= 9    #částice
        I= 10   #citoslovce
        Z= 11   #symbol
        DEGREE_TITLE= 12   #titul
        ROMAN_NUMBER= 13   #římská číslice
        INITIAL_ABBREVIATION= 14    #Iniciálová zkratka.
        EOF= 15 #konec vstupu
        X= 100    #neznámé

        
        @classmethod
        def createFrom(cls, s):
            """
            Převede z textové reprezentace.
            
            :param s: Textová reprezentace druhu.
            :type s: String
            :raise KeyError: Při neznámém druhu jména.
            """

            return {
                "N":cls.N,
                "A":cls.A,
                "P":cls.P,
                "C":cls.C,
                "V":cls.V,
                "D":cls.D,
                "R":cls.R,
                "J":cls.J,
                "T":cls.T,
                "I":cls.I,
                "Z":cls.Z,
                "T":cls.DEGREE_TITLE,
                "RN":cls.ROMAN_NUMBER,
                "IA":cls.INITIAL_ABBREVIATION,
                "EOF":cls.EOF,
                "X":cls.X
                }[s]
        
        @property
        def terminalRepr(self):
            return {
                self.N:"N",
                self.A:"A",
                self.P:"P",
                self.C:"C",
                self.V:"V",
                self.D:"D",
                self.R:"R",
                self.J:"J",
                self.T:"T",
                self.I:"I",
                self.Z:"Z",
                self.DEGREE_TITLE:"T",
                self.ROMAN_NUMBER:"RN",
                self.INITIAL_ABBREVIATION:"IA",
                self.EOF:0,
                self.X:"X"
                }[self] 
            
                
        def __str__(self):
            return {
                self.N:"N",
                self.A:"A",
                self.P:"P",
                self.C:"C",
                self.V:"V",
                self.D:"D",
                self.R:"R",
                self.J:"J",
                self.T:"T",
                self.I:"I",
                self.Z:"Z",
                self.DEGREE_TITLE:"T",
                self.ROMAN_NUMBER:"RN",
                self.INITIAL_ABBREVIATION:"IA",
                self.EOF:"0",
                self.X:"X"
                }[self] 
                
        def __hash__(self):
            return hash(self.value)
        
        def __eq__(self, other):
            if self.__class__ is other.__class__:
                return self.value==other.value
            
            return False
    
    def __init__(self, word, tokenType):
        """
        Vytvoření tokenu.
        
        :param word: Slovo ze, kterého token vznikl.
        :type word: Word
        :param tokenType: Druh tokenu.
        :type tokenType:
        """
        self._word=word
        self._type=tokenType
        
    @property
    def word(self):
        return self._word;
    
    @property
    def type(self):
        return self._type
    
    @property
    def terminal(self):
        return self._type.terminalRepr
    
    

class Lex(object):
    """
    Lexikální analyzátor pro jména.
    """

    ROMAN_NUMBER_REGEX=re.compile(r"^X{0,3}(IX|IV|V?I{0,3})\.?$", re.IGNORECASE)
    
    @classmethod
    def getTokens(cls, name):
        """
        Získání tokenů pro sémantický analyzátor.
        
        :param cls: Třída
        :param name: Jméno pro analýzu
        :type name: Name
        :return: List tokenů pro dané jméno.
        :rtype: [str]
        :raise Word.WordCouldntGetInfoException: Vyjímka symbolizující, že se nepovedlo získat mluvnické kategorie ke slovu.
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
                token=Token(w, Token.Type.createFrom(w.info["pos"]))
                
            tokens.append(token)
            
        tokens.append(Token(None, Token.Type.EOF)) 
    
        return tokens  


        
class InvalidGrammarException(Errors.ExceptionMessageCode):
    pass

class Rule(object):
    """
    Reprezentace pravidla pro gramatiku.
    """
    
    def __init__(self, fromString, nonterminals, terminals):
        """
        Vytvoření pravidla z řetězce.
        formát pravidla: Neterminál -> Terminály a neterminály
        
        :param fromString: Pravidlo v podobě řetězce.
        :type fromString: str
        :param _nonterminals: Množina neterminálů dané gramatiky.
        :type _nonterminals: set
        :param _terminals:Množina terminálů dané gramatiky.
        :type _terminals: set
        :raise exception: 
            InvalidGrammarException pokud je pravidlo v chybném formátu.
        """
        try:
            self._leftSide, self._rightSide=fromString.split("->")
        except ValueError:
            #špatný formát pravidla
            raise InvalidGrammarException(Errors.ErrorMessenger.CODE_GRAMMAR_INVALID_FILE,
                                          Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_INVALID_FILE)+"\n\t"+fromString)
            
        self._leftSide=self._leftSide.strip()
        
        if self._leftSide not in nonterminals:
            raise InvalidGrammarException(Errors.ErrorMessenger.CODE_GRAMMAR_INVALID_FILE,
                                          Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_INVALID_FILE)+"\n\t"+fromString)
        
        self._rightSide=[x.strip() for x in self._rightSide.split()]

        #kontrola zda-li se na pravé straně opravdu vyskytují pouze terminály a neterminály a nebo Grammar.EMPTY_STR
        for x in self._rightSide:
            if x not in nonterminals and x not in terminals and x !=Grammar.EMPTY_STR:
                raise InvalidGrammarException(Errors.ErrorMessenger.CODE_GRAMMAR_INVALID_FILE, 
                                              Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_INVALID_FILE)+"\n\t"+x+"\t"+fromString)
        
        
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
        :return: Terminály a neterminály (epsilon) na právé straně prvidla.
        :rtype: list
        """
        return self._rightSide
    
    
        
    def __str__(self):
        return self._leftSide+"->"+" ".join(self._rightSide)
    
    def __repr(self):
        return str(self)


class Symbol(object):
        """
        Reprezentace symbolu na zásobníku
        """
        
        def __init__(self, s, isTerm=True):
            """
            Vytvoření symbolu s typu t.
            :param s: Symbol
            :type s: str
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
    Používání a načtení LL gramatiky ze souboru.
    Provádí sémantickou analýzu
    """
    EMPTY_STR="ε"   #Prázdný řetězec.
    
    #Má-li neterminál tuto značku na začátku znamená to, že všechny derivovatelné řetězce z něj
    #se nemají ohýbat.
    NON_GEN_MORPH_SIGN="!"   
    
    class UnknownTerminal(Errors.ExceptionMessageCode):
        """
        Neznámý token, který se nenachází v množině terminálů.
        """
        pass
    
    class NotInLanguage(Errors.ExceptionMessageCode):
        """
        Řetězec není v jazyce generovaným danou gramatikou.
        """
        pass
    

    def __init__(self, filePath):
        """
        Inicializace grammatiky jejim načtením ze souboru.
        
        :param filePath: Cesta k souboru s gramatikou
        :type filePath: str
        :raise exception:
            Errors.ExceptionMessageCode pokud nemůže přečíst vstupní soubor.
            InvalidGrammarException pokud je problém se samotnou gramtikou.
        """
        
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
    
                #první řádek je množina neterminálů
                self._nonterminals=set( n for n in fG.readline().split())
                if len(self._nonterminals) == 0:
                    raise InvalidGrammarException(code=Errors.ErrorMessenger.CODE_GRAMMAR_EMPTY_SET_OF_NONTERMINALS)
                
                #druhý řádek je množina terminálů
                self._terminals=set( t for t in fG.readline().split())
                if len(self._terminals) == 0:
                    raise InvalidGrammarException(code=Errors.ErrorMessenger.CODE_GRAMMAR_EMPTY_SET_OF_TERMINALS)
                            
                if self.EMPTY_STR in self._terminals | self._nonterminals:
                    raise InvalidGrammarException(code=Errors.ErrorMessenger.CODE_GRAMMAR_EPSILON_IN_TERM_OR_NONTERM)
                
                #třetí řádek je startovní symbol
                self._startS=fG.readline().strip()
                if len(self._startS) == 0:
                    raise InvalidGrammarException(code=Errors.ErrorMessenger.CODE_GRAMMAR_NO_START_SYMBOL)
    
                
                if self._startS not in self._nonterminals:
                    #startovací symbol není v množině neterminálů
                    raise InvalidGrammarException(code=Errors.ErrorMessenger.CODE_GRAMMAR_START_SYMBOL)
                
                if len(self._terminals & self._nonterminals)>0:
                    #množina terminálů a neterminálů má neprázdný průnik
                    raise InvalidGrammarException(Errors.ErrorMessenger.CODE_GRAMMAR_SETS_TERM_NONTERM_NON_DIS,
                                                  Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_SETS_TERM_NONTERM_NON_DIS)+"\n\t"+str(self._terminals & self._nonterminals))
                
                #Zbytek řádků představuje pravidla. Vždy jedno pravidlo na řádku.
                self._rules=set()
                for line in fG:
                    #formát pravidla: Neterminál -> Terminály a neterminály
                    self._rules.add(Rule(line, self._nonterminals, self._terminals))
                    
                if len(self._rules) == 0:
                    raise InvalidGrammarException(code=Errors.ErrorMessenger.CODE_GRAMMAR_NO_RULES)
            
        except IOError:
            raise Errors.ExceptionMessageCode(Errors.ErrorMessenger.CODE_COULDNT_READ_INPUT_FILE,
                                              Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_COULDNT_READ_INPUT_FILE)+"\n\t"+filePath)
            
        #vytvoříme si tabulku pro parsování
        self._makeTable()
            
    def analyse(self, tokens):
        """
        Provede syntaktickou analýzu pro dané tokeny.
        Poslední token předpokládá EOF. Pokud jej neobsahuje, tak jej sám přidá na konec tokens.
        
        :param tokens: Tokeny pro zpracování.
        :type tokens: list
        :return: List pravidel určující levou derivaci.
        :rtype: list
        :raise UnknownTerminal: Pokud se objeví terminál, který není v gramatice.
        :raise NotInLanguage: Řetězec není v jazyce generovaným danou gramatikou.
        """
        if tokens[-1].type!=Token.Type.EOF:
            tokens.append(Token(None,Token.Type.EOF))
            
        for t in tokens:
            
            if t.terminal not in self._terminals and t.type!=Token.Type.EOF:
   
                raise self.UnknownTerminal(Errors.ErrorMessenger.CODE_GRAMMAR_UNKNOWN_TERMINAL, \
                                           Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_UNKNOWN_TERMINAL)+"\t"+str(t.terminal))
        
        # Přidáme na zásoník konec vstupu a počáteční symbol
        stack=[Symbol(Token.Type.EOF.terminalRepr, True), Symbol(self._startS, False)]
        position=0
        
        rules=[]    #aplikovaná pravidla
        
        while(len(stack)>0):
            s=stack.pop()
            token=tokens[position].terminal
            
            if s.isTerm:
                #terminál na zásobníku
                if s.val==token:
                    #stejný token můžeme se přesunout
                    position+=1
                    
                else:
                    #chyba rozdílný terminál na vstupu a zásobníku
                    raise self.NotInLanguage(Errors.ErrorMessenger.CODE_GRAMMAR_NOT_IN_LANGUAGE, \
                                             Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_NOT_IN_LANGUAGE).format(\
                                                s.val, token, ", ".join([str(r) for r in rules])))

            else:
                #neterminál na zásobníku
                
                #vybereme pravidlo
                rule=self._table[s.val][token]
                if rule is None:
                    #v gramatice neexistuje vhodné pravidlo
                    raise self.NotInLanguage(Errors.ErrorMessenger.CODE_GRAMMAR_NOT_IN_LANGUAGE, \
                                             Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_NOT_IN_LANGUAGE).format(\
                                                s.val, token, ", ".join([str(r) for r in rules])))
                
                #provedeme derivaci, vložíme pravidlo na zásobník
                for rulePart in reversed(rule.rightSide):
                    if rulePart!=self.EMPTY_STR:#prázdný symbol nemá smysl dávat na zásobník
                        stack.append(Symbol(rulePart, rulePart in self._terminals or rulePart==self.EMPTY_STR))
                    
                rules.append(rule)

        #příjmáme
        return rules
    
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
            
        inputSymbols=self._terminals | {Token.Type.EOF.terminalRepr}

        #inicializace tabulky
        self._table={ n:{t:None for t in inputSymbols} for n in self._nonterminals}
        
        #zjištění pravidla pro daný terminál na vstupu a neterminál na zásobníku
        for r in self._rules:
            for t in inputSymbols:
                if t in self._predict[r]:
                    #t může být nejlevěji derivován
                    if self._table[r.leftSide][t] is not None:
                        #nejednoznačnost, našli jsme více jak jedno vhodné pravidlo
                        raise InvalidGrammarException(Errors.ErrorMessenger.CODE_GRAMMAR_AMBIGUITY,
                                                      Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_GRAMMAR_AMBIGUITY)+"\n\t"+str(self._table[r.leftSide][t])\
                                                      +" predict"+str(self._predict[self._table[r.leftSide][t]])+"\t"+str(r)+" predict"+str(self._predict[r]))
                        
                    self._table[r.leftSide][t]=r
                    
                    
        
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
        self._empty[self.EMPTY_STR]=True
        
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
        Získání "množin" firt (v aktuální gramatice) v podobě dict s množinami 
        prvních terminálů derivovatelných pro daný symbol.
        
        Před zavoláním této metody je nutné zavolat _makeEmptySets!
        """

        self._first={t:set([t]) for t in self._terminals} #terminály mají jako prního samy sebe
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
        self._follow[self._startS]=set([Token.Type.EOF.terminalRepr])
        
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


                
                