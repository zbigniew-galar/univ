#### Analiza ABC w Excelu
##### Definicje
**Definicja analizy Pareto:**
Analiza Pareto ustala priorytety działań na podstawie założenia, że około 80 procent problemów wynika zazwyczaj z 20 procent możliwych przyczyn. Oznacza to, że nie wszystkie możliwe przyczyny problemów są równie ważne. Analiza Pareto identyfikuje najbardziej krytyczne (najczęstsze) przyczyny problemów, dzięki czemu działania doskonalące można skoncentrować tam, gdzie nakład czasu, wysiłku i pieniędzy przyniesie największy zwrot.
**Analiza Pareto składa się z czterech kroków:**
1. Określ kategorie, dla których będą zbierane informacje. Na przykład wskaż kategorie opisujące możliwe przyczyny lub rodzaje wad. Kategorie te mogą pochodzić z analizy przyczynowo-skutkowej.
2. Zbierz dane i oblicz częstość obserwacji w każdej kategorii dla odpowiedniego okresu. Do zbierania danych można użyć arkusza kontrolnego.
3. Posortuj kategorie malejąco według ich udziałów procentowych.
4. Przedstaw dane graficznie.

**Źródło:** Swink, M., Melnyk, S. and Hartley, J.L. (2024) _Managing Operations Across the Supply Chain_. New York: McGraw Hill. s. 212.

- **Kardynalność (Cardinality)** - określa unikalność wartości w relacji w modelu danych i opisuje, ile wystąpień jednej encji jest powiązanych z wystąpieniami innej encji.
- **CSV** - Comma-Separated Values (wartości rozdzielone przecinkami). Najpopularniejszy tekstowy format danych.
- **Format długi i szeroki** - format długi (wąski, pionowy, „stacked”) oznacza, że każdy wiersz jest jedną obserwacją, natomiast format szeroki (poziomy, „unstacked”) rozkłada zmienne na kolumny.
- **Pivotowanie (przestawianie)** - przekształca dane z formatu pionowego na poziomy. Tworzy kolumny z wierszy. Funkcja pivot w Pythonie. Narzędzie Cross Tab w Alteryx.
- **SKU** - Stock Keeping Unit (jednostka magazynowa, indeks). Alfanumeryczny symbol rodzaju dobra fizycznego używanego przez firmę. Podstawa zarządzania danymi podstawowymi (master data).

##### Główna formuła
**Reguła granicy:** SKU jest klasyfikowane według skumulowanego udziału wszystkich SKU sklasyfikowanych **przed** nim (`D2-C2`).
- SKU, które przekracza próg 80 %, nadal należy do grupy A.
- Pojedyncze dominujące SKU (np. 85 % całkowitej wartości) jest poprawnie klasyfikowane jako A, a nie B.
- W okresach o łącznej wartości 0 wszystkie SKU trafiają do grupy C.

``` mermaid
flowchart TD
    A[Start] --> T{"Czy łączna wartość okresu = 0?"}
    T -- Tak --> C0["Zwróć 'C'"]
    T -- Nie --> B{"Czy poprzedni udział skumulowany D2-C2 < 0,8?"}
    B -- Tak --> CatA["Zwróć 'A'"]
    B -- Nie --> C{"Czy poprzedni udział skumulowany D2-C2 < 0,95?"}
    C -- Tak --> CatB["Zwróć 'B'"]
    C -- Nie --> CatC["Zwróć 'C'"]
    C0 --> End[Koniec]
    CatA --> End
    CatB --> End
    CatC --> End
```
``` excel
=JEŻELI(SUMA($B:$B)=0;"C";JEŻELI(D2-C2<0,8;"A";JEŻELI(D2-C2<0,95;"B";"C")))
```

##### Kroki wykonania analizy ABC
**Definicja grup ABC:**
- A - najważniejsze SKU
- B - mniej ważne SKU
- C - nieistotne SKU

**Otwieranie danych:**
- Kliknij plik dwukrotnie lub użyj Plik > Otwórz w Excelu.
- Jeśli znaki Unicode, daty lub liczby dziesiętne nie wyświetlają się poprawnie, zaimportuj dane przez Dane > Pobierz dane > Z pliku > Z pliku tekstowego/CSV. W Power Query ustaw typy kolumn: prawy przycisk myszy > Zmień typ > Używanie ustawień regionalnych… (np. Data / polski dla formatu `DD.MM.RRRR` i przecinka dziesiętnego).
- Zamień każdy zakres źródłowy w Tabelę Excela (Wstawianie > Tabela) i nadaj jej nazwę w Projekt tabeli > Nazwa tabeli. Tabele rozszerzają się automatycznie, więc nie są potrzebne sztywne limity wierszy.

**Układ tabel źródłowych (używany we wszystkich krokach poniżej):**
Nazwy tabel i kolumn pozostają angielskie, ponieważ odpowiadają nagłówkom plików CSV używanych przez kod Python.

| Nazwa tabeli | Kolumny |
|---|---|
| StockHistory | Date, SKU, Stock (ilość), Period, MonthEnd |
| SalesHistory | Date, SKU, Sales (ilość), Period |
| COGS | SKU, COGS, Duplicate |

**Kolumna Period** (dane w granulacji dziennej). Dodaj ją jako kolumnę obliczeniową w StockHistory i SalesHistory:
``` excel
=TEKST([@Date];"rrrr-mm")
// jeśli Excel ma ustawiony język angielski
=TEKST([@Date];"yyyy-mm")
// alternatywa bez funkcji TEKST
=JEŻELI(MIESIĄC([@Date])<10;ROK([@Date])&"-0"&MIESIĄC([@Date]);ROK([@Date])&"-"&MIESIĄC([@Date]))
```

**Kolumna MonthEnd** (tylko StockHistory).
- Zapas jest stanem, a nie przepływem. Można użyć wyłącznie ostatniego zrzutu stanu dla danego SKU i miesiąca. Kilka wierszy z tą samą datą (magazyny, partie) jest nadal sumowanych.
- Jeśli zrzut zawiera dokładnie jedną datę na miesiąc, MonthEnd wynosi wszędzie 1.
``` excel
=JEŻELI([@Date]=MAKS.WARUNKÓW([Date];[SKU];[@SKU];[Period];[@Period]);1;0)
```
Szybka alternatywa dla bardzo dużych zrzutów (powyżej ok. 50 tys. wierszy):
1. Posortuj tabelę według SKU od A do Z, Period od A do Z, Date od najnowszych do najstarszych i zachowaj tę kolejność.
2. Dodaj kolumnę pomocniczą F `LatestDate`: `=JEŻELI(ORAZ(B2=B1;D2=D1);F1;A2)`.
3. Ustaw MonthEnd na `=JEŻELI(A2=F2;1;0)`.

**Kolumna Duplicate** (tabela COGS). Oznacza SKU z więcej niż jedną ceną. PODAJ.POZYCJĘ w Excelu i kod Python używają **pierwszej** ceny, ale duplikaty należy usunąć w danych podstawowych:
``` excel
=LICZ.JEŻELI([SKU];[@SKU])>1
```

###### Analiza ABC w Excelu z użyciem formuł
**Układ arkusza "Tabela ABC":**
- A = SKU
- B = COGS (cena jednostkowa)
- C:T = okresy (w tym przykładzie 18 okresów; dostosuj zakresy do liczby okresów)
- U = Suma ze wszystkich okresów

**Kroki:**
1. Przygotuj Tabelę "StockHistory": zrzut danych z ERP w formacie długim, ze stanem zapasu na koniec miesiąca kalendarzowego (MonthEnd = 1).
2. Przygotuj Tabelę "COGS" z cenami i sprawdź kolumnę Duplicate.
3. Skopiuj wszystkie SKU, wklej je jako wartości do kolumny A arkusza "Tabela ABC" i usuń duplikaty.
```
Excel -> Dane -> Usuń duplikaty
```
4. Dodaj cenę z COGS dla każdego SKU w kolumnie B (pierwsze dopasowanie, 0 gdy brak):
``` excel
=JEŻELI.BŁĄD(INDEKS(COGS[COGS];PODAJ.POZYCJĘ(\$A2;COGS[SKU];0));0)
```
   SKU z ceną 0 mają wartość zerową i trafiają do C. Sprawdź je, filtrując kolumnę B = 0.
5. Skopiuj wszystkie okresy ze StockHistory i usuń duplikaty. Wklej je z transpozycją jako nagłówki do C1:T1.
   - Nagłówki muszą pozostać **tekstem** (`2024-01`). Jeśli Excel zamienia je na daty, przed wklejeniem sformatuj C1:T1 jako Tekst.
6. Uzupełnij wartość zapasu funkcją SUMA.WARUNKÓW w C2 i przeciągnij w prawo i w dół. MAX(0;…) obcina ujemne stany ERP i zwroty netto do 0:
``` excel
=MAX(0;SUMA.WARUNKÓW(StockHistory[Stock];StockHistory[SKU];$A2;StockHistory[Period];C$1;StockHistory[MonthEnd];1))*\$B2
```
   Suma ze wszystkich okresów w U2 (do zagregowanej analizy ABC, patrz krok 7):
``` excel
=SUMA(C2:T2)
```
7. Wykonaj analizę ABC.
   1. Skopiuj SKU (kolumna A) i kolumnę wartości **jednego okresu**, a następnie wklej je jako wartości do arkusza "ABC": SKU w kolumnie A, wartość w kolumnie B.
      - Klasyczna analiza ABC używa wartości zagregowanej z 6–12 miesięcy, a klasy miesięczne mogą się zmieniać z miesiąca na miesiąc. Do analizy zagregowanej wklej zamiast pojedynczego okresu kolumnę U (Suma).
   2. Utwórz tabelę i posortuj ją dwupoziomowo: wartość od największych do najmniejszych, następnie SKU od A do Z. Drugi poziom rozstrzyga remisy, dzięki czemu wyniki są powtarzalne i identyczne z Pythonem.
```
Excel -> Dane -> Sortuj -> Dodaj poziom
```
   3. Dodaj udział w łącznej wartości jako kolumnę C:
``` excel
=JEŻELI(SUMA($B:$B)=0;0;B2/SUMA($B:$B))
```
8. Dodaj udział skumulowany jako kolumnę D, blokując komórkę początkową:
``` excel
=SUMA(C\$2:C2)
```
9. Przypisz grupy ABC w kolumnie E. `D2-C2` to skumulowany udział wszystkich SKU sklasyfikowanych przed bieżącym:
``` excel
=JEŻELI(SUMA($B:$B)=0;"C";JEŻELI(D2-C2<0,8;"A";JEŻELI(D2-C2<0,95;"B";"C")))
```
10. Skopiuj kolumny SKU i ABC i wklej je jako wartości do nowego arkusza dla bezpieczeństwa, np. "ABC Zapas 2024-01" (SKU w A, ABC w B). Powtórz kroki 7–9 dla każdego okresu. Arkusz analizy zagregowanej nazwij np. "ABC Zapas Suma".
11. Powtórz całą analizę ABC dla danych sprzedażowych per SKU i okres.
   - Użyj Tabeli SalesHistory bez kryterium MonthEnd, ponieważ sprzedaż jest przepływem i wszystkie wiersze są sumowane:
``` excel
=MAX(0;SUMA.WARUNKÓW(SalesHistory[Sales];SalesHistory[SKU];$A2;SalesHistory[Period];C$1))*\$B2
```
   - Zapisz wyniki jako "ABC Sprzedaż 2024-01" … oraz "ABC Sprzedaż Suma".
12. Porównaj grupy ABC zapasu i sprzedaży dla **tego samego okresu** w arkuszu "Porównanie".
   - Kolumna A: suma zbiorów SKU z obu arkuszy wynikowych, bez duplikatów.
   - SKU nieobecne po jednej stronie ma tam wartość zerową i jest traktowane jako C.
``` excel
// B2 – ABC Zapas
=JEŻELI.BŁĄD(INDEKS('ABC Zapas 2024-01'!$B:$B;PODAJ.POZYCJĘ(\$A2;'ABC Zapas 2024-01'!$A:$A;0));"C")
// C2 – ABC Sprzedaż
=JEŻELI.BŁĄD(INDEKS('ABC Sprzedaż 2024-01'!$B:$B;PODAJ.POZYCJĘ(\$A2;'ABC Sprzedaż 2024-01'!$A:$A;0));"C")
// D2 – Ryzyko
=JEŻELI(ORAZ(C2="A";B2="C");"Ryzyko braku towaru";JEŻELI(ORAZ(C2="C";B2="A");"Ryzyko utylizacji (termin przydatności)";""))
```
   - SKU w grupie A sprzedaży i C zapasu może prowadzić do braku towaru (stock-out).
   - SKU w grupie C sprzedaży i A zapasu może prowadzić do utylizacji lub odpisu z powodu terminu przydatności.
13. Zastosuj formatowanie warunkowe dla komórek klasyfikacji ABC: A na zielono, B na żółto, C na czerwono, lub odwrotnie.
   Użyj `Zielone wypełnienie z ciemnozielonym tekstem`, `Żółte wypełnienie z ciemnożółtym tekstem` oraz `Jasnoczerwone wypełnienie z ciemnoczerwonym tekstem`.
```
Excel -> Narzędzia główne -> Formatowanie warunkowe -> Reguły wyróżniania komórek -> Tekst, który zawiera...
```

##### Kroki wykonania analizy ABC w Excelu z użyciem tabel przestawnych
1. Dodaj odpowiednią wartość COGS jako nową kolumnę obliczeniową "COGS" w Tabeli źródłowej (pierwsze dopasowanie, 0 gdy brak):
``` excel
=JEŻELI.BŁĄD(INDEKS(COGS[COGS];PODAJ.POZYCJĘ([@SKU];COGS[SKU];0));0)
```
2. Utwórz nową kolumnę obliczeniową "Value", mnożąc ilość przez COGS:
``` excel
=[@Stock]*[@COGS]
```
3. Zaznacz Tabelę źródłową i utwórz tabelę przestawną:
```
Wstawianie -> Tabela przestawna -> Nowy arkusz
```
4. Rozmieść pola:
   - Przeciągnij **Period** do obszaru Filtry i wybierz jeden okres. Do analizy zagregowanej wybierz (Wszystko).
   - Tylko dla zapasu: przeciągnij **MonthEnd** do obszaru Filtry i wybierz 1.
   - Przeciągnij **SKU** do obszaru Wiersze.
   - Przeciągnij **Value** do obszaru Wartości **trzy razy**. Otrzymasz trzy kolumny: B = Suma z Value, C = suma bieżąca, D = udział.
5. Ustaw opcje wyświetlania wartości:
   - Drugie pole wartości (kolumna C): prawy przycisk myszy > Pokaż wartości jako > % sumy bieżącej w… > SKU.
   - Trzecie pole wartości (kolumna D): prawy przycisk myszy > Pokaż wartości jako > % sumy kolumny.
```
Suma z Value (prawy przycisk myszy) -> Pokaż wartości jako -> % sumy bieżącej w... -> SKU
Suma z Value2 (prawy przycisk myszy) -> Pokaż wartości jako -> % sumy kolumny
```
6. Wyłącz sumy końcowe, aby żaden wiersz sumy nie otrzymał klasy:
```
Projektowanie -> Sumy końcowe -> Wyłącz dla wierszy i kolumn
```
7. Posortuj etykiety wierszy malejąco według zwykłego pola "Suma z Value":
```
Etykiety wierszy (przycisk sortowania) -> Więcej opcji sortowania -> Malejąco (od Z do A) według: -> Suma z Value
```
8. Wyklucz SKU o wartości ujemnej, co odpowiada obcięciu ich do 0. Sumy i udziały procentowe są wtedy przeliczane na widocznych SKU. SKU bez klasy traktuje się jako C.
```
Etykiety wierszy (przycisk filtra) -> Filtry wartości -> Suma z Value -> jest większe niż -> 0
```
9. Dodaj kolumnę formuły E obok tabeli przestawnej, zaczynając od pierwszego wiersza danych tabeli. Przy dwóch filtrach raportu jest to wiersz 5, przy jednym filtrze (Sprzedaż) wiersz 4. Przeciągnij formułę w dół daleko poza maksymalną liczbę SKU. Po zmianie filtra Period analiza ABC aktualizuje się dynamicznie:
``` excel
=JEŻELI(A5="";"";JEŻELI(CZY.BŁĄD(C5);"C";JEŻELI(C5-D5<0,8;"A";JEŻELI(C5-D5<0,95;"B";"C"))))
```

#### Analiza XYZ w Excelu
##### Definicje
- **Współczynnik zmienności (CV, Coefficient of Variation)** - miara rozproszenia. Stosunek odchylenia standardowego do średniej. W tym dokumencie zarówno w Excelu (`ODCH.STAND.POPUL`), jak i w Pythonie (`ddof=0`) używana jest wersja dla populacji.
Współczynnik zmienności dla populacji: $$ CV = \frac{\sigma}{\mu} $$Współczynnik zmienności dla próby: $$ CV = \frac{s}{\bar{x}} $$
- **CSV** - Comma-Separated Values (wartości rozdzielone przecinkami). Najpopularniejszy tekstowy format danych.
- **Decyl** - kwantyl dzielący na dziesięć grup. Wartości dzielące zbiór danych uporządkowany od najmniejszej do największej na dziesięć równych części, z których każda obejmuje 10 % obserwacji.
- **Rozkład** - opisuje możliwe wartości zmiennej losowej i częstość ich występowania w zbiorze danych. Pozwala zrozumieć częstość, prawdopodobieństwo i rozrzut różnych wyników.
- **Histogram** - wizualna prezentacja rozkładu danych ilościowych. Wykres złożony z prostokątów, których pole jest proporcjonalne do częstości zmiennej, a szerokość równa przedziałowi klasowemu.
- **Format długi i szeroki** - format długi (wąski, pionowy, „stacked”) oznacza, że każdy wiersz jest jedną obserwacją, natomiast format szeroki (poziomy, „unstacked”) rozkłada zmienne na kolumny.
- **Mediana** - drugi z kwantyli dzielących na cztery grupy, czyli drugi kwartyl. Wartość dzieląca zbiór danych uporządkowany od najmniejszej do największej na dwie równe części, z których każda obejmuje 50 % obserwacji.
- **Melting (anulowanie przestawienia, unpivot)** - przekształca dane z formatu poziomego na pionowy. Funkcja melt w Pythonie. Narzędzie Transpose w Alteryx.
- **Kwartyl** - kwantyl dzielący na cztery grupy. Wartości dzielące zbiór danych uporządkowany od najmniejszej do największej na cztery równe części, z których każda obejmuje 25 % obserwacji.
- **Kwantyl** - punkt dzielący zbiór danych na podgrupy równej wielkości, tak że określony odsetek danych znajduje się poniżej tego punktu. Popularne kwantyle mają specjalne nazwy, np. kwartyle (cztery grupy), decyle (dziesięć grup) i percentyle (100 grup).
- **Percentyl** - kwantyl dzielący na sto grup. Wartości dzielące zbiór danych uporządkowany od najmniejszej do największej na sto równych części, z których każda obejmuje 1 % obserwacji. `PERCENTYL.PRZEDZ.ZAMK` w Excelu odpowiada `quantile()` w pandas (interpolacja liniowa).
- **Pivotowanie (przestawianie)** - przekształca dane z formatu pionowego na poziomy. Tworzy kolumny z wierszy. Funkcja pivot w Pythonie. Narzędzie Cross Tab w Alteryx.
- **Odchylenie standardowe** - statystyczna miara rozrzutu danych wokół średniej, wskazująca, jak bardzo poszczególne obserwacje odbiegają od średniej.
Odchylenie standardowe populacji:
$$
\sigma =\sqrt{\frac{\sum_{i=1}^{N} (x_i - \mu)^2}{N}}
$$
Odchylenie standardowe próby:
$$
s = \sqrt{\frac{\sum_{i=1}^{n} (x_i - \bar{x})^2}{n-1}}
$$
- **Wariancja** - statystyczna miara _rozrzutu lub rozproszenia_ obserwacji w zbiorze względem ich średniej.
Wariancja populacji: $$ \sigma^2 = \frac{\sum_{i=1}^{N} (x_i - \mu)^2}{N} $$ Wariancja próby: $$ s^2 = \frac{\sum_{i=1}^{n} (x_i - \bar{x})^2}{n-1} $$
- **SKU** - Stock Keeping Unit (jednostka magazynowa, indeks). Alfanumeryczny symbol rodzaju dobra fizycznego używanego przez firmę. Podstawa zarządzania danymi podstawowymi (master data).

##### Analiza XYZ w Excelu
###### Główna formuła
**Progi:**
- `$W$2` = x_threshold i `$X$2` = y_threshold (patrz krok 7). Domyślnie są to 33. i 66. percentyl CV.
- Stałe wartości, takie jak 2,16 / 2,4, to progi odczytane z histogramu **jednego konkretnego zbioru danych**, a nie reguły ogólne. Wartości podręcznikowe to X ≤ 0,5 i Y ≤ 1,0.
- SKU bez popytu (średnia = 0) otrzymują puste CV i **nie są klasyfikowane**. Nie są to SKU „stabilne”.

``` mermaid
flowchart TD
    A[Start] --> M{"Czy CV jest puste (średnia = 0)?"}
    M -- Tak --> N["Zwróć pusty tekst (brak popytu)"]
    M -- Nie --> B{"Czy T2 <= x_threshold?"}
    B -- Tak --> X["Zwróć 'X'"]
    B -- Nie --> C{"Czy T2 <= y_threshold?"}
    C -- Tak --> Y["Zwróć 'Y'"]
    C -- Nie --> Z["Zwróć 'Z'"]
    N --> End[Koniec]
    X --> End
    Y --> End
    Z --> End
```
``` excel
=JEŻELI(T2="";"";JEŻELI(T2<=$W$2;"X";JEŻELI(T2<=$X$2;"Y";"Z")))
```

###### Kroki wykonania analizy XYZ
**Definicja grup XYZ:**
- X - SKU stabilne
- Y - SKU mniej stabilne
- Z - SKU niestabilne
- puste - brak popytu w analizowanym horyzoncie (bez klasyfikacji)

**Otwieranie danych:**
Tak samo jak w analizie ABC: Pobierz dane ze Zmień typ > Używanie ustawień regionalnych, jeśli daty lub liczby dziesiętne są źle odczytywane, a następnie zamiana źródeł na Tabele StockHistory / SalesHistory (wraz z kolumnami Period i MonthEnd).

###### Kroki wykonania analizy XYZ w Excelu
**Układ arkusza "Tabela XYZ":**
- A = SKU
- B:S = ilość w poszczególnych okresach (18 okresów)
- T = CV
- U = XYZ
- W1/W2 = x_threshold
- X1/X2 = y_threshold

Analiza XYZ zawsze używa **ilości**, a nie wartości.

**Kroki:**
1. Przygotuj Tabelę "StockHistory": zrzut danych z ERP w formacie długim, ze stanem zapasu na koniec miesiąca kalendarzowego (MonthEnd = 1).
2. Skopiuj wszystkie SKU, wklej je jako wartości do kolumny A arkusza "Tabela XYZ" i usuń duplikaty.
```
Excel -> Dane -> Usuń duplikaty
```
3. Skopiuj wszystkie okresy ze StockHistory i usuń duplikaty. Wklej je z transpozycją do B1:S1 jako nagłówki **tekstowe**.
4. Uzupełnij ilość zapasu funkcją SUMA.WARUNKÓW w B2 i przeciągnij w prawo i w dół. Brakujące kombinacje SKU/okres zwracają 0 (dane gęste), a wartości ujemne są obcinane do 0:
``` excel
=MAX(0;SUMA.WARUNKÓW(StockHistory[Stock];StockHistory[SKU];$A2;StockHistory[Period];B$1;StockHistory[MonthEnd];1))
// dla danych sprzedażowych
=MAX(0;SUMA.WARUNKÓW(SalesHistory[Sales];SalesHistory[SKU];$A2;SalesHistory[Period];B$1))
```
5. Oblicz współczynnik zmienności w kolumnie T. Jako źródło danych użyj ilości z każdego okresu dla danego SKU.
   - **Które odchylenie standardowe:** użyj odchylenia standardowego populacji (`ODCH.STAND.POPUL`), tak samo jak `ddof=0` w Pythonie.
     - Wersja dla populacji odpowiada na pytanie: jak bardzo sprzedaż tego SKU _faktycznie_ się wahała w ciągu tych 18 miesięcy?
     - Wersja dla próby (`ODCH.STANDARDOWE.PRÓBKI`) jest standardem _wnioskowania statystycznego_. Daje **nieobciążony estymator** prawdziwej wariancji populacji.
     - Przy 18 okresach różnica wynosi ok. 3 %. Ma znaczenie tylko przy stałych progach, ale wszędzie należy używać tej samej wersji.
   - **Średnia zerowa:** zwraca pusty tekst. `PERCENTYL.PRZEDZ.ZAMK` ignoruje tekst, więc takie SKU nie zniekształcają progów.
``` excel
=JEŻELI(ŚREDNIA(B2:S2)=0;"";ODCH.STAND.POPUL(B2:S2)/ŚREDNIA(B2:S2))
```
   Opcjonalny wariant cyklu życia (Excel 365). CV jest liczone tylko między pierwszym a ostatnim okresem z popytem, więc zera sprzed wprowadzenia i po wycofaniu produktu nie spychają nowych i wygaszanych SKU do Z. SKU z mniej niż 2 aktywnymi okresami pozostają puste.
   - Nazwy zmiennych w LET nie mogą być literami `W` ani `K`, które są zarezerwowane dla notacji W1K1 w polskim Excelu.
``` excel
=LET(zakres;B2:S2;idx;SEKWENCJA(1;LICZBA.KOLUMN(zakres));
 JEŻELI(SUMA(zakres)=0;"";
 LET(nz;FILTRUJ(idx;zakres<>0);okno;FILTRUJ(zakres;(idx>=MIN(nz))*(idx<=MAX(nz)));
 JEŻELI(ILE.LICZB(okno)<2;"";ODCH.STAND.POPUL(okno)/ŚREDNIA(okno)))))
```
6. Zaznacz kolumnę CV i utwórz histogram w arkuszu "Wykresy", aby znaleźć najlepsze granice grup XYZ. Puste wartości CV są pomijane.
```
Wstawianie -> Wykresy -> Wstaw wykres statystyczny -> Histogram
```
7. Oblicz progi.
   - X to 33. percentyl, a Y to 66. percentyl populacji CV, z wartością zastępczą 0,5 / 1,0, gdy 66. percentyl wynosi 0 lub nie istnieje żadne CV. Jest to logika identyczna z Pythonem.
   - W1 = "x_threshold", X1 = "y_threshold":
``` excel
// W2 – x_threshold
=JEŻELI.BŁĄD(JEŻELI(PERCENTYL.PRZEDZ.ZAMK($T:$T;0,66)=0;0,5;PERCENTYL.PRZEDZ.ZAMK($T:$T;0,33));0,5)
// X2 – y_threshold
=JEŻELI.BŁĄD(JEŻELI(PERCENTYL.PRZEDZ.ZAMK($T:$T;0,66)=0;1;PERCENTYL.PRZEDZ.ZAMK($T:$T;0,66));1)
```
   - Wersja ręczna: wpisz wartości odczytane z histogramu bezpośrednio do W2 i X2. Na przykład 0,5 / 1 (wartości podręcznikowe) lub 2,16 / 2,4 (progi jednego konkretnego zbioru danych).
8. Oblicz grupy XYZ w kolumnie U:
``` excel
=JEŻELI(T2="";"";JEŻELI(T2<=$W$2;"X";JEŻELI(T2<=$X$2;"Y";"Z")))
```
9. Zastosuj formatowanie warunkowe dla komórek klasyfikacji XYZ: X na zielono, Y na żółto, Z na czerwono, lub odwrotnie.
```
Excel -> Narzędzia główne -> Formatowanie warunkowe -> Reguły wyróżniania komórek -> Tekst, który zawiera...
```
10. Zbuduj macierz ABC-XYZ w arkuszu "Macierz". Użyj zagregowanej (Suma) analizy ABC dla tego samego źródła danych.
``` excel
// A = SKU (lista unikalna), B2 – ABC
=JEŻELI.BŁĄD(INDEKS('ABC Sprzedaż Suma'!$B:$B;PODAJ.POZYCJĘ(\$A2;'ABC Sprzedaż Suma'!$A:$A;0));"C")
// C2 – XYZ (&"" zapobiega zwróceniu 0 dla pustej komórki)
=JEŻELI.BŁĄD(INDEKS('Tabela XYZ'!$U:$U;PODAJ.POZYCJĘ(\$A2;'Tabela XYZ'!$A:$A;0))&"";"")
// D2 – Segment
=B2&C2
// Siatka: F2:F4 = A, B, C; G1:I1 = X, Y, Z; G2 przeciągnij w prawo i w dół
=LICZ.WARUNKI($B:$B;$F2;$C:$C;G$1)
```

###### Kroki wykonania analizy XYZ w Excelu z użyciem tabel przestawnych
1. Zaznacz Tabelę źródłową i utwórz tabelę przestawną:
```
Wstawianie -> Tabela przestawna -> Nowy arkusz
```
2. Rozmieść pola:
   - Tylko dla zapasu: przeciągnij **MonthEnd** do obszaru Filtry i wybierz 1.
   - Przeciągnij **SKU** do obszaru Wiersze, a **Period** do obszaru Kolumny.
   - Przeciągnij pole **ilości** (Stock lub Sales, nie Value) do obszaru Wartości jako Suma.
3. Wyłącz sumy końcowe, aby kolumna sumy nie wchodziła do zakresu CV:
```
Projektowanie -> Sumy końcowe -> Wyłącz dla wierszy i kolumn
```
4. Pokazuj puste komórki jako 0. `ŚREDNIA` i `ODCH.STAND.POPUL` ignorują puste komórki, więc bez tego ustawienia brakujące okresy byłyby pomijane (dane rzadkie) zamiast liczone jako zerowy popyt (dane gęste, jak w Pythonie):
```
Analiza tabeli przestawnej -> Opcje -> Układ i formatowanie -> Dla pustych komórek pokaż: 0
```
5. Oblicz współczynnik zmienności w kolumnie U obok tabeli przestawnej, zostawiając pustą kolumnę T jako odstęp.
   - Zacznij od pierwszego wiersza danych (w tym układzie wiersz 5) i przeciągnij formułę w dół daleko poza maksymalną liczbę SKU.
   - B5:S5 obejmuje 18 okresów; dostosuj zakres do liczby okresów.
   - Wersja dla Excel 365, która obcina ujemne wartości netto do 0:
``` excel
=JEŻELI(A5="";"";LET(zakres;JEŻELI(B5:S5<0;0;B5:S5);JEŻELI(ŚREDNIA(zakres)=0;"";ODCH.STAND.POPUL(zakres)/ŚREDNIA(zakres))))
```
   - Bez LET (tylko gdy dane nie zawierają wartości ujemnych):
``` excel
=JEŻELI(A5="";"";JEŻELI(ŚREDNIA(B5:S5)=0;"";ODCH.STAND.POPUL(B5:S5)/ŚREDNIA(B5:S5)))
```
6. Zaznacz kolumnę CV i utwórz histogram w arkuszu "Wykresy", aby znaleźć najlepsze granice grup XYZ.
7. Oblicz progi w X2 / Y2, z etykietami w X1 / Y1:
``` excel
// X2 – x_threshold
=JEŻELI.BŁĄD(JEŻELI(PERCENTYL.PRZEDZ.ZAMK($U:$U;0,66)=0;0,5;PERCENTYL.PRZEDZ.ZAMK($U:$U;0,33));0,5)
// Y2 – y_threshold
=JEŻELI.BŁĄD(JEŻELI(PERCENTYL.PRZEDZ.ZAMK($U:$U;0,66)=0;1;PERCENTYL.PRZEDZ.ZAMK($U:$U;0,66));1)
```
8. Oblicz grupy XYZ w kolumnie V:
``` excel
=JEŻELI(U5="";"";JEŻELI(U5<=$X$2;"X";JEŻELI(U5<=$Y$2;"Y";"Z")))
```
9. Zastosuj formatowanie warunkowe dla komórek klasyfikacji XYZ: X na zielono, Y na żółto, Z na czerwono, lub odwrotnie.
```
Excel -> Narzędzia główne -> Formatowanie warunkowe -> Reguły wyróżniania komórek -> Tekst, który zawiera...
```

#### Analiza ABC w Pythonie
##### Wyjaśnienie
Kod Python wykonuje analizę dla wszystkich okresów dostarczonych w formacie długim oraz jedną analizę zagregowaną ze wszystkich okresów.

**Pliki wejściowe** (rozdzielane średnikiem, przecinek dziesiętny):
- `Sales.csv` lub `Stock.csv` z kolumnami `Date;SKU;Sales` lub `Date;SKU;Stock`
- `COGS.csv` z kolumnami `SKU;COGS`

**Przetwarzanie:**
- Daty są parsowane z jawnie podanym formatem `DATE_FORMAT`, więc dzień i miesiąc nigdy nie zostaną po cichu zamienione.
- Dla zapasu zachowywany jest tylko stan na koniec miesiąca dla każdego SKU.
- Przy zduplikowanych SKU w COGS zachowywana jest pierwsza cena, tak samo jak w funkcji PODAJ.POZYCJĘ w Excelu.
- Ujemne wartości SKU/okres są obcinane do 0.
- Wewnętrznie klasyfikacja używa schematu `('SKU', 'Period', 'Value')`. Period ma format `RRRR-MM`.

**Wynik:**
- `abc_<Sales|Stock>.xlsx` (per okres)
- `abc_total_<Sales|Stock>.xlsx` (zagregowany)

Zmodyfikuj blok konfiguracji i uruchom kod raz dla `Stock` i raz dla `Sales`:
``` python
# Configuration:
value_field = 'Sales'   # 'Sales' or 'Stock'
input_dir = "C:/Python repositories/Test 2/data/input_data/"
DATE_FORMAT = '%d.%m.%Y'  # '%Y-%m-%d' for ISO dates
```
##### Kod Python
``` python
import os
import numpy as np
import pandas as pd

# =====================================================================
# Configuration
# =====================================================================
value_field = 'Sales'                     # 'Sales' or 'Stock'
input_dir = "C:/Python repositories/Test 2/data/input_data/"
file_path1 = input_dir + value_field + ".csv"
file_path2 = input_dir + "COGS.csv"

CSV_SEP = ';'
DECIMAL = ','            # decimal separator in the CSV files
THOUSANDS = '.'          # thousands separator in the CSV files (None if not used)
DATE_FORMAT = '%d.%m.%Y' # ERP date format, e.g. '%Y-%m-%d' for ISO dates
A_THRESHOLD = 0.80
B_THRESHOLD = 0.95


# =====================================================================
# Loading helpers
# =====================================================================
def load_long_data(file_path: str, value_field: str, date_format: str = DATE_FORMAT) -> pd.DataFrame:
    """Load a long-format ERP dump (Date; SKU; <value_field>) and add a 'Period' (YYYY-MM) column."""
    df = pd.read_csv(
        file_path, sep=CSV_SEP, decimal=DECIMAL, thousands=THOUSANDS,
        dtype={'SKU': str, 'Date': str},   # keeps leading zeros in SKUs; dates parsed explicitly below
    )
    missing = {'Date', 'SKU', value_field} - set(df.columns)
    if missing:
        raise ValueError(f"{file_path}: missing column(s) {missing}")

    df[value_field] = pd.to_numeric(df[value_field], errors='coerce')
    n_bad = int(df[value_field].isna().sum())
    if n_bad:
        print(f"⚠️  {n_bad} empty/non-numeric '{value_field}' values replaced with 0.")
        df[value_field] = df[value_field].fillna(0.0)

    # Explicit format: raises an error instead of silently swapping day and month
    df['Date'] = pd.to_datetime(df['Date'], format=date_format)
    df['Period'] = df['Date'].dt.strftime('%Y-%m')
    return df


def keep_month_end_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    """Stock is a level, not a flow: keep only the last snapshot date per SKU and month.
    Several rows on that date (warehouses, batches) are kept and summed later."""
    last_date = df.groupby(['SKU', 'Period'])['Date'].transform('max')
    out = df.loc[df['Date'] == last_date].copy()
    dropped = len(df) - len(out)
    if dropped:
        print(f"ℹ️  {dropped} intra-month stock snapshot rows removed (month-end kept).")
    return out


def load_cogs(file_path: str) -> pd.DataFrame:
    """Load COGS prices; duplicate SKUs keep the first price (same as Excel MATCH)."""
    cogs = pd.read_csv(file_path, sep=CSV_SEP, decimal=DECIMAL, thousands=THOUSANDS, dtype={'SKU': str})
    missing = {'SKU', 'COGS'} - set(cogs.columns)
    if missing:
        raise ValueError(f"{file_path}: missing column(s) {missing}")
    cogs['COGS'] = pd.to_numeric(cogs['COGS'], errors='coerce').fillna(0.0)

    dups = int(cogs['SKU'].duplicated().sum())
    if dups:
        print(f"⚠️  {dups} duplicate SKUs in COGS – keeping the first price.")
        cogs = cogs.drop_duplicates('SKU', keep='first')
    return cogs[['SKU', 'COGS']]


def clip_negative(df: pd.DataFrame, col: str = 'Value') -> pd.DataFrame:
    """Clip negative SKU/Period values (returns, negative ERP stock) to 0 and log them."""
    df = df.copy()
    neg = df[col] < 0
    if neg.any():
        print(f"⚠️  {int(neg.sum())} negative SKU/Period values clipped to 0.")
        df.loc[neg, col] = 0.0
    return df


# =====================================================================
# ABC Classification
# =====================================================================
def assign_abc_groups(df: pd.DataFrame, a_threshold: float = 0.80, b_threshold: float = 0.95) -> pd.DataFrame:
    """
    Assigns ABC classes to SKUs per Period based on cumulative value contribution (Pareto).

    Boundary rule
    -------------
    A SKU is classified by the cumulative share of all SKUs ranked BEFORE it.
    The SKU that crosses the 80 % (95 %) line therefore still belongs to A (B),
    and a single dominant SKU (> 80 % of value) is classified as A.
    Excel equivalent: =IF(SUM($B:$B)=0;"C";IF(D2-C2<0,8;"A";IF(D2-C2<0,95;"B";"C")))

    Rules
    -----
    - Aggregation at (SKU, Period) is SUM; negative results are clipped to 0.
    - Ties in Value are broken by SKU ascending (reproducible results).
    - Periods with total value 0 -> all SKUs 'C'.

    Returns
    -------
    Input columns + ['Share', 'Cumulative_Percent', 'ABC_Group'].
    """
    # === 1. Input validation ===
    required_columns = {'SKU', 'Period', 'Value'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_columns - set(df.columns)}")
    if not pd.api.types.is_numeric_dtype(df['Value']):
        raise TypeError("'Value' column must be numeric (float or int).")
    if not 0 < a_threshold < b_threshold <= 1:
        raise ValueError("Thresholds must satisfy 0 < a_threshold < b_threshold <= 1.")

    df = df.copy()
    df['Value'] = df['Value'].fillna(0.0)

    # === 2. Aggregate per SKU/Period and clip negatives ===
    agg_df = df.groupby(['Period', 'SKU'], as_index=False)['Value'].sum()
    agg_df = clip_negative(agg_df)

    # === 3. Sort (value desc, SKU asc as tie-breaker) and compute cumulative metrics ===
    agg_df = agg_df.sort_values(['Period', 'Value', 'SKU'], ascending=[True, False, True]).reset_index(drop=True)

    total = agg_df.groupby('Period')['Value'].transform('sum')
    cum_value = agg_df.groupby('Period')['Value'].cumsum()
    prev_cum_value = cum_value.groupby(agg_df['Period']).shift(fill_value=0.0)

    safe_total = total.where(total != 0)          # NaN where period total = 0
    agg_df['Share'] = (agg_df['Value'] / safe_total).fillna(0.0)
    agg_df['Cumulative_Percent'] = (cum_value / safe_total).fillna(1.0)
    prev_cum_pct = (prev_cum_value / safe_total).fillna(1.0)

    # === 4. ABC Group assignment (vectorized) ===
    agg_df['ABC_Group'] = np.select(
        [total == 0, prev_cum_pct < a_threshold, prev_cum_pct < b_threshold],
        ['C', 'A', 'B'],
        default='C',
    )

    # === 5. Merge results back into original DataFrame ===
    result_df = pd.merge(
        df,
        agg_df[['Period', 'SKU', 'Share', 'Cumulative_Percent', 'ABC_Group']],
        on=['Period', 'SKU'],
        how='left',
        validate='m:1',
    )

    # === 6. Validation ===
    if result_df['ABC_Group'].isna().any():
        raise RuntimeError("ABC group assignment failed for some rows.")

    return result_df.sort_values(['Period', 'Cumulative_Percent', 'SKU']).reset_index(drop=True)


# =====================================================================
# Saving in the same folder as the Python (py or ipynb) file
# =====================================================================
def save_file(data: pd.DataFrame, name: str) -> None:
    """Saves a DataFrame to Excel; uses xlsxwriter if installed, otherwise openpyxl."""
    data_dump = os.path.join(os.getcwd(), f"{name}.xlsx")
    try:
        import xlsxwriter  # noqa: F401
        engine = "xlsxwriter"
    except ModuleNotFoundError:
        print("⚠️  xlsxwriter not found. Falling back to openpyxl.")
        engine = "openpyxl"

    with pd.ExcelWriter(data_dump, engine=engine) as writer:
        data.to_excel(writer, sheet_name=name[:31], index=False)
    print(f"✅ Data successfully saved as: {data_dump}")


# =====================================================================
# Execution
# =====================================================================
# Load input data
abc_table = load_long_data(file_path1, value_field)
if value_field == 'Stock':
    abc_table = keep_month_end_snapshot(abc_table)

cogs = load_cogs(file_path2)

# Vlookup COGS column (m:1 guaranteed after de-duplication)
stock_cogs = pd.merge(abc_table, cogs, how='left', on='SKU', validate='m:1')
no_price = stock_cogs['COGS'].isna()
if no_price.any():
    print(f"⚠️  {stock_cogs.loc[no_price, 'SKU'].nunique()} SKUs without COGS – valued at 0 (they fall into C).")
stock_cogs['COGS'] = stock_cogs['COGS'].fillna(0.0)

# New Value column
stock_cogs['Value'] = stock_cogs[value_field] * stock_cogs['COGS']

# Aggregate on SKU/Period level and clip negatives (Excel: MAX(0;SUMIFS(...))*price)
abc_input = stock_cogs.groupby(['SKU', 'Period'], as_index=False)['Value'].sum()
abc_input = clip_negative(abc_input)

# ABC classification per period
df_result = assign_abc_groups(abc_input, A_THRESHOLD, B_THRESHOLD)

# ABC classification over all periods (classical aggregate view)
periods = sorted(abc_input['Period'].unique())
total_input = abc_input.groupby('SKU', as_index=False)['Value'].sum()
total_input['Period'] = f"{periods[0]}..{periods[-1]}"
df_total = assign_abc_groups(total_input, A_THRESHOLD, B_THRESHOLD)

# Save output files
save_file(df_result, "abc_" + value_field)
save_file(df_total, "abc_total_" + value_field)
```

#### Analiza XYZ w Pythonie
##### Wyjaśnienie
Kod Python wykonuje analizę dla wszystkich okresów dostarczonych w formacie długim. Analiza XYZ zawsze używa **ilości**.

**Plik wejściowy:** `Sales.csv` lub `Stock.csv` z kolumnami `Date;SKU;Sales` lub `Date;SKU;Stock`. Obowiązują te same zasady parsowania co w skrypcie ABC: jawny format daty, stan na koniec miesiąca dla zapasu, obcinanie wartości ujemnych do 0. Wewnętrznie używany jest schemat `('SKU', 'Period', 'Value')`.

**Statystyka:**
- Odchylenie standardowe populacji (`ddof=0`), identyczne z `ODCH.STAND.POPUL` w Excelu.
- Progi to 33. i 66. percentyl (`PERCENTYL.PRZEDZ.ZAMK`) wszystkich SKU z popytem.
- Wartości zastępcze 0,5 / 1,0, gdy 66. percentyl wynosi 0 lub nie istnieje żadne kwalifikujące się SKU.
- SKU ze średnią zerową nie są klasyfikowane (puste).

**Opcje `DATA_MODE`:**
- `"dense"` (domyślnie, identycznie jak tabela w Excelu): brakujące okresy są liczone jako 0.
- `"sparse"`: używane są tylko okresy obecne w danych.
- `"lifecycle"`: dane gęste, ale tylko między pierwszym a ostatnim okresem z popytem dla każdego SKU. Odpowiada formule cyklu życia w Excel 365.

**Wynik:**
- `xyz_<Sales|Stock>.xlsx` (format długi)
- `xyz_wide_<Sales|Stock>.xlsx` (jeden wiersz na SKU)

Oba wyniki pochodzą z tego samego obliczenia, więc zawsze zawierają identyczne klasy.
``` python
# Configuration:
value_field = 'Sales'
file_path = "C:\\Python repositories\\Education project\\src\\data\\input\\" + value_field + ".csv"
DATA_MODE = 'dense'
MANUAL_THRESHOLDS = None   # e.g. (0.5, 1.0) textbook or (2.16, 2.4) read from a histogram
```
##### Kod Python
``` python
import os
from typing import Literal, Optional, Tuple

import numpy as np
import pandas as pd

# =====================================================================
# Configuration
# =====================================================================
value_field = 'Sales'                     # 'Sales' or 'Stock' (quantity)
file_path = "C:\\Python repositories\\Education project\\src\\data\\input\\" + value_field + ".csv"

CSV_SEP = ';'
DECIMAL = ','
THOUSANDS = '.'
DATE_FORMAT = '%d.%m.%Y'                  # '%Y-%m-%d' for ISO dates
DATA_MODE = 'dense'                       # 'dense' (= Excel), 'sparse', 'lifecycle'
X_QUANTILE = 0.33
Y_QUANTILE = 0.66
MANUAL_THRESHOLDS: Optional[Tuple[float, float]] = None   # e.g. (0.5, 1.0) or (2.16, 2.4)
MIN_PERIODS = 2
FALLBACK_THRESHOLDS = (0.5, 1.0)

DataMode = Literal["dense", "sparse", "lifecycle"]


# =====================================================================
# Loading helpers
# =====================================================================
def load_long_data(file_path: str, value_field: str, date_format: str = DATE_FORMAT) -> pd.DataFrame:
    """Load a long-format ERP dump (Date; SKU; <value_field>) and add a 'Period' (YYYY-MM) column."""
    df = pd.read_csv(
        file_path, sep=CSV_SEP, decimal=DECIMAL, thousands=THOUSANDS,
        dtype={'SKU': str, 'Date': str},
    )
    missing = {'Date', 'SKU', value_field} - set(df.columns)
    if missing:
        raise ValueError(f"{file_path}: missing column(s) {missing}")

    df[value_field] = pd.to_numeric(df[value_field], errors='coerce')
    n_bad = int(df[value_field].isna().sum())
    if n_bad:
        print(f"⚠️  {n_bad} empty/non-numeric '{value_field}' values replaced with 0.")
        df[value_field] = df[value_field].fillna(0.0)

    df['Date'] = pd.to_datetime(df['Date'], format=date_format)
    df['Period'] = df['Date'].dt.strftime('%Y-%m')
    return df


def keep_month_end_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only the last snapshot date per SKU and month (stock is a level, not a flow)."""
    last_date = df.groupby(['SKU', 'Period'])['Date'].transform('max')
    out = df.loc[df['Date'] == last_date].copy()
    dropped = len(df) - len(out)
    if dropped:
        print(f"ℹ️  {dropped} intra-month stock snapshot rows removed (month-end kept).")
    return out


def clip_negative(df: pd.DataFrame, col: str = 'Value') -> pd.DataFrame:
    """Clip negative SKU/Period values to 0 and log them (Excel: MAX(0;SUMIFS(...)))."""
    df = df.copy()
    neg = df[col] < 0
    if neg.any():
        print(f"⚠️  {int(neg.sum())} negative SKU/Period values clipped to 0.")
        df.loc[neg, col] = 0.0
    return df


# =====================================================================
# Shared XYZ calculation (used by BOTH output functions -> identical classes)
# =====================================================================
def _prepare_period_sum(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Validate input, coerce Value to numeric, aggregate (SKU, Period) by SUM, clip negatives."""
    required = {"SKU", "Period", "Value"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required column(s): {required - set(df.columns)}")

    df_out = df.copy()
    if not pd.api.types.is_numeric_dtype(df_out["Value"]):
        coerced = pd.to_numeric(df_out["Value"], errors="coerce")
        if coerced.isna().all():
            raise TypeError("'Value' column must be numeric or convertible to numeric.")
        df_out["Value"] = coerced
    df_out["Value"] = df_out["Value"].fillna(0.0)

    period_sum = df_out.groupby(["SKU", "Period"], as_index=False)["Value"].sum()
    period_sum = clip_negative(period_sum)
    return df_out, period_sum


def _build_stats_source(period_sum: pd.DataFrame, data_mode: DataMode) -> pd.DataFrame:
    """
    Build the data used for mean/std:
    - sparse:    only the (SKU, Period) rows present in the data
    - dense:     all SKUs x all Periods, missing = 0 (identical to the Excel table)
    - lifecycle: dense, trimmed per SKU to [first, last] period with demand
    """
    if data_mode == "sparse":
        return period_sum

    all_skus = period_sum["SKU"].unique()
    all_periods = np.sort(period_sum["Period"].unique())
    scaffold = pd.MultiIndex.from_product(
        [all_skus, all_periods], names=["SKU", "Period"]
    ).to_frame(index=False)

    dense = scaffold.merge(period_sum, on=["SKU", "Period"], how="left")
    dense["Value"] = dense["Value"].fillna(0.0)
    if data_mode == "dense":
        return dense

    # lifecycle
    dense = dense.sort_values(["SKU", "Period"]).reset_index(drop=True)
    active = dense["Value"].ne(0)
    after_first = active.groupby(dense["SKU"]).cummax()
    before_last = active[::-1].groupby(dense["SKU"][::-1]).cummax().sort_index()
    return dense[after_first & before_last]


def _compute_sku_stats(stats_source: pd.DataFrame) -> pd.DataFrame:
    """Per-SKU count, mean, POPULATION std (ddof=0 = Excel STDEV.P) and CV (NaN if mean = 0)."""
    g = stats_source.groupby("SKU")["Value"]
    stats = pd.DataFrame({
        "n_periods": g.count(),
        "mean_value": g.mean(),
        "std_value": g.std(ddof=0),
    }).reset_index()
    stats["cv"] = stats["std_value"] / stats["mean_value"].where(stats["mean_value"] > 0)
    return stats


def _compute_thresholds(
    sku_stats: pd.DataFrame,
    x_quantile: float = X_QUANTILE,
    y_quantile: float = Y_QUANTILE,
    manual_thresholds: Optional[Tuple[float, float]] = None,
) -> Tuple[float, float, str]:
    """
    Percentile thresholds over eligible SKUs (>= MIN_PERIODS and CV defined).
    Fallback to (0.5, 1.0) only if no eligible SKU exists or the y-threshold is 0.
    A legitimate x-threshold of 0 (many perfectly constant SKUs) is kept.
    """
    if manual_thresholds is not None:
        x, y = (float(v) for v in manual_thresholds)
        if x > y:
            raise ValueError("Manual thresholds must satisfy x <= y.")
        return x, y, "manual"

    eligible = (sku_stats["n_periods"] >= MIN_PERIODS) & sku_stats["cv"].notna()
    cvs = sku_stats.loc[eligible, "cv"]
    if cvs.empty:
        return *FALLBACK_THRESHOLDS, "fallback (no eligible SKUs)"

    x = float(cvs.quantile(x_quantile))   # linear interpolation = Excel PERCENTILE.INC
    y = float(cvs.quantile(y_quantile))
    if y == 0.0:
        return *FALLBACK_THRESHOLDS, "fallback (y-threshold = 0)"
    return x, y, "percentile"


def _classify(sku_stats: pd.DataFrame, x_threshold: float, y_threshold: float) -> pd.DataFrame:
    """X/Y/Z, or blank for SKUs without demand or with too few periods."""
    stats = sku_stats.copy()
    conditions = [
        stats["n_periods"] < MIN_PERIODS,   # only possible in sparse/lifecycle mode
        stats["cv"].isna(),                 # mean = 0 -> no demand -> not classified
        stats["cv"] <= x_threshold,
        stats["cv"] <= y_threshold,
    ]
    stats["XYZ"] = np.select(conditions, ["", "", "X", "Y"], default="Z")
    return stats


def _xyz_stats(
    df: pd.DataFrame,
    data_mode: DataMode,
    x_quantile: float,
    y_quantile: float,
    manual_thresholds: Optional[Tuple[float, float]],
):
    if data_mode not in ("dense", "sparse", "lifecycle"):
        raise ValueError(f"data_mode must be 'dense', 'sparse' or 'lifecycle', not '{data_mode}'")

    df_out, period_sum = _prepare_period_sum(df)
    source = _build_stats_source(period_sum, data_mode)
    stats = _compute_sku_stats(source)

    # SKUs dropped from the stats source (lifecycle: no demand at all) are kept as unclassified
    stats = pd.DataFrame({"SKU": period_sum["SKU"].unique()}).merge(stats, on="SKU", how="left")
    stats["n_periods"] = stats["n_periods"].fillna(0).astype(int)

    x, y, method = _compute_thresholds(stats, x_quantile, y_quantile, manual_thresholds)
    print(f"--- XYZ thresholds ({data_mode}, {method}) ---")
    print(f"x_threshold: {x:.4f}")
    print(f"y_threshold: {y:.4f}")
    print("---------------------------------------------")

    stats = _classify(stats, x, y)
    return df_out, period_sum, stats, x, y


# =====================================================================
# Public functions
# =====================================================================
def assign_xyz_groups(
    df: pd.DataFrame,
    data_mode: DataMode = "dense",
    x_quantile: float = X_QUANTILE,
    y_quantile: float = Y_QUANTILE,
    manual_thresholds: Optional[Tuple[float, float]] = None,
) -> pd.DataFrame:
    """
    Long output: original rows + ['XYZ', 'CV', 'x_threshold', 'y_threshold'].

    Note on 'n_periods': in dense mode it is the total number of periods for every SKU;
    in sparse mode it is the number of (SKU, Period) rows PRESENT in the data (these can
    contain zeros); in lifecycle mode it is the length of the SKU's active window.
    """
    df_out, _, stats, x, y = _xyz_stats(df, data_mode, x_quantile, y_quantile, manual_thresholds)

    cols_to_merge = stats[["SKU", "XYZ", "cv"]].rename(columns={"cv": "CV"})
    merged = df_out.merge(cols_to_merge, on="SKU", how="left", validate="m:1")
    merged["XYZ"] = merged["XYZ"].fillna("")
    merged["x_threshold"] = x
    merged["y_threshold"] = y

    disallowed = set(merged["XYZ"].unique()) - {"", "X", "Y", "Z"}
    if disallowed:
        raise RuntimeError(f"Unexpected XYZ values found: {disallowed}")

    new_cols = ["XYZ", "CV", "x_threshold", "y_threshold"]
    final_cols = [c for c in df.columns if c not in new_cols] + new_cols
    return merged[final_cols].copy()


def assign_xyz_groups_wide(
    df: pd.DataFrame,
    data_mode: DataMode = "dense",
    x_quantile: float = X_QUANTILE,
    y_quantile: float = Y_QUANTILE,
    manual_thresholds: Optional[Tuple[float, float]] = None,
) -> pd.DataFrame:
    """
    Wide output (one row per SKU), identical layout to the Excel 'XYZ Table':
    'SKU', [Period_1 (oldest)] ... [Period_N (newest)], 'XYZ', 'CV'.
    Uses exactly the same statistics and thresholds as assign_xyz_groups().
    """
    _, period_sum, stats, _, _ = _xyz_stats(df, data_mode, x_quantile, y_quantile, manual_thresholds)

    pivot = pd.pivot_table(
        period_sum, values="Value", index="SKU", columns="Period",
        aggfunc="sum", fill_value=0.0,
    ).sort_index(axis=1)
    period_cols = list(pivot.columns)

    final_df = pivot.reset_index().merge(
        stats[["SKU", "XYZ", "cv"]].rename(columns={"cv": "CV"}),
        on="SKU", how="left", validate="1:1",
    )
    final_df.columns.name = None
    final_df["XYZ"] = final_df["XYZ"].fillna("")
    return final_df[["SKU"] + period_cols + ["XYZ", "CV"]].copy()


# =====================================================================
# Saving in the same folder as the Python (py or ipynb) file
# =====================================================================
def save_file(data: pd.DataFrame, name: str) -> None:
    """Saves a DataFrame to Excel; uses xlsxwriter if installed, otherwise openpyxl."""
    data_dump = os.path.join(os.getcwd(), f"{name}.xlsx")
    try:
        import xlsxwriter  # noqa: F401
        engine = "xlsxwriter"
    except ModuleNotFoundError:
        print("⚠️  xlsxwriter not found. Falling back to openpyxl.")
        engine = "openpyxl"

    with pd.ExcelWriter(data_dump, engine=engine) as writer:
        data.to_excel(writer, sheet_name=name[:31], index=False)
    print(f"✅ Data successfully saved as: {data_dump}")


# =====================================================================
# Execution
# =====================================================================
xyz_table = load_long_data(file_path, value_field)
if value_field == 'Stock':
    xyz_table = keep_month_end_snapshot(xyz_table)

# Rename quantity column to the default input column 'Value'
xyz_input = xyz_table.rename(columns={value_field: 'Value'})[['SKU', 'Period', 'Value']].copy()

# Aggregate on SKU/Period level
xyz_input = xyz_input.groupby(['SKU', 'Period'], as_index=False)['Value'].sum()

# XYZ classification
df_result = assign_xyz_groups(xyz_input, data_mode=DATA_MODE, manual_thresholds=MANUAL_THRESHOLDS)
df_wide_result = assign_xyz_groups_wide(xyz_input, data_mode=DATA_MODE, manual_thresholds=MANUAL_THRESHOLDS)

# Save output files
save_file(df_result, "xyz_" + value_field)
save_file(df_wide_result, "xyz_wide_" + value_field)
```

#### Macierz ABC-XYZ oraz porównanie zapasu i sprzedaży w Pythonie
##### Wyjaśnienie
Ten skrypt łączy wyniki dwóch powyższych skryptów. Odczytuje je z folderu roboczego, więc najpierw uruchom:
1. ABC z `value_field = 'Stock'`
2. ABC z `value_field = 'Sales'`
3. XYZ z `value_field = MATRIX_VALUE_FIELD`

**Wyniki** (wszystkie w pliku `abc_xyz_report.xlsx`):
- **Stock_vs_Sales:** dla każdego okresu oznacza `Stock-out risk` (ryzyko braku towaru: Sprzedaż A / Zapas C) oraz `Write-off risk (shelf life)` (ryzyko utylizacji z powodu terminu przydatności: Sprzedaż C / Zapas A). SKU nieobecne po jednej stronie ma tam wartość zerową i jest traktowane jako C. Etykiety ryzyka w wynikach Pythona pozostają angielskie, ponieważ kod nie został zmieniony.
- **Segments:** ABC (analiza zagregowana) + XYZ dla każdego SKU, np. `AX`.
- **Matrix:** liczba SKU w każdej komórce ABC × XYZ (`n/a` = brak popytu).

**Typowa interpretacja:**

| | X (stabilne) | Y (mniej stabilne) | Z (niestabilne) |
|---|---|---|---|
| **A** | automatyczne uzupełnianie, niski zapas bezpieczeństwa | prognoza + przegląd | wysoka uwaga, zapas bezpieczeństwa lub produkcja na zamówienie |
| **B** | automatyzacja | przegląd okresowy | decyzja indywidualna |
| **C** | automatyzacja, zamówienia hurtowe | przegląd okresowy | produkcja na zamówienie / kandydat do wycofania |

##### Kod Python
``` python
import os
import numpy as np
import pandas as pd

OUTPUT_DIR = os.getcwd()
MATRIX_VALUE_FIELD = 'Sales'   # which ABC/XYZ results build the matrix


def read_result(name: str) -> pd.DataFrame:
    path = os.path.join(OUTPUT_DIR, f"{name}.xlsx")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found – run the ABC/XYZ script for this data first.")
    return pd.read_excel(path, sheet_name=name[:31], dtype={'SKU': str, 'Period': str})


def compare_stock_sales(abc_stock: pd.DataFrame, abc_sales: pd.DataFrame) -> pd.DataFrame:
    """Compare ABC classes of stock and sales for the same SKU and period."""
    common = sorted(set(abc_stock['Period']) & set(abc_sales['Period']))
    if not common:
        raise ValueError("Stock and sales results have no common periods.")

    s = abc_stock.loc[abc_stock['Period'].isin(common), ['SKU', 'Period', 'ABC_Group']] \
        .rename(columns={'ABC_Group': 'ABC_Stock'})
    d = abc_sales.loc[abc_sales['Period'].isin(common), ['SKU', 'Period', 'ABC_Group']] \
        .rename(columns={'ABC_Group': 'ABC_Sales'})

    cmp = s.merge(d, on=['SKU', 'Period'], how='outer', validate='1:1')
    # SKU missing on one side has zero value there -> class C
    cmp[['ABC_Stock', 'ABC_Sales']] = cmp[['ABC_Stock', 'ABC_Sales']].fillna('C')

    cmp['Risk'] = np.select(
        [(cmp['ABC_Sales'] == 'A') & (cmp['ABC_Stock'] == 'C'),
         (cmp['ABC_Sales'] == 'C') & (cmp['ABC_Stock'] == 'A')],
        ['Stock-out risk', 'Write-off risk (shelf life)'],
        default='',
    )
    return cmp.sort_values(['Period', 'Risk', 'SKU'], ascending=[True, False, True]).reset_index(drop=True)


def abc_xyz_matrix(abc_total: pd.DataFrame, xyz_wide: pd.DataFrame):
    """Combine aggregate ABC and XYZ per SKU; return segments and the count matrix."""
    seg = abc_total[['SKU', 'ABC_Group']].merge(
        xyz_wide[['SKU', 'XYZ']], on='SKU', how='outer', validate='1:1'
    )
    seg['ABC_Group'] = seg['ABC_Group'].fillna('C')
    seg['XYZ'] = seg['XYZ'].fillna('')            # blank cells are read back as NaN
    seg['Segment'] = seg['ABC_Group'] + seg['XYZ'].replace('', '-')

    matrix = pd.crosstab(
        seg['ABC_Group'], seg['XYZ'].replace('', 'n/a'),
        margins=True, margins_name='Total',
    )
    matrix = matrix.reindex(
        index=['A', 'B', 'C', 'Total'], columns=['X', 'Y', 'Z', 'n/a', 'Total'], fill_value=0
    )
    matrix.columns.name = None
    matrix = matrix.reset_index().rename(columns={'ABC_Group': 'ABC'})
    return seg.sort_values(['Segment', 'SKU']).reset_index(drop=True), matrix


def save_sheets(sheets: dict, name: str) -> None:
    path = os.path.join(OUTPUT_DIR, f"{name}.xlsx")
    try:
        import xlsxwriter  # noqa: F401
        engine = "xlsxwriter"
    except ModuleNotFoundError:
        engine = "openpyxl"
    with pd.ExcelWriter(path, engine=engine) as writer:
        for sheet_name, data in sheets.items():
            data.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    print(f"✅ Report saved as: {path}")


# Execution
abc_stock = read_result('abc_Stock')
abc_sales = read_result('abc_Sales')
comparison = compare_stock_sales(abc_stock, abc_sales)
print(comparison['Risk'].replace('', 'No risk').value_counts().to_string())

abc_total = read_result('abc_total_' + MATRIX_VALUE_FIELD)
xyz_wide = read_result('xyz_wide_' + MATRIX_VALUE_FIELD)
segments, matrix = abc_xyz_matrix(abc_total, xyz_wide)
print(matrix.to_string(index=False))

save_sheets(
    {'Stock_vs_Sales': comparison, 'Segments': segments, 'Matrix': matrix},
    'abc_xyz_report',
)
```

#### Słownik funkcji Excel PL – EN
Separator argumentów w polskim Excelu to średnik `;`, a separator dziesiętny to przecinek `,`.

| Polski Excel | Angielski Excel |
|---|---|
| JEŻELI | IF |
| JEŻELI.BŁĄD | IFERROR |
| CZY.BŁĄD | ISERROR |
| ORAZ | AND |
| SUMA | SUM |
| SUMA.WARUNKÓW | SUMIFS |
| LICZ.JEŻELI | COUNTIF |
| LICZ.WARUNKI | COUNTIFS |
| ILE.LICZB | COUNT |
| INDEKS | INDEX |
| PODAJ.POZYCJĘ | MATCH |
| MAKS.WARUNKÓW | MAXIFS |
| MAX / MIN | MAX / MIN |
| ŚREDNIA | AVERAGE |
| ODCH.STAND.POPUL | STDEV.P |
| ODCH.STANDARDOWE.PRÓBKI | STDEV.S |
| PERCENTYL.PRZEDZ.ZAMK | PERCENTILE.INC |
| TEKST | TEXT |
| ROK / MIESIĄC | YEAR / MONTH |
| LET | LET |
| SEKWENCJA | SEQUENCE |
| FILTRUJ | FILTER |
| LICZBA.KOLUMN | COLUMNS |
| Format daty `"rrrr-mm"` | Format daty `"yyyy-mm"` |
### Animal segmentation
| Code | Animal    |
| ---- | --------- |
| AX   | Horses    |
| BX   | Horses    |
| AY   | Mad Bulls |
| AZ   | Mad Bulls |
| BY   | Mad Bulls |
| BZ   | Mad Bulls |
| CX   | Turtles   |
| CY   | Rabbits   |
| CZ   | Rabbits   |
