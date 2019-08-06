# namegen
Program pro generování tvarů jmen osob, lokací a událostí.

### Ukázka funkce

**vstup**

    Leonardo da Vinci		P:::M	https://cs.wikipedia.org/wiki/Leonardo_da_Vinci

**výstup**

    Leonardo da Vinci		P:::M	Leonardo[k1gMnSc1]#G da#7 Vinci#L|Leonarda[k1gMnSc2]#G da#7 Vinci#L|Leonardu[k1gMnSc3]#G/Leonardovi[k1gMnSc3]#G da#7 Vinci#L|Leonarda[k1gMnSc4]#G da#7 Vinci#L|Leonardo[k1gMnSc5]#G da#7 Vinci#L|Leonardu[k1gMnSc6]#G/Leonardovi[k1gMnSc6]#G da#7 Vinci#L|Leonardem[k1gMnSc7]#G da#7 Vinci#L	https://cs.wikipedia.org/wiki/Leonardo_da_Vinci
    Leonardo da Vinci		P:::M	Leonardo[k1gMnSc1]#G da#S Vinci[k1gMnSc1]#S|Leonarda[k1gMnSc2]#G da#S Vinciho[k1gMnSc2]#S|Leonardu[k1gMnSc3]#G/Leonardovi[k1gMnSc3]#G da#S Vincimu[k1gMnSc3]#S|Leonarda[k1gMnSc4]#G da#S Vinciho[k1gMnSc4]#S|Leonardo[k1gMnSc5]#G da#S Vinci[k1gMnSc5]#S|Leonardu[k1gMnSc6]#G/Leonardovi[k1gMnSc6]#G da#S Vincim[k1gMnSc6]#S|Leonardem[k1gMnSc7]#G da#S Vincim[k1gMnSc7]#S	https://cs.wikipedia.org/wiki/Leonardo_da_Vinci


## Závislosti

Je nutné mít k dispozici Morfologický analyzátor pro češtinu ( [MA - odkaz na interní wiki](http://knot.fit.vutbr.cz/wiki/index.php/Morfologick%C3%BD_slovn%C3%Adk_a_morfologick%C3%BD_analyz%C3%A1tor_pro_%C4%8De%C5%A1tinu#Morfologick.C3.BD_analyz.C3.A1tor_pro_.C4.8De.C5.A1tinu) ). 

Cestu k analyzátoru (příkaz ke spuštění) lze nastavovat v konfiguračním souboru v sekci MA položka PATH_TO. 

Další závislosti jsou uvedeny v souboru **requirements.txt**.

## Nápověda
Nápovědu lze vyvolat zadáním:

	./namegen.py -h


## Formát vstupu
Formát vstupního souboru je následující:

	<název>\t<jazyk>\t<druh>\t<URLs>
	
### Jazyk

Tento sloupec má význam pro filtrování. V konfiguračním souboru ([více](#config)) je možné si nastavit filtr na základě jazyka. Jedná se o pole LANGUAGES v sekci FILTERS. Pokud není jazyk uveden (sloupec je prázdný) rozumí se jako neznámí (UNKNOWN). Více informací k filtrování lze nalézt přímo v konfiguračním souboru.

Příklad označení jména jako českého:

    Leonardo da Vinci	cs	P:::M	https://cs.wikipedia.org/wiki/Leonardo_da_Vinci

### Druh

**Jméno osoby:**

    <Type: P=Person>:<Subtype: F/G=Fictional/Group>:<Future purposes: determine regular name and alias>:<Gender: F/M=Female/Male>

Příklad pro mužské jméno:

    Leonardo da Vinci		P:::M	https://cs.wikipedia.org/wiki/Leonardo_da_Vinci

Příklad pro ženské jméno:

    Ada Lovelaceová		P:::F	https://cs.wikipedia.org/wiki/Ada_Lovelace

**Název lokace:**

    L
    
Příklad:

    Velké Meziříčí		L	https://cs.wikipedia.org/wiki/Velké_Meziříčí


Také je možné druh vynechat. V tom případe namegen předpokládá, že se jedná o jméno osoby a odhadne, zda-li jde o ženské, či mužské.
	
**Název události:**

Je připravena i podpora pro události. Spíše budoucí užití. Gramatika je v raném stadiu. Je použita gramatika vycházející z lokací.

	E
	
Příklad:

    Bitva na Bílé hoře	cs	E	https://cs.wikipedia.org/wiki/Bitva_na_B%C3%ADl%C3%A9_ho%C5%99e
	
### URLs

Jedná se pouze o dodatečná data, které namegen pouze propouští na výstup.

## Formát výstupu
Formát vstupního souboru je následující:

	<název>\t<jazyk>\t<druh>\t<tvary>\t<URLs>
	
Kde sloupce jsou stejné jako na vstupu až na sloupec obsahující tvary, který může vypadat například takto:

    Leonardo[k1gMnSc1]#G da#7 Vinci#L|Leonarda[k1gMnSc2]#G da#7 Vinci#L|Leonardu[k1gMnSc3]#G/Leonardovi[k1gMnSc3]#G da#7 Vinci#L|Leonarda[k1gMnSc4]#G da#7 Vinci#L|Leonardo[k1gMnSc5]#G da#7 Vinci#L|Leonardu[k1gMnSc6]#G/Leonardovi[k1gMnSc6]#G da#7 Vinci#L|Leonardem[k1gMnSc7]#G da#7 Vinci#L
    
Jednotlivé podoby jména/názvu jsou odděleny pomocí | s tím, že prvně je uvedena podoba pro 1. pád a dále podoba pro 2. pád a tak dále.

Pomocí parametru **--whole**, lze nastavit, že chceme vypisovat tvary, pouze pokud jsme schopni vypsat všechny pády. 

Nyní si rozeberme formát podoby jména pro jeden pád. Máme zde vždy jednotlivá slova oddělená původními oddělovači, kdy každé jednotlivé slovo je následováno značkami (uzavřenými v hranatých závorkách) popisujícími dané slovo. Za znakem # je označen druh slova. Možné druhy slov jsou popsány v:

	data/grammars/README.md

Toto README obsahuje mimo jiné i informace, které lze vztáhnout ke značkám v hranatých závorkách. Je zde totiž uveden popis terminálů (více o terminálech v *data/grammars/README.md*), které používají obdobná značení. Například terminál
	
	1{t=G,c=1,n=S,g=M}

by mohl odpovídat:
	
	[k1gMnSc1]#G

## Příklad
Chceme vygenerovat tvary jmen uložených v souboru example.txt a výsledek uložit do souboru gen.txt:

	./namegen.py -o gen.txt example.txt 
	
## Složka data

Složka

	data

obsahuje soubor s výčtem slov, které se mají identifikovat jako tituly (Bc., Mgr., …)

	data/titles.txt

Více informací o titulech lze získat v:

	data/README.md

Dále tato složka obsahuje podsložku s gramatikami. Více informací o gramatikách lze nalézt v následující [sekci](#grammars).

### <a name="grammars">Gramatiky</a>

Pro generování tvarů jmen používá namegen gramatik, které jsou uloženy v:

	data/grammars

Z těchto gramatik například určuje části jména/názvu, které se mají ohýbat.
Více informací ke gramatikám lze získat ve zmiňované složce v souboru README.md.

Jaká z gramatik bude na konkrétní jméno použita je určeno dle druhu jména/názvu a mapování

	druh -> soubor s gramatikou
	
je uvedeno v konfiguračním souboru.
	
## <a name="config">Konfigurační soubor</a>

Konfigurační soubor se nachází přímo v kořenovém adresáři a jeho název je:

	namegen_config.ini
	
Konfigurační soubor obsahuje i popis jednotlivých parametrů.