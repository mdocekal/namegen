"""
Created on 7. 6. 2018
Modul zastřešující chybové zprávy, kódy a práci s nimi.

:author:     Martin Dočekal
:contact:    xdocek09@stud.fit.vubtr.cz
"""

import sys

class ExceptionMessageCode(Exception):
    """
    Vyjímka se zprávou a kódem.
    """
    def __init__(self, code, message=None):
        """
        Konstruktor pro vyjímku se zprávou a kódem.
        
        :param code: Kód chyby. Pokud je uveden pouze kód, pak se zpráva automaticky na základě něj doplní.
        :param message: zpráva popisující chybu
        """
        self.message = message if message is not None else ErrorMessenger.getMessage(code)
        self.code = code
        
        

class ErrorMessenger(object):
    """
    Obstarává chybové kódy a příslušné zprávy k těmto kódům.
    Píše zprávy do stderr a ukončuje skript s daným chybovým kódem.
    """

    CODE_ALL_OK=0;
    CODE_INVALID_ARGUMENTS=1
    CODE_COULDNT_WORK_WITH_FILE=2
    CODE_COULDNT_READ_INPUT_FILE=3
    CODE_INVALID_INPUT_FILE=4
    CODE_INVALID_INPUT_FILE_UNKNOWN_NAME_TYPE=5
    CODE_NO_DATA=6
    CODE_WORD_ANALYZE=7
    CODE_INVALID_CONFIG=8
    CODE_GRAMMAR_EMPTY_SET_OF_NONTERMINALS=9
    CODE_GRAMMAR_EMPTY_SET_OF_TERMINALS=10
    CODE_GRAMMAR_NO_START_SYMBOL=11
    CODE_GRAMMAR_NO_RULES=12
    CODE_GRAMMAR_INVALID_FILE=13
    CODE_GRAMMAR_EPSILON_IN_TERM_OR_NONTERM=14
    CODE_GRAMMAR_AMBIGUITY=15
    CODE_GRAMMAR_START_SYMBOL=16
    CODE_GRAMMAR_SETS_TERM_NONTERM_NON_DIS=17
    CODE_INVALID_NAME=18
    CODE_WORD_NO_MORPHS_GENERATED=19
    CODE_NAME_IS_NOT_IN_LANGUAGE_GENERATED_WITH_GRAMMAR=20
    CODE_WORD_MISSING_MORF_FOR_CASE=21
    CODE_GRAMMAR_UNKNOWN_TERMINAL=22
    CODE_GRAMMAR_NOT_IN_LANGUAGE=23
    CODE_MA_FAILURE=24
    
    
    CODE_UNKNOWN_ERROR=100

    """
    Obsahuje chybové zpráva. Indexy korespondují s chybovými kódy.
    """
    __ERROR_MESSAGES={
            CODE_ALL_OK:"Vše v pořádku.",
            CODE_INVALID_ARGUMENTS:"Nevalidní argumenty.",
            CODE_COULDNT_WORK_WITH_FILE: "Nemohu pracovat se souborem.",
            CODE_COULDNT_READ_INPUT_FILE:"Nemohu číst vstupní soubor.",
            CODE_INVALID_INPUT_FILE:"Nevalidní vstupní soubor.",
            CODE_INVALID_INPUT_FILE_UNKNOWN_NAME_TYPE:"Nevalidní vstupní soubor. Neznámý druh jména.",
            CODE_WORD_ANALYZE:"Nepodařilo se analyzovat slovo.",
            CODE_INVALID_CONFIG:"Nevalidní hodnota v konfiguračním souboru.",
            CODE_GRAMMAR_EMPTY_SET_OF_NONTERMINALS:"Prázdná množina neterminálů.",
            CODE_GRAMMAR_EMPTY_SET_OF_TERMINALS:"Prázdná množina terminálů.",
            CODE_GRAMMAR_NO_START_SYMBOL:"Není uveden startovací symbol.",
            CODE_GRAMMAR_NO_RULES:"Nejsou uvedena pravidla.",
            CODE_GRAMMAR_INVALID_FILE:"Nevalidní soubor s gramatikou.",
            CODE_GRAMMAR_EPSILON_IN_TERM_OR_NONTERM:"Gramatiky nesmí obsahovat ε v množině terminálů či neterminálů.",
            CODE_GRAMMAR_AMBIGUITY:"Nejednoznačnost v gramatice.",
            CODE_GRAMMAR_START_SYMBOL:"Startovací symbol není v množině neterminálů.",
            CODE_GRAMMAR_SETS_TERM_NONTERM_NON_DIS:"Množina terminálů a neterminálů má neprázdný průnik.",
            CODE_INVALID_NAME:"Nevalidní jméno.",
            CODE_WORD_NO_MORPHS_GENERATED:"Pro slovo se nepodařilo vygenerovat tvary.",
            CODE_NAME_IS_NOT_IN_LANGUAGE_GENERATED_WITH_GRAMMAR:"Název není v jazyce generovaným poskytnutou gramatikou.",
            CODE_WORD_MISSING_MORF_FOR_CASE:"Nepovedlo se vygenerovat tvar pro pád.",
            CODE_GRAMMAR_UNKNOWN_TERMINAL:"Neznámý terminál.",
            CODE_GRAMMAR_NOT_IN_LANGUAGE:"Selhání na příslušnosti do jazyka při: {} na zásobníku a {} na vstupu. Použitá pravidla: {}",
            CODE_MA_FAILURE:"Morfologický analyzátor selhal.",
            
            CODE_UNKNOWN_ERROR:"Neznámá chyba."  ,
    }

    @staticmethod
    def echoError(message, code):
        """
        Vypíše chybovou zprávu do stderr a ukončí skript s poskytnutým kódem.

        :param message: Text chybové zprávy.
        :param code: ukončující kód
        """
        print(message, file=sys.stderr)
        sys.exit(code);
        

    @classmethod
    def getMessage(cls, code):
        """
        Getter pro chybovou zprávu, která odpovídá danému chybovému kódu.

        :param cls: Class
        :param code: Chybový kód.
        :return: Chybová zpráva.
        """
        return cls.__ERROR_MESSAGES[code];
