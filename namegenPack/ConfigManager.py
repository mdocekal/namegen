"""
Created on 7. 6. 2018
Modul pro zpracování konfigurace pro namgen.py

:author:     Martin Dočekal
:contact:    xdocek09@stud.fit.vubtr.cz
"""

import configparser
from namegenPack import Errors
import os

class ConfigManagerInvalidException(Errors.ExceptionMessageCode):
    """
    Nevalidní konfigurace
    """
    pass

class ConfigManager(object):
    """
    Tato třída slouží pro načítání konfigurace z konfiguračního souboru.
    """

    sectionDataFiles="DATA_FILES"
    
    
    
    
    def __init__(self):
        """
        Inicializace config manažéru.
        """
        
        self.configParser = configparser.ConfigParser()
    
        
    def read(self, filesPaths):
        """
        Přečte hodnoty z konfiguračních souborů. Také je validuje a převede do jejich datových typů.
        
        :param filesPaths: list s cestami ke konfiguračním souborům.
        :returns: Konfigurace.
        :raise ConfigManagerInvalidException: Pokud je konfigurační soubor nevalidní.
        """
        try:
            self.configParser.read(filesPaths)
        except configparser.ParsingError as e:
            raise ConfigManagerInvalidException(Errors.ErrorMessenger.CODE_INVALID_CONFIG, "Nevalidní konfigurační soubor: "+str(e))
                                       
        
        return self.__transformVals()
        
        
    def __transformVals(self):
        """
        Převede hodnoty a validuje je.
        
        :returns: dict -- ve formátu jméno sekce jako klíč a k němu dict s hodnotami.
        :raise ConfigManagerInvalidException: Pokud je konfigurační soubor nevalidní.
        """
        result={}

        result[self.sectionDataFiles]=self.__transformDataFiles()
        
        return result
    
    def __transformDataFiles(self):
        """
        Převede hodnoty pro DATA_FILES a validuje je.
        
        :returns: dict -- ve formátu jméno prametru jako klíč a k němu hodnota parametru
        :raise ConfigManagerInvalidException: Pokud je konfigurační soubor nevalidní.
        """
       
        par=self.configParser[self.sectionDataFiles]
        result={
            "TAGGER":None,
            "DICTIONARY":None,
            "GRAMMAR_MALE":None,
            "GRAMMAR_FEMALE":None,
            "GRAMMAR_LOCATIONS":None
            }
        
        for k in result.keys():
            if par[k]: 
                if par[k][0]!="/":
                    result[k]=os.path.dirname(os.path.realpath(__file__))+"/"+par[k]
                else:
                    result[k]=par[k]
            else:
                raise ConfigManagerInvalidException(Errors.ErrorMessenger.CODE_INVALID_CONFIG, "Nevalidní konfigurační soubor. Chybí "+self.sectionDataFiles+" -> "+k)
    
        return result

