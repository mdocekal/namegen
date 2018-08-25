# Formát gramatik ZASTARALé
Zde si popíšeme formát souboru s gramatikou.
* První řádek je množina neterminálů oddělených bílým znakem.
* Druhý řádek je množina terminálů oddělených bílým znakem.
* Třetí řádek je startovací symbol.
* Zbytek řádků představuje pravidla. Vždy jedno pravidlo na řádku.
  * Formát pravidla: Neterminál -> Terminály a neterminály odděleny bílým znakem

Množina terminálů a neterminálů musí mít prázdný průnik. Startovací symbol je z množiny neterminálů. Znak ε je vyhrazen pro prázdný řetězec. Předpokládá se LL gramatika.

Pokud je jako 1. znak v neterminálu uveden !, pak se jedná o neohebnou část jména (dědí se dále v derivačním stromu).
Neterminály mohou být zvoleny libovolně. Seznam povolených terminálů je následující:

	N	#podstatné jméno
	A	#přídavné jméno
	P	#zájméno
	C	#číslovka
	V	#sloveso
	D	#příslovce
	R 	#předložka
	J	#spojka
	T	#částice
	I	#citoslovce
	Z	#symbol
	T	#titul
	RN	#římská číslice
	IA	#Iniciálová zkratka.
	X	#neznámé

## Příklad

    S E
    ( ) + i
    S
    S -> E
    E -> ( E + E )
    E -> i
