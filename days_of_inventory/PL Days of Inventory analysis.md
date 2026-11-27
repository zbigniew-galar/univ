### Definicje
- **CSV** - Comma-Separated Values (wartości rozdzielone przecinkami). Najpopularniejszy tekstowy format danych.
- **Dni zapasu (Days of Inventory)** - nazywane również dniami pokrycia zapasem lub dniami sprzedaży. Wybiegająca w przyszłość miara zapasów w łańcuchu dostaw, określająca liczbę dni działalności, które mogą zostać obsłużone przy użyciu zapasu dostępnego na stanie. Informacja o tym, na jak długo wystarczy nam zapasu, zakłada, że nie zostanie zakupiony ani wyprodukowany żaden dodatkowy zapas.

$$  
\text{Dni zapasu} = \frac{\text{Zapas na koniec miesiąca}}{\text{Sprzedaż w miesiącu}} \quad*30
$$
- **Rotacja zapasów (Inventory turnover)** - retrospektywna, finansowa miara zapasów, określająca, ile razy w ciągu roku obraca się kapitał zamrożony w zapasach. Czasami do obliczeń w ujęciu ilościowym stosuje się wzór nr 3, gdy zarówno koszt towaru, jak i jego cena sprzedaży znacząco zmieniają się w ciągu roku (np. benzyna).

$$  
\text{Rotacja zapasów} = \frac{\text{Koszt sprzedanych towarów}}{\text{Średni zapas według kosztu}} \quad (1)  
$$

$$  
\text{Rotacja zapasów} = \frac{\text{Sprzedaż netto}}{\text{Średni zapas w cenach sprzedaży}} \quad (2)  
$$

$$  
\text{Rotacja zapasów} = \frac{\text{Sprzedaż w sztukach}}{\text{Średni zapas w sztukach}} \quad (3)  
$$
- **Format długi i szeroki** - Format długi (wąski, skumulowany lub pionowy) oznacza, że każdy wiersz jest pojedynczą obserwacją, natomiast format szeroki (poziomy lub nieskumulowany) rozkłada zmienne na kolumny.
- **Melting (topienie)** - przekształca dane z formatu poziomego do pionowego. Funkcja melt w Pythonie. Narzędzie Transpose w Alteryx.
- **Pivoting (przestawianie)** - przekształca dane z formatu pionowego do poziomego. Tworzy kolumny z wierszy. Funkcja pivot w Pythonie. Narzędzie Cross Tab w Alteryx.
- **SKU** - Stock Keeping Unit (jednostka magazynowa). Alfanumeryczny symbol rodzaju towaru fizycznego używanego przez firmę. Podstawa zarządzania danymi podstawowymi (masterdata).
### Techniki
- **Okres z pola daty:**
``` excel
=JEŻELI(MIESIĄC(B2)<10;ROK(B2)&"-0"&MIESIĄC(B2);ROK(B2)&"-"&MIESIĄC(B2))
lub
=TEKST(B2;"rrrr-mm")
// wersja angielska
=TEXT(B2;"yyyy-mm")
```
- **Przestawianie ilorazu danych o zapasie (kolumna C) i danych o sprzedaży (kolumna D) z formatu długiego do szerokiego dla każdego SKU (kolumna B) według okresu (kolumna A), pomnożonego przez 30:**
``` excel
=SUMA.WARUNKÓW('Historia zapasów i sprzedaży'!$C$2:$C$90000;
'Historia zapasów i sprzedaży'!$B$2:$B$90000;\$A2;'Historia zapasów i sprzedaży'!$A$2:$A$90000;B\$1)
/
SUMA.WARUNKÓW('Historia zapasów i sprzedaży'!$D$2:$D$90000;
'Historia zapasów i sprzedaży'!$B$2:$B$90000;\$A2;'Historia zapasów i sprzedaży'!$A$2:$A$90000;B\$1)
*30
```
- **Dołączanie danych cenowych z kolumny B tabeli `COGS` do tabeli zapasów na podstawie SKU z kolumny B, które można znaleźć w kolumnie A tabeli `COGS`:**
``` excel
=JEŻELI.BŁĄD(INDEKS(COGS!$B$2:$B$90000;PODAJ.POZYCJĘ(B2;COGS!$A$2:$A$90000;0));0)
```
### Funkcje Excela
- **Dodaje wartości. Można dodawać pojedyncze wartości, odwołania do komórek, zakresy lub kombinację wszystkich trzech:**
``` excel
SUMA(liczba1;[liczba2];...)
```
- **Dodaje wszystkie argumenty spełniające wiele kryteriów. Sumuje wiele wierszy na podstawie przecięcia wielu kryteriów. Wartość 1 w kolumnie 1, wartość 2 w kolumnie 2 itd.:**
``` excel
SUMA.WARUNKÓW(zakres_sumy; zakres_kryteriów1; kryteria1; [zakres_kryteriów2; kryteria2]; ...)
```
- **Wyszukuje dane w tabeli lub zakresie według wierszy. Szukana wartość musi znajdować się w pierwszej kolumnie zakresu. Numer kolumny zawierającej zwracaną wartość. Użyj 0 jako ostatniego argumentu dla dokładnego dopasowania:**
``` excel
WYSZUKAJ.PIONOWO(szukana_wartość; tabela_tablica; nr_kolumny; [przeszukiwany_zakres])
```
- **Wyszukuje szukany termin w jednej kolumnie i zwraca wynik z tego samego wiersza w innej kolumnie, niezależnie od tego, po której stronie znajduje się kolumna zwracana:**
``` excel
X.WYSZUKAJ(szukana_wartość; szukana_tablica; zwracana_tablica; [jeżeli_nie_znaleziono]; [tryb_dopasowania]; [tryb_wyszukiwania])
```
- **Wyszukuje określony element w zakresie komórek, a następnie zwraca względną pozycję tego elementu w zakresie:**
``` excel
PODAJ.POZYCJĘ(szukana_wartość; przeszukiwana_tablica; [typ_porównania])
```
- **Zwraca wartość lub odwołanie do wartości z tabeli lub zakresu:**
``` excel
INDEKS(tablica; nr_wiersza; [nr_kolumny])
```
- **Wyświetla określoną wartość w przypadku błędu, np. zero `0` lub pustą komórkę `""`. Błędy są przyjacielem. Są jak sygnał bólu dający informację zwrotną. Usuwaj je tylko wtedy, gdy dogłębnie rozumiesz analizę:**
``` excel
JEŻELI.BŁĄD(wartość; wartość_jeżeli_błąd)
```
- **INDEKS z PODAJ.POZYCJĘ jako ulepszone WYSZUKAJ.PIONOWO (robi to samo co WYSZUKAJ.PIONOWO i więcej, np. przecięcia). Znajduje wartość z A2 w kolumnie A aż do A200 i wyświetla wartość z tego samego wiersza, ale z kolumny B:**
``` excel
JEŻELI.BŁĄD(INDEKS('Arkusz1'!$B$2:$B$200;PODAJ.POZYCJĘ(A2;'Arkusz1'!$A$2:$A$200;0));"")
```
- **Funkcja TEKST pozwala zmienić sposób wyświetlania liczby poprzez zastosowanie do niej formatowania za pomocą kodów formatu. Jest przydatna, gdy chcesz wyświetlić liczby w bardziej czytelnym formacie lub połączyć liczby z tekstem albo symbolami.**
``` excel
=TEKST(Wartość, którą chcesz sformatować; "Kod formatu, który chcesz zastosować")
```
### Funkcje Power BI
- **Zwraca pierwsze wyrażenie, którego wynikiem nie jest BLANK. Jeśli wynikiem wszystkich wyrażeń jest BLANK, zwracana jest wartość BLANK.:**
``` excel
COALESCE(<expression>, <expression>[, <expression>]…)
```
- **Zwraca powiązaną wartość z innej tabeli. Gdy funkcja RELATED wykonuje wyszukiwanie, sprawdza wszystkie wartości w określonej tabeli niezależnie od zastosowanych filtrów. `RELATED(<Table>[Column])` pobiera _pojedynczą wartość_ kolumny `<Column>` z tabeli powiązanej z bieżącą tabelą poprzez relację w modelu. Koncepcyjnie wykonuje wyszukiwanie od bieżącego wiersza (kontekst wiersza) do powiązanej tabeli, podążając ścieżką relacji zdefiniowaną w modelu danych. Jest przeznaczona do użycia tam, gdzie istnieje relacja jeden-do-wielu, a my znajdujemy się po stronie „wiele” (np. `Stock` wiele → `COGS` jeden).:**
``` excel
RELATED(<column>)
```
- **Zwraca wartość dla wiersza, który spełnia wszystkie kryteria określone przez jeden lub więcej warunków wyszukiwania. Wartość `result_columnName` w wierszu, w którym wszystkie pary `search_columnName` i `search_value` są dokładnie dopasowane. Jeśli nie ma dopasowania spełniającego wszystkie szukane wartości, zwracana jest wartość BLANK lub `alternateResult` (jeśli został określony). Innymi słowy, funkcja nie zwraca wartości wyszukiwania, jeśli dopasowana jest tylko część kryteriów. Jeśli wiele wierszy pasuje do szukanych wartości, a wartości w `result_columnName` dla tych wierszy są identyczne, zwracana jest ta wartość. Jeśli jednak `result_columnName` zwraca różne wartości, zwracany jest błąd lub `alternateResult` (jeśli został określony).:**

|Termin|Definicja|
|---|---|
|`result_columnName`|Nazwa istniejącej kolumny zawierającej wartość, którą chcesz zwrócić. Nie może być wyrażeniem.|
|`search_columnName`|Nazwa istniejącej kolumny. Może znajdować się w tej samej tabeli co result_columnName lub w tabeli powiązanej. Nie może być wyrażeniem. Można określić wiele par search_columnName i search_value.|
|`search_value`|Wartość wyszukiwana w search_columnName. Można określić wiele par search_columnName i search_value.|
|`alternateResult`|(Opcjonalnie) Wartość zwracana, gdy kontekst dla result_columnName został przefiltrowany do zera lub więcej niż jednej unikalnej wartości. Jeśli nie zostanie określona, funkcja zwraca BLANK, gdy result_columnName zostanie przefiltrowana do zera wartości, lub błąd, gdy w kontekście result_columnName występuje więcej niż jedna unikalna wartość.|
``` excel
LOOKUPVALUE (
    <result_columnName>,
    <search_columnName>,
    <search_value>
    [, <search2_columnName>, <search2_value>]…
    [, <alternateResult>]
)
```
- **Konwertuje wartość na tekst zgodnie z określonym formatem.:**
``` excel
FORMAT(<value>, <format_string>[, <locale_name>])
```
- **Dodaje wszystkie liczby w kolumnie.:**
``` excel
SUM(<column>)
```
- **Oblicza wyrażenie w zmodyfikowanym kontekście filtra.:**
``` excel
CALCULATE(<expression>[, <filter1> [, <filter2> [, …]]])
```
- **Stosuje wynik wyrażenia tabelarycznego jako filtry do kolumn z niepowiązanej tabeli.:**
``` excel
TREATAS(table_expression, <column>[, <column>[, <column>[,…]]]} )
```
- **Przechowuje wynik wyrażenia jako nazwaną zmienną, którą można następnie przekazać jako argument do innych wyrażeń miar. Po obliczeniu wartości wynikowych dla wyrażenia zmiennej wartości te nie zmieniają się, nawet jeśli do zmiennej odwołuje się inne wyrażenie.:**
``` excel
VAR <name> = <expression>
```
- **Zwraca wartość pustą.:**
``` excel
BLANK()
```
- **Wykonuje dzielenie i zwraca wynik alternatywny lub BLANK() w przypadku dzielenia przez 0.:**
``` excel
DIVIDE(<numerator>, <denominator> [,<alternateresult>])
```
- **Sprawdza warunek i zwraca jedną wartość, gdy jest on spełniony (`TRUE`), w przeciwnym razie zwraca drugą wartość.:**
``` excel
IF(<logical_test>, <value_if_true>[, <value_if_false>])
```
## Analiza dni zapasu w Power BI
### Kroki wykonania analizy w Power BI
1. Załaduj tabelę Sales (sprzedaż), tabelę Stock (zapas) i tabelę COGS (koszt sprzedanych towarów) jako osobne pliki Excela. Połącz SKU z tabeli Sales z tabelą COGS oraz SKU z tabeli Stock z tabelą COGS relacją wiele-do-jednego.
```
Kardynalność: Wiele do jednego
```
2. Dodaj nową kolumnę danych w tabeli Stock i tabeli Sales, pobierającą odpowiadające wartości COGS:
``` excel
COGS = RELATED(COGS[COGS])
```
lub to samo, ale z obsługą błędów (w obu tabelach, Stock i Sales, formuły są takie same):
``` excel
COGS = 
VAR RelatedCOGS = RELATED(COGS[COGS])
RETURN
    // Użyj COALESCE do obsługi przypadków, w których nie znaleziono dopasowania dla SKU
    COALESCE(RelatedCOGS, 0)

// --- Wyjaśnienie ---
// RELATED: Pobiera pojedynczą powiązaną wartość z tabeli COGS dla każdego SKU
// COALESCE: Zastępuje wartości BLANK zerem, jeśli nie ma pasującego SKU
// Ta kolumna zawiera teraz odpowiadającą kwotę COGS dla każdego wiersza tabeli Stock.
```
3. Na podstawie dostarczonej kolumny wartości jednostkowej (COGS) możemy teraz obliczyć wartość zapasu i sprzedaży jako nowe kolumny:
``` excel
Stock_Value = Stock[Stock]*Stock[COGS]
```
oraz dla tabeli Sales:
``` excel
Sales_Value = Sales[Sales]*Sales[COGS]
```
4. W obu tabelach wyodrębnij wartości roku i miesiąca jako nowe kolumny Period (okres):
``` excel
Period = FORMAT('Stock'[Date], "yyyy-MM")
```
oraz dla tabeli Sales:
``` excel
Period = FORMAT('Sales'[Date], "yyyy-MM")
```
5. Tabela Sales jest na poziomie dnia sprzedaży, dlatego musimy utworzyć dynamiczną miarę, która zagreguje całą sprzedaż na poziomie okresu:
``` excel
Sales (Monthly, No Rel) = 
CALCULATE (
    SUM ( Sales[Sales] ),
    TREATAS (
        VALUES ( Stock[SKU] ),
        Sales[SKU]
    ),
    TREATAS (
        VALUES ( Stock[Period] ),
        Sales[Period]
    )
)
// Wyjaśnienie:
// Dla bieżącego SKU i okresu pochodzących z tabeli Stock oblicz całkowitą sprzedaż
// dla tego samego SKU i okresu, mimo że między tabelami nie ma relacji.
```
6. Główna formuła miary dni zapasu powinna zostać zastosowana do tabeli Stock:
``` excel
Stock Coverage (Days, No Rel) = 
VAR StockQty =
    SUM ( Stock[Stock] )

VAR SalesQty =
    [Sales (Monthly, No Rel)]

RETURN
IF (
    SalesQty <= 0,
    BLANK(),
    DIVIDE ( StockQty, SalesQty ) * 30
)
```
### Obliczanie dni zapasu przy użyciu prymitywów transformacji danych ETL
``` mermaid
graph TD
    subgraph "Faza 1: Pozyskanie danych"
        A["input_data: Sales_Data.csv"]
        B["input_data: Stock_Data.csv"]
        C["input_data: Prices.csv"]
    end

    subgraph "Faza 2: Wycena (monetyzacja)"
        %% Wzbogacenie sprzedaży o koszt
        A --> D["join: other=Prices, on=SKU, type=left"]
        C --> D
        D --> E["formula: Mth_Sales_Value = Sales_quantity * COGS"]

        %% Wzbogacenie zapasu o koszt
        B --> F["join: other=Prices, on=SKU, type=left"]
        C --> F
        F --> G["formula: Month_End_Stock_Value = Stock_quantity * COGS"]
    end

    subgraph "Faza 3: Łączenie strumieni"
        E --> H["select: keep=SKU, Period, Mth_Sales_Value"]
        G --> I["select: keep=SKU, Period, Month_End_Stock_Value"]
        
        %% Połączenie sprzedaży i zapasu według czasu i towaru
        H --> J["join: other=Stock_Stream, on=SKU, Period, type=inner"]
        I --> J
    end

    subgraph "Faza 4: Obliczenie dni zapasu (DOI)"
        J --> K["formula: DOI_Value_Based = (Month_End_Stock_Value / Mth_Sales_Value) * 30"]
        K --> L["output_data: SKU_Period_DOI_Report.csv"]
    end
```
