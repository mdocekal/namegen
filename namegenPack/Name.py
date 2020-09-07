"""
Created on 17. 6. 2018
Modul se třídami pro reprezentaci jména/názvu.

:author:     Martin Dočekal
:contact:    xdocek09@stud.fit.vubtr.cz
"""

import locale
import logging
import sys
from builtins import str
from enum import Enum
from typing import List, Dict, Set, Tuple, Union

import namegenPack.Grammar
from namegenPack import Errors
from namegenPack.Filters import Filter
from namegenPack.Grammar import Terminal, Token
from namegenPack.Language import Language
from namegenPack.Word import Word, WordTypeMark
from namegenPack.morpho import MorphCategories
from namegenPack.morpho.MorphCategories import Case, POS, Note
from namegenPack.morpho.MorphoAnalyzer import MARule


class NameMorph(object):
    """
    Tvar jména pro nějaký pád.
    Lze použít pro výpis pádu daného jména.
    """

    UNKNOWN_ANALYZE_FLAG = "E"

    def __init__(self, forName, wordsMorphs: List[Set[Tuple[str, Union[MARule, None]]]],
                 wordsTypes: List[Tuple[WordTypeMark, bool]]):
        """
        Vytvoření tvaru jména pro dané jméno.

        :param forName: Vytvořený tvar patří k tomuto jménu.
        :type forName:vName
        :param wordsMorphs: Vygenerované tvary slov společně s jejich značko pravidly.
        Slovo může mít i více tvarů pro konkrétní pád, proto máme list množin.
        Pravidla, obsahující značky, budou uvedeny posplu s vygenervanými tvary slov.
        :type wordsMorphs: List[Set[Tuple[str, Union[MARule, None]]]]
        :param wordsTypes: List dvojic s druhy slov ve jméně společně s informací zdali se má
            uvést příznak informující i chybějící analýze.
            Uvádí se u daného tvaru.
            Počet musí být stejný jako počet slov (počet položek v listu morphs).
            Dvojice: (word type, příznak (E)) U příznaku True znamená přidání UNKNOWN_ANALYZE_FLAG. False
            nepřidává nic.
        :type wordsTypes: List[Tuple[WordTypeMark, bool]]
        """

        self.forName = forName
        self.wordsMorphs = wordsMorphs
        self.wordsTypes = wordsTypes

    def __str__(self):
        morph = ""

        for i, (wordMorphs, wordType) in enumerate(zip(self.wordsMorphs, self.wordsTypes)):

            actMorphsTags = ""

            #druh slova jméno, příjmení...
            if wordType[0] != WordTypeMark.UNKNOWN:
                actMorphsTags = "#" + str(wordType[0].value) + (self.UNKNOWN_ANALYZE_FLAG if wordType[1] else "")

            #slovo / možné varianty slova s lntrf značko pravidly a druhem slova
            morph += "/".join(wordMorph +
                              ("[" + morphRule.lntrfWithoutNote + "]" if morphRule is not None else "") +
                              actMorphsTags
                              for wordMorph, morphRule in wordMorphs)

            # přidání oddělovače slov
            if i < len(self.forName.separators):
                putSep = self.forName.separators[i]
                # přidáváme mezeru nulové délky, pokud neni separator
                morph += putSep if len(putSep) > 0 else u'\u200b'



        return morph


class Name(object):
    """
    Reprezentace celého jména osoby či lokace.
    """

    class NameCouldntCreateException(Errors.ExceptionMessageCode):
        """
        Nepodařilo se vytvořit jméno. Deatil ve zprávě
        """
        pass

    class Type(object):
        """
        Přípustné druhy jmen.
        
        Podporuje rozšířené porovnání pomocí ==.
        Mimo klasické rovnosti je možné se ptát i například následujícím způsobem.
        
        Příklad dotazu na MainType:
            Je x lokace?
                x == MainType.LOCATION
        
        Příklad dotazu na pohlaví:
            Je x jméno ženy?
                x== PersonGender.FEMALE
        
        Zjištění zda je druh x plně určen pro výběr vhodné gramatiky (true není):
            x == None
        """

        INDEX_OF_MAIN_TYPE = 0
        INDEX_OF_PERSONS_GENDER = 3

        class MainType(Enum):
            """
            Hlavní druh jména.
            """
            LOCATION = "L"
            EVENTS = "E"
            PERSON = "P"

            def __str__(self):
                return self.value

        class PersonGender(Enum):
            """
            Pohlaví osoby.
            """
            MALE = "M"
            FEMALE = "F"

            def __str__(self):
                return self.value

        def __init__(self, nType):
            """
            Vytvoří druh jména.
            
            :param nType: Druh jména.
                #Formát řetězce pro jména osob:
                #    <Type: P=Person>:<Subtype: F/G=Fictional/Group>:<Future purposes: determine regular name and alias>:<Gender: F/M=Female/Male>
                #    Pokud se bude měnit formát je nutná úprava v metodě Name.guessType.
                #Pro názvy lokací je to jen značka L.
            :type nType: str
            :raise ValueError: Při nevalidnim vstupu.
            """

            self.levels = [x if len(x) > 0 else None for x in nType.split(":")]

            # validace hodnot
            # prozatím validujeme pouze MainType a PersonGender, protože se toho více nepoužívá.
            # Ostatní pouze uchováváme pro pozdější výpis a možnost porovnání jmen.

            self.levels[self.INDEX_OF_MAIN_TYPE] = self.MainType(self.levels[self.INDEX_OF_MAIN_TYPE])
            if self.levels[self.INDEX_OF_MAIN_TYPE] == self.MainType.PERSON:
                # Jedná se o osobu, tak validujeme pohlaví.
                if self.levels[self.INDEX_OF_PERSONS_GENDER] is not None:
                    self.levels[self.INDEX_OF_PERSONS_GENDER] = self.PersonGender(
                        self.levels[self.INDEX_OF_PERSONS_GENDER])

        def __hash__(self):
            """
            Vlastnost, že dva objekty pro které vrací __eq__ true mají stejný hash je splněna pouze
            pro porovnání objektů této třídy a nemusí tedy platit pro rozšířené vyhledávání (viz __eq__).
            """
            return hash(str(self))

        def __eq__(self, other):
            """
            Implementuje i rozšířené porovnání:
            Příklad dotazu na MainType:
                Je x lokace?
                    x == MainType.LOCATION
            
            Příklad dotazu na pohlaví:
                Je x jméno ženy?
                    x== PersonGender.FEMALE
            
            Zjištění zda je druh x plně určen pro výběr vhodné gramatiky (true není):
                x == None
                
            """
            if other is None:
                # Zjištění zda je druh x plně určen pro výběr vhodné gramatiky
                if self.levels[self.INDEX_OF_MAIN_TYPE] == self.MainType.PERSON and \
                        self.levels[self.INDEX_OF_PERSONS_GENDER] == other:
                    # není
                    return True

            if isinstance(other, self.__class__):
                # druhý je také typ
                # klasicky porovnáme
                return str(self) == str(other)

            if isinstance(other, self.MainType):
                # porovnání na úrorvni main type
                if self.levels[self.INDEX_OF_MAIN_TYPE] == other:
                    return True

            if isinstance(other, self.PersonGender):
                # porovnání na úrovni osob
                if self.levels[self.INDEX_OF_MAIN_TYPE] == self.MainType.PERSON and \
                        self.levels[self.INDEX_OF_PERSONS_GENDER] == other:
                    return True

            return False

        def __str__(self):
            return ":".join("" if x is None else str(x) for x in self.levels)

    def __init__(self, name, language: Language, nType, addit=None, wordDatabase=None):
        """
        Konstruktor jména.

        :param name: Řetězec se jménem.
        :type name: String
        :param language: Jazyk tohoto jména.
        :type language: Language
        :param nType: Druh jména.
        :type nType: str
        :param addit: Přídavné info ke jménu
        :type addit: List
        :param wordDatabase: Databáze obsahující již vyskytující se slova v předcházejících jménech.
        :type wordDatabase: Dict[str,Word]
        :raise NameCouldntCreateException: Nelze vytvořit jméno.
        """

        if addit is None:
            addit = []

        if wordDatabase is None:
            wordDatabase = {}

        self._language = language
        self._type = nType
        self.additionalInfo = addit
        try:
            # nejprve převedeme a validujeme druh jména

            # Pokud None a předpokládáme název pro osobu,tak později může být určeno její pohlaví
            # pomocí guessType.
            if self._type is not None:
                self._type = self.Type(nType)
        except ValueError:
            raise self.NameCouldntCreateException(Errors.ErrorMessenger.CODE_INVALID_INPUT_FILE_UNKNOWN_NAME_TYPE,
                                                  Errors.ErrorMessenger.getMessage(
                                                      Errors.ErrorMessenger.CODE_INVALID_INPUT_FILE_UNKNOWN_NAME_TYPE) + "\n\t" + name + "\t" + nType)

        # rozdělíme jméno na jednotlivá slova a oddělovače
        words, self._separators = self._findWords(name)
        self._words = [wordDatabase[w] if w in wordDatabase else Word(w) for w in words]

    def __str__(self):
        n = ""
        i = 0
        for w in self._words:
            n += str(w)
            if i < len(self._separators):
                n += self._separators[i]
            i += 1

        return n

    def __repr__(self):
        return str((str(self), self._language, self._type, self.additionalInfo))

    def __lt__(self, other):
        # porovnání s ohledem na aktuální locale
        return locale.strxfrm(str(self)) < locale.strxfrm(str(other))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return str(self) == str(other) and self._language == other._language and self._type == other._type

        return False

    def __hash__(self):
        return hash(str(self)) ^ hash(self._language) ^ hash(self._type)

    def __len__(self):
        return len(self._words)

    def __iter__(self):
        for w in self._words:
            yield w

    def __getitem__(self, key):
        return self._words[key]

    def index(self, word: Word, all=False):
        """
        Najde pozici, na které se slovo ve jméně nachází.
        Hledá první shodu (od 0), pokud je all=False.

        :param word: Slovo jehož pozici hledáme.
        :type word: Word
        :param all: Pokud je true, pak hledá všechny výskyty.
        :type all: bool
        :return: Index slova ve jméně. Nebo list indexů všech výskytů.
        :rtype: Union[int, List[int]]
        :raise ValueError: Když není slovo přítomno.
        """

        indexesSoFar=[]
        for i, w in enumerate(self):
            if w == word:
                if all:
                    indexesSoFar.append(i)
                else:
                    return i
        if len(indexesSoFar)>0:
            return indexesSoFar
        else:
            raise ValueError("Word {} is not in name {}.".format(word, self))

    def printName(self):
        """
        Převede jméno do string. Pokud má jméno nějaké přídavné informace, tak je také přidá.
        Formát: <jméno>\TAB<jazyk>\TAB<typeflag>\TAB\TAB<url>
        """

        res = str(self)

        res += "\t" + ("Unknown" if self._language is None else self._language.code)

        res += "\t" + str(self._type)

        res += "\t\t"

        if len(self.additionalInfo) > 0:
            res += ("\t".join(self.additionalInfo))

        return res

    def guessType(self, tokens: List[namegenPack.Grammar.Token] = None):
        """
        Provede odhad typu jména. Jedná se o jisté zpochybnění zda-li se jedná o mužské, či ženské jméno.
        Jména lokací a událostí nezpochybňujě.
        Přepíše typ jména pokud si myslí, že je jiný.
        Pokud není typ jména uveden odhadne jej, ovšem pevně předpokládá, že se jedná o jméno osoby.
        (Dle zadání má být automaticky předpokládána osoba, kde se může stát, že typ není uveden.)

        :param tokens: Tokeny odpovídající tomuto jménu. Tento volitelný parametr je zde zaveden pro zrychlení výpočtu, aby nebylo nutné v některých případech
            provádět vícekrát lexikální analýzu. Pokud bude vynechán nic se neděje jen si provede lexikální analýzu sám.
        :type tokens: List[Token]
        :return: Zde vrací analyzované tokeny ( a pravidla), získané při analýze pomocí gramatiky, která generuje jazyk
            v němž je toto jméno. Pokud je jméno ve více gramatikách nebo v žádné vrátí None.
        :rtype aTokens: (List, List) | None
        :raise Word.WordCouldntGetInfoException:Pokud se nepodařilo analyzovat nějaké slovo.
        :raise TimeoutException: Při provádění syntaktické analýzy (pro jednou z gramatik), nad tímto jménem, došlo k timeoutu.
        """
        if self._type != self.Type.MainType.PERSON:
            # zbochybňujeme jen jména a osob
            return
        if not tokens:
            tokens = self.language.lex.getTokens(self)

        # zkusíme zpochybnit typ jména
        changeTo = None
        # najdeme první podstatné nebo přídavné jméno od konce (příjmení)
        # Příjmení jak se zdá může být i přídavné jméno (`Internetová jazyková příručka <http://prirucka.ujc.cas.cz/?id=320#nadpis3>`_.)

        grammars = {Name.Type.PersonGender.FEMALE: self.language.gFemale,
                    Name.Type.PersonGender.MALE: self.language.gMale}
        try:
            for token in reversed(tokens):
                if token.type == namegenPack.Grammar.Token.Type.ANALYZE:
                    # získáme možné mluvnické kategorie
                    analyze = token.word.info
                    posCat = analyze.getAllForCategory(MorphCategories.MorphCategories.POS,
                                                       {Case.NOMINATIVE})  # máme zájem jen o 1. pád
                    if MorphCategories.POS.NOUN in posCat or MorphCategories.POS.ADJECTIVE in posCat:
                        if token.word[-3:] in {"ová", "cká", "ská"}:
                            # muž s přijmení končícím na ová,cká a ská zřejmě není
                            # změníme typ pokud není ženský
                            changeTo = self.Type.PersonGender.FEMALE
                        break
                elif token.type == namegenPack.Grammar.Token.Type.ANALYZE_UNKNOWN:
                    # Máme token, který by potřeboval analýzu, ale analyzátor nezná dané slovo.
                    # Zkusme aspoň bez závislost na slovním druhu (protože ho nezjistíme) otestovat slovo na ženská koncovky.
                    if token.word[-3:] in {"ová", "cká", "ská"}:
                        # muž s přijmení končícím na ová,cká a ská, zřejmě není
                        # změníme typ pokud není ženský
                        changeTo = self.Type.PersonGender.FEMALE
                    break

            # Provedeme odhad na základě gramatik, pokud bude odpovídat právě jedna gramatika, pak ji přířazený typ
            # určuje daný odhad.
            aTokens = None
            rules = None

            if changeTo is None and grammars:
                # příjmení nekončí na ová
                for t, g in grammars.items():
                    try:
                        rules, aTokens = g.analyse(tokens)

                        if changeTo is None:
                            # zatím odpovídá jedna gramatika
                            changeTo = t
                        else:
                            # více než jedna gramatika odpovídá
                            changeTo = None
                            aTokens = None
                            rules = None
                            break

                    except namegenPack.Grammar.Grammar.NotInLanguage:
                        continue

            # Vytvoříme si příznak pro smazání derivací, protože dále klademe další podmínky, které musí být splněny.
            # pokud nebudou smažeme derivace před návratem z funkce.
            cleanDeriv = True

            if changeTo is not None:
                if self._type == None:   #Používáme rozšířené porovnání implementované v Name.__eq__.
                    logging.info("Pro " + str(self) + " přiřazuji " + str(changeTo) + ".")
                    if self._type is None:
                        # Nutné vytvořit celý nový typ.
                        # Formát pro osoby:
                        # <Type: P=Person>:<Subtype: F/G=Fictional/Group>:<Future purposes: determine regular name and alias>:<Gender: F/M=Female/Male>
                        self._type = self.Type("P:::" + str(changeTo))
                    else:
                        # Stačí jen doplnit gender
                        self._type.levels[self.Type.INDEX_OF_PERSONS_GENDER] = changeTo

                    cleanDeriv = False  # tyto derivace chceme použít

                elif self._type.levels[self.Type.INDEX_OF_PERSONS_GENDER] != changeTo and aTokens is not None:
                    # Změníme typ pouze pokud morfologická analýza říká, že daná slova opravdu mohou být G či S.
                    # Tedy například pokud gramatika říká, že dané slovo má být příjmení, tak morfologický analyzátor
                    # musí dané příjmení jako příjmení znát (note=jS).

                    couldNotChange = False  # příznak, že se druh nemůže změnit

                    for actDerivAnalTokens in aTokens:

                        for aT in actDerivAnalTokens:

                            # získejme prvně druh slova ve jméně

                            wordType = aT.matchingTerminal.getAttribute(
                                namegenPack.Grammar.Terminal.Attribute.Type.WORD_TYPE)

                            if wordType.value in {WordTypeMark.GIVEN_NAME, WordTypeMark.SURNAME}:
                                # kontrolujeme jen pro jméno a příjmení

                                if aT.token.type == namegenPack.Grammar.Token.Type.ANALYZE_UNKNOWN:
                                    # budeme provádět změnu jen v případech, kdy máme pro všechna zkoumaná slova potřebnou analýzyu
                                    couldNotChange = True
                                    break

                                # podmínky na slovo, které budou použity při generování tvarů
                                # použijeme
                                conditionWord = aT.morphCategories

                                # zjistíme jaké máme poznámky
                                notes = aT.token.word.info.getAllForCategory(MorphCategories.MorphCategories.NOTE,
                                                                             conditionWord)


                                if (Note.GIVEN_NAME if wordType.value == WordTypeMark.GIVEN_NAME else Note.SURNAME) not in notes:
                                    # nemáme přislušnou poznámku v morfologické analýze nemůžeme tedy druh změnit
                                    couldNotChange = True
                                    break
                        if couldNotChange:
                            break

                    if not couldNotChange:
                        logging.info("Pro " + str(self) + " měním " + str(
                            self._type.levels[self.Type.INDEX_OF_PERSONS_GENDER]) + " na " + str(changeTo) + ".")
                        self._type.levels[self.Type.INDEX_OF_PERSONS_GENDER] = changeTo
                        cleanDeriv = False  # tyto derivace chceme použít

        except Word.WordCouldntGetInfoException:
            # nepovedlo se získat informace o slově
            # končíme
            return

        if cleanDeriv:
            rules = None
            aTokens = None

        return rules, aTokens

    @property
    def words(self):
        """
        Slova tvořící jméno.

        @return: Slova ve jméně
        @rtype: List[Word]
        """

        return self._words

    @words.setter
    def words(self, newWords:List[Word]):
        """
        Přiřadí nové slova do jména.
        Používat obezřetně. Dojde opravdu jen k náhradě slov, sepárotory zůstavají.

        :param newWords: Nová slova ve jméně.
        :type newWords:List[Word]
        """

        self._words=newWords

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

        words = []
        separators = []

        actWord = ""
        actSeparator = ""
        separatorOccured = False

        parsingNumeric = False  # Chceme i rozdělovat slova jako: 1.díl (Jako např. v názvu Škarez 1.díl )

        # Procházíme jméno a hledáme slova s jejich oddělovači.
        # Vynacháváme oddělovače na konci a začátku.
        for c in name:
            if c.isspace() or c == '-' or c == '–' or c == ',':
                # separátor

                if len(actWord) > 0:
                    # počáteční vynecháváme
                    actSeparator += c
                    separatorOccured = True

                parsingNumeric = False  # budeme delit tak, ci tak
            else:
                # znak slova

                if c.isnumeric():
                    # slovo obsahuje cislici, budeme chtit pripadne delit
                    # a pokud mame co, tak budeme delit jiz hned
                    if len(actWord) > 0 and not parsingNumeric:
                        # pred cislici byly nejake znaky (ne cislice)
                        separatorOccured = True

                    parsingNumeric = True
                elif parsingNumeric and c != ".":
                    # budeme delit
                    separatorOccured = True
                    parsingNumeric = False

                if separatorOccured:
                    # již se má načítat další slovo
                    # uložíme to staré a příslušný separátor
                    words.append(actWord)
                    actWord = ""

                    separators.append(actSeparator)
                    actSeparator = ""
                    separatorOccured = False

                actWord += c

        if len(actWord) > 0:
            words.append(actWord)

        return words, separators

    def simpleWordsTypesGuess(self, tokens: List[namegenPack.Grammar.Token] = None):
        """
        Provede zjednodušený odhad typů slov ve jméně.

        :param tokens: Tokeny odpovídající tomuto jménu. Tento volitelný parametr je zde zaveden pro zrychlení výpočtu, aby nebylo nutné v některých případech
            provádět vícekrát lexikální analýzu. Pokud bude vynechán nic se neděje jen si provede lexikální analýzu sám.
        :type tokens: List[Token]
        :return: Typy pro slova ve jméně.
        :rtype: List(namegenPack.Word.WordTypeMark)
        """

        if not tokens:
            tokens = self.language.lex.getTokens(self)

        types = []
        logging.info(str(self) + "\tPoužívám zjednodušené určování druhu slov.")
        # používá se u mužských/ženských jmen, kde za předložkou dáváme lokaci
        womanManType = namegenPack.Word.WordTypeMark.GIVEN_NAME

        lastGivenName = None  # uchováváme si index posledního křestních jmen pro pozdější změnu na příjmení

        for token in tokens:
            if token.type == namegenPack.Grammar.Token.Type.ANALYZE or token.type == namegenPack.Grammar.Token.Type.ANALYZE_UNKNOWN:
                if self._type == self.Type.MainType.LOCATION:
                    types.append(namegenPack.Word.WordTypeMark.LOCATION)
                else:
                    try:

                        pos = token.word.info.getAllForCategory(MorphCategories.MorphCategories.POS)
                        if len({POS.PREPOSITION, POS.PREPOSITION_M} & pos) > 0:
                            # jedná se o předložku
                            types.append(namegenPack.Word.WordTypeMark.PREPOSITION)
                            logging.info("\t" + str(token.word) + "\t" + str(
                                namegenPack.Word.WordTypeMark.PREPOSITION) + "\tNa základě morfologické analýzy.")
                            # přepneme z křestního na lokaci
                            womanManType = namegenPack.Word.WordTypeMark.LOCATION
                        else:
                            if womanManType == namegenPack.Word.WordTypeMark.LOCATION:
                                logging.info("\t" + str(token.word) + "\t" + str(
                                    womanManType) + "\tSlovo se nachází za předložkou.")
                            else:
                                lastGivenName = len(types)
                            types.append(womanManType)

                    except Word.WordCouldntGetInfoException:
                        if womanManType != namegenPack.Word.WordTypeMark.LOCATION:
                            lastGivenName = len(types)
                        types.append(womanManType)
            elif token.type == namegenPack.Grammar.Token.Type.INITIAL_ABBREVIATION:
                logging.info("\t" + str(token.word) + "\t" + str(
                    namegenPack.Word.WordTypeMark.INITIAL_ABBREVIATION) + "\tNa základě lexikální analýzy.")
                types.append(namegenPack.Word.WordTypeMark.INITIAL_ABBREVIATION)
            elif token.type == namegenPack.Grammar.Token.Type.ROMAN_NUMBER:
                if self._type != self.Type.MainType.LOCATION:
                    # může být i předložka v, kvůli stejné reprezentaci s římskou číslicí 5
                    if str(token.word) == "v":
                        # jedná se o malé v bez tečky, bereme jako předložku
                        logging.info("\t" + str(token.word) + "\t" + str(
                            namegenPack.Word.WordTypeMark.PREPOSITION) + "\tJedná se o malé v bez tečky.")
                        types.append(namegenPack.Word.WordTypeMark.PREPOSITION)
                        # přepneme z křestního na lokaci
                        womanManType = namegenPack.Word.WordTypeMark.LOCATION
                    else:
                        logging.info("\t" + str(token.word) + "\t" + str(
                            namegenPack.Word.WordTypeMark.ROMAN_NUMBER) + "\tNa základě lexikální analýzy.")
                        types.append(namegenPack.Word.WordTypeMark.ROMAN_NUMBER)
                else:
                    types.append(namegenPack.Word.WordTypeMark.ROMAN_NUMBER)
            elif token.type == namegenPack.Grammar.Token.Type.DEGREE_TITLE:
                logging.info("\t" + str(token.word) + "\t" + str(
                    namegenPack.Word.WordTypeMark.DEGREE_TITLE) + "\tNa základě lexikální analýzy.")
                types.append(namegenPack.Word.WordTypeMark.DEGREE_TITLE)
            else:
                if token.word is not None:
                    logging.info("\t" + str(token.word) + "\t" + str(namegenPack.Word.WordTypeMark.UNKNOWN))
                types.append(namegenPack.Word.WordTypeMark.UNKNOWN)

        firstGivenName = True
        for i in range(len(types)):
            if not firstGivenName and i == lastGivenName:
                # poslední křestní se stane příjmením
                # pokud není zároveň prvním
                logging.info("\t" + str(tokens[i].word) + "\t" + str(
                    namegenPack.Word.WordTypeMark.SURNAME) + "\tPoslední doposud neurčené slovo.")
                types[i] = namegenPack.Word.WordTypeMark.SURNAME
                break
            if types[i] == namegenPack.Word.WordTypeMark.GIVEN_NAME:

                if (self._type == self.Type.PersonGender.FEMALE or self._type == None) and self._words[i][-3:] == "ová":
                    logging.info("\t" + str(tokens[i].word) + "\t" + str(
                        namegenPack.Word.WordTypeMark.SURNAME) + "\tJedná se o ženské jméno(či neznámého druhu) a slovo končí na ová.")
                    types[i] = namegenPack.Word.WordTypeMark.SURNAME
                else:
                    logging.info("\t" + str(tokens[i].word) + "\t" + str(types[i]) + "\tVýchozí druh slova.")

                firstGivenName = False

        return types

    def genMorphs(self, analyzedTokens: List[namegenPack.Grammar.AnalyzedToken],
                  missingCaseToken: Set[Tuple[namegenPack.Grammar.AnalyzedToken, Case]] = None):
        """
        Na základě slovům odpovídajících analyzovaných tokenů ve jméně vygeneruje tvary jména.
        Pokusí se vygenerovat všech sedm pádů, pokud nebude možné nějaké vygenerovat vrátí alespoň ty, které
        se mu vygenerovat povedly.

        :param analyzedTokens: Analyzované tokeny, získané ze syntaktické analýzy tohoto jména.
        :type analyzedTokens: List[namegenPack.Grammar.AnalyzedToken]
        :param missingCaseToken: Volitelný atribut, který lze použít pro získání tokenú/slov, u kterých se nepodařilo
            získat tvar v nějakém z pádů.
        :type missingCaseToken: Set[Tuple[AnalyzedToken, Case]]
        :return:  Vygenerované tvary pro každý pád. Seřazeno od 1. pádu do 7..
        :rtype: List[NameMorph]
        :raise Word.WordNoMorphsException: Pokud se nepodaří získat tvary u nějakého slova.
        :raise WordCouldntGetInfoException: Vyjímka symbolizující, že se nepovedlo získat mluvnické kategorie ke slovu.
        """

        # získáme tvary jednotlivých slov
        genMorphsForWords = []
        for word, aToken in zip(self._words, analyzedTokens):
            if aToken.morph:
                cateWord = aToken.morphCategories  # podmínky na původní slovo

                cateMorph = set()  # podmínky přímo na tvary
                # překopírujeme a ignorujeme pády, jelikož nemůžeme vybrat jen jeden, když chceme
                # generovat všechny
                for x in cateWord:
                    if x.category() != MorphCategories.MorphCategories.CASE:
                        cateMorph.add(x)

                # ještě získáme flagy, pro filtraci
                groupFlags = aToken.matchingTerminal.getAttribute(Terminal.Attribute.Type.FLAGS)
                groupFlags = set() if groupFlags is None else groupFlags.value

                genMorphsForWords.append(word.morphs(cateMorph, cateWord, groupFlags))

            else:
                genMorphsForWords.append(None)

        # z tvarů slov poskládáme tvary jména
        # Set[Tuple[MARule,str]]
        morphs = []

        for c in [Case.NOMINATIVE, Case.GENITIVE, Case.DATIVE, Case.ACCUSATIVE, Case.VOCATIVE, Case.LOCATIVE,
                  Case.INSTRUMENTAL]:  # pády
            wordsTypes=[]
            wordsWithRules=[]
            for i, (word, aToken) in enumerate(zip(self._words, analyzedTokens)):

                if aToken.morph and isinstance(genMorphsForWords[i], set):
                    # ohýbáme

                    morphsThatWeAlreadyHaves = set()

                    morphsWithRules=set()

                    for maRule, wordMorph in genMorphsForWords[i]:
                        # najdeme tvar slova pro daný pád
                        try:
                            if maRule[MorphCategories.MorphCategories.CASE] == c:
                                actMorph = wordMorph + "[" + maRule.lntrfWithoutNote + "]"

                                if actMorph in morphsThatWeAlreadyHaves:
                                    # Díky tomu, že nezohledňujeme poznámku při výpisu,
                                    # tak můžeme dostávat tvary, které vypadají totožně a není
                                    # nutné je tedy vypisovat.
                                    continue

                                morphsThatWeAlreadyHaves.add(actMorph)
                                morphsWithRules.add((wordMorph, maRule))


                        except KeyError:
                            # pravděpodobně nemá pád vůbec
                            pass

                    if len(morphsWithRules)==0:
                        # nepovedlo se získat aktuální pád pro aktuální slovo
                        if missingCaseToken is not None:
                            missingCaseToken.add((aToken, c))
                    else:
                        wordsWithRules.append(morphsWithRules)
                        wordsTypes.append((aToken.matchingTerminal.getAttribute(
                            namegenPack.Grammar.Terminal.Attribute.Type.WORD_TYPE).value, False))
                else:
                    # neohýbáme
                    wordsWithRules.append({(str(word), None)})
                    wordsTypes.append((aToken.matchingTerminal.getAttribute(
                        namegenPack.Grammar.Terminal.Attribute.Type.WORD_TYPE).value,
                               aToken.token.type == Token.Type.ANALYZE_UNKNOWN))

            if len(wordsWithRules) > 0:
                morphs.append(NameMorph(self, wordsWithRules, wordsTypes))

        return morphs

    @staticmethod
    def getWordsOfType(wordType: WordTypeMark, analyzedTokens: List[namegenPack.Grammar.AnalyzedToken]):
        """
        Na základě slovům odpovídajících analyzovaných tokenů ve jméně vybere slova daného typu.

        :param wordType: Druh slova na základě, kterého vybírá
        :type wordType: WordTypeMark
        :param analyzedTokens: Analyzované tokeny, získané ze syntaktické analýzy tohoto jména.
        :type analyzedTokens: List[namegenPack.Grammar.AnalyzedToken]
        :return: List s vybranými slovy a příslušnými značko pravidly.
        :rtype: List[Tuple[Word, Set[MARule]]]
        """
        selection = []
        for aToken in analyzedTokens:
            if aToken.matchingTerminal.getAttribute(
                    namegenPack.Grammar.Terminal.Attribute.Type.WORD_TYPE).value == wordType:
                # získáme příslušná pravidla

                cateFilters = aToken.morphCategories  # podmínky na původní slovo

                rules = {r for r, w in aToken.token.word.morphs(cateFilters, cateFilters) if
                         str(w) == str(aToken.token.word)}
                selection.append((aToken.token.word, {r for r in rules}))

        return selection

    @property
    def type(self):
        """Getter pro druh jména."""
        return self._type

    @property
    def language(self):
        """Getter pro jazyk jména."""
        return self._language


class NameReader(object):
    """
    Třída pro čtení vstupního souboru a převedení vstupu do posloupnosti objektů Name.

    """

    def __init__(self, languages: Dict[str, Language], langDef: str, inputFile=None, shouldSort:bool=True):
        """
        Konstruktor

        :param languages: All suported languages.
        :type languages: Dict[str, Language]
        :param langDef: The default language for unknown.
        :type langDef: str
        :param inputFile: Cesta ke vstupnímu souboru se jmény.
            Pokud je None čte z stdin
        :type inputFile: string | None
        :param shouldSort: Příznak zda si má po přečtení uložit jména v sežazeném pořadí vzestupně.
        :type shouldSort: bool
        """
        self.names = []
        self._errorCnt = 0  # počet chybných nenačtených jmen

        if inputFile is None:
            self._readInput(sys.stdin, languages, langDef)
        else:
            with open(inputFile, "r") as rInput:
                self._readInput(rInput, languages, langDef)

        if shouldSort:
            self.names = sorted(self.names)

    def _readInput(self, rInput, languages: Dict[str, Language], langDef: str):
        """
        Čtení vstupu.

        :param rInput: Vstup
        :param languages: All suported languages.
        :param langDef: The default language for unknown.
        """

        wordDatabase = {}  # zde budeme ukládat již vyskytující se slova
        for line in rInput:
            line = line.strip()
            parts = line.split("\t")  # <jméno>\TAB<jazyk>\TAB<typeflag>\TAB<url>

            if len(parts) < 3:
                # nevalidní formát vstupu
                print(Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_INVALID_NAME) + "\t" + line,
                      file=sys.stderr)
                self._errorCnt += 1
                continue
            try:
                additInfo = []  # přídavné info, například URL odkaď název/jméno pochází
                if len(parts) > 3:
                    additInfo = parts[3:]
                # Přidáváme wordDatabase pro ušetření paměti
                # <jméno>\TAB<jazyk>\TAB<typeflag>\TAB<url>

                lang = langDef if parts[1] == "" else parts[1]

                try:
                    lang = languages[lang]
                except KeyError:
                    lang = None

                self.names.append(Name(parts[0], lang, parts[2], additInfo, wordDatabase))
            except Name.NameCouldntCreateException as e:
                # problém při vytváření jména
                print(e.message, file=sys.stderr)
                self._errorCnt += 1

    @property
    def errorCnt(self):
        """
        Počet chybných nenačtených jmen
        """
        return self._errorCnt

    def allWords(self, stringRep=False, alnumCheck=False, but: Filter = None):
        """
        Slova vyskytující se ve všech jménech.

        :param stringRep: True v str reprezentaci. False jako Word objekt.
        :type stringRep: bool
        :param alnumCheck: Vybere jen ta slova, která obsahují aspoň jeden alfanumerický znak.
        :type alnumCheck: bool
        :param but: Volitelně je možné přidat filtr jmen jejichž slova nemají být použita.
        :type but: Filter
        :return Množina všech slov ve jménech.
        :rtype: Set[Word] | Set[str]
        """
        words = set()

        filteredNames = self.names

        if but is not None:
            filteredNames = filter(but, filteredNames)

        if stringRep:
            if alnumCheck:
                for name in filteredNames:
                    for w in name:
                        st = str(w)
                        if any(s.isalnum() for s in st):
                            words.add(st)
            else:
                for name in filteredNames:
                    for w in name:
                        words.add(str(w))
        else:
            if alnumCheck:
                for name in filteredNames:
                    for w in name:
                        if any(s.isalnum() for s in str(w)):
                            words.add(w)
            else:
                for name in filteredNames:
                    for w in name:
                        words.add(w)
        return words

    def __iter__(self):
        """
        Iterace přes všechna jména. V seřazeném pořadí.
        """
        return iter(self.names)

