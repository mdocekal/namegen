#!/usr/bin/env python3
# encoding: utf-8
"""
namegen -- Generátor tvarů jmen.

namegen je program pro generování tvarů jmen osob a lokací.

:author:     Martin Dočekal
:contact:    xdocek09@stud.fit.vubtr.cz
"""

import sys
import os
from argparse import ArgumentParser
import traceback
from namegenPack import Errors
from namegenPack.ConfigManager import ConfigManager
import logging
from namegenPack.Grammar import Grammar, Lex

from namegenPack.Name import *

outputFile = sys.stdout



class ArgumentParserError(Exception): pass
class ExceptionsArgumentParser(ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)
    
class ArgumentsManager(object):
    """
    Arguments manager pro namegen.
    """
    
    @classmethod
    def parseArgs(cls):
        """
        Parsování argumentů.
        
        :param cls: arguments class
        :returns: Parsované argumenty.
        """
        
        parser = ExceptionsArgumentParser(description="namegen je program pro generování tvarů jmen osob a lokací.")
        
        parser.add_argument("-o", "--output", help="Výstupní soubor.", type=str, required=True)
        parser.add_argument("-ew", "--error-words", help="Cesta k souboru, kde budou uloženy slova, pro která se nepovedlo získat informace (tvary, slovní druh...).", type=str)
        parser.add_argument('input', nargs=1, help='Vstupní soubor se jmény.')

        try:
            parsed=parser.parse_args()
            
        except ArgumentParserError as e:
            parser.print_help()
            print("\n"+str(e), file=sys.stderr)
            Errors.ErrorMessenger.echoError(Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_INVALID_ARGUMENTS), Errors.ErrorMessenger.CODE_INVALID_ARGUMENTS)

        return parsed
 
def main():
    """
    Vstupní bod programu.
    """
    try:
        
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        #zpracování argumentů
        args=ArgumentsManager.parseArgs()
        
        #načtení konfigurace
        configManager=ConfigManager()
        configAll=configManager.read(os.path.dirname(os.path.realpath(__file__))+'/namegen_config.ini')
        
        #inicializace morphodity (lemmatizace, info o slově)
        Word.initMorphoDita(configAll[configManager.sectionDataFiles]["TAGGER"], configAll[configManager.sectionDataFiles]["DICTIONARY"])
        
        #načtení gramatik
        
        try:
            grammarMale=Grammar.Grammar(configAll[configManager.sectionDataFiles]["GRAMMAR_MALE"])
        except Errors.ExceptionMessageCode as e:
            raise Errors.ExceptionMessageCode(e.code, configAll[configManager.sectionDataFiles]["GRAMMAR_MALE"]+": "+e.message)
        
        try:
            grammarFemale=Grammar.Grammar(configAll[configManager.sectionDataFiles]["GRAMMAR_FEMALE"])
        except Errors.ExceptionMessageCode as e:
            raise Errors.ExceptionMessageCode(e.code, configAll[configManager.sectionDataFiles]["GRAMMAR_FEMALE"]+": "+e.message)
        
        try:
            grammarLocations=Grammar.Grammar(configAll[configManager.sectionDataFiles]["GRAMMAR_LOCATIONS"])
        except Errors.ExceptionMessageCode as e:
            raise Errors.ExceptionMessageCode(e.code, configAll[configManager.sectionDataFiles]["GRAMMAR_PERSONS"]+": "+e.message)

        #načtení jmen pro zpracování
        namesR=NameReader(args.input[0])
        
        
        #čítače chyb
        errorsOthersCnt=0   
        errorsGrammerCnt=0  #není v gramatice
        errorsWordInfoCnt=0   #nemůže vygenrovat tvary, zjistit POS...

        errorWordsShouldSave=True if args.error_words is not None else False
        errorWords=set()    #slova ke, kterým nemůže vygenerovat tvary, zjistit POS... Jedná se o dvojice ( druhu slova ve jméně, dané slovo)
         
        cnt=0   #projito slov
        
        #nastaveni logování
        

        with open(args.output, "w") as outF:
            
            for name in namesR:
                try:
                    
                    #Vybrání a zpracování gramatiky na základě druhu jména.
                    if name.type==Name.Type.LOCATION:
                        rules=grammarLocations.analyse(Lex.getTokens(name))
                    elif name.type==Name.Type.MALE:
                        rules=grammarMale.analyse(Lex.getTokens(name))
                    else:
                        rules=grammarFemale.analyse(Lex.getTokens(name))
  
                    morphs=name.genMorphs(Grammar.Grammar.getMorphMask(rules))
                    
                    print(str(name)+"\t"+str(name.type)+"\t"+("|".join(morphs)), file=outF)
                        
                except (Word.WordException) as e:
                    print(str(name)+"\t"+e.message, file=sys.stderr)
                    errorsWordInfoCnt+=1
    
                    if errorWordsShouldSave:
                        try:
                            for m, w in zip(name.markWords(), name.words):
                                if w==e.word:
                                    errorWords.add((m, e.word))
                        except:
                            #nelze získat informaci o druhu slova ve jméně
                            errorWords.add(("", e.word))
                            pass
                        
                except Grammar.Grammar.NotInLanguage as e:
                    errorsGrammerCnt+=1
                    print(Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_NAME_IS_NOT_IN_LANGUAGE_GENERATED_WITH_GRAMMAR)+\
                              "\t"+str(name)+"\t"+str(name.type)+"\t"+e.message, file=sys.stderr)
                except Grammar.Grammar.UnknownTerminal as e:
                    errorsGrammerCnt+=1
                    print(str(name)+"\t"+e.message, file=sys.stderr)
                except Errors.ExceptionMessageCode as e:
                    #chyba při zpracování slova
                    errorsOthersCnt+=1
                    print(str(name)+"\t"+e.message, file=sys.stderr)
                    
                cnt+=1
                if cnt%100==0:
                    logging.info("Projito slov: "+str(cnt))
                
        
        print("-------------------------")
        print("Celkem jmen: "+ str(namesR.errorCnt+len(namesR.names)))
        print("\tNenačtených jmen: "+ str(namesR.errorCnt))
        print("\tNačtených jmen/názvů celkem: ", len(namesR.names))
        print("\t\tNepokryto gramatikou: ", errorsGrammerCnt)
        print("\t\tNepodařilo se získat informace o slově (tvary, slovní druh...): ", errorsWordInfoCnt)
        
        
        if errorWordsShouldSave:
            #save words with errors into a file
            with open(args.error_words, "w") as errWFile:
                for m, w in errorWords:#označení typu slova ve jméně(jméno, příjmení), společně se jménem
                    try:
                        print(str(w)+"\t"+"j"+str(m)+"\t"+Morphodita.Morphodita.transInfoToLNTRF(w.info), file=errWFile)
                    except Word.WordException:
                        #no info
                        print(str(w), file=errWFile)
        
  

    except Errors.ExceptionMessageCode as e:
        Errors.ErrorMessenger.echoError(e.message, e.code)
    except IOError as e:
        Errors.ErrorMessenger.echoError(Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_COULDNT_WORK_WITH_FILE)+"\n"+str(e), 
                                 Errors.ErrorMessenger.CODE_COULDNT_WORK_WITH_FILE)

    except Exception as e: 
        print("--------------------", file=sys.stderr)
        print("Detail chyby:\n", file=sys.stderr)
        traceback.print_tb(e.__traceback__)
        
        print("--------------------", file=sys.stderr)
        print("Text: ", end='', file=sys.stderr)
        print(e, file=sys.stderr)
        print("--------------------", file=sys.stderr)
        Errors.ErrorMessenger.echoError(Errors.ErrorMessenger.getMessage(Errors.ErrorMessenger.CODE_UNKNOWN_ERROR), Errors.ErrorMessenger.CODE_UNKNOWN_ERROR)

    

if __name__ == "__main__":
    main()
