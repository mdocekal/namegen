"""
Created on 24. 5. 2019
Modul se třídami (funktory) pro filtrování.

:author:     Martin Dočekal
:contact:    xdocek09@stud.fit.vubtr.cz
"""

from abc import ABC, abstractmethod
from typing import Any, Set

import re
class Filter(ABC):
    """
    Základni funktor pro filtrování
    """

    @abstractmethod
    def __call__(self, o:Any) -> bool:
        """
        Volání filtru
        
        :param o: objekt pro filtrování
        :type o: Any
        :return: True pokud má být objekt o propuštěn filtrem. False pokud má být odfiltrován.
        :rtype: bool
        """
        pass
        
class NamesFilter(Filter):
    """
    Filtruje jména na základě vybraných jazyků a podoby samotného jména.
    """
    
    
    def __init__(self, languages:Set[str], nameRegex:re):
        """
        Inicializace filtru.
        
        :param languages: Povolené jazyky.
        :type languages: Set[str]
        :param nameRegex: Regulární výraz určující množinu všech povolených jmen.
        :type nameRegex:re
        """
        
        self._languages=languages
        self._nameRegex=nameRegex
        
    def __call__(self, o) -> bool:
        """
        Volání filtru
        
        :param o: jméno pro filtrování
        :type o: Name
        :return: True pokud má být jméno o propuštěno filtrem. False pokud má být odfiltrováno.
        :rtype: bool
        """
        
        return (self._languages is None or o.language in self._languages) \
                and (self._nameRegex is None or self._nameRegex.match(str(o)))

        
        