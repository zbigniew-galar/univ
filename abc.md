###### Analiza ABC w Excelu z użyciem formuł
1. Tabela "Stock history" to zwykle zrzut danych z systemu ERP w formacie długim. Ilość zapasu na koniec miesiąca kalendarzowego.
2. Tabela kosztu sprzedanych towarów "COGS" z cenami.
3. Skopiuj wszystkie SKU i wklej do arkusza "Table" jako wartości, a następnie usuń duplikaty.
```
Excel -> Data -> Remove Duplicates
```
4. Dodaj ceny z "COGS" dla każdego indeksu za pomocą INDEX(MATCH).
``` excel
IFERROR(INDEX(COGS!$B$2:$B$90000;MATCH(C2;COGS!$A$2:$A$90000;0));0)
```
5. Skopiuj wszystkie okresy z "Stock history" i usuń duplikaty. Wklej je transponowane jako kolumny w arkuszu "Table".
6. Użyj funkcji SUMIFS, aby uzupełnić wartość zapasu w cenach COGS dla poszczególnych SKU i okresów.
``` excel
=SUMIFS('Stock history'!$B$2:$B$90000;'Stock history'!$C$2:$C$90000;$A2;'Stock history'!$A$2:$A$90000;B$1)*$T2
```
7. W ramach analizy ABC skopiuj i wklej wartość zapasu dla pierwszego okresu do arkusza "ABC". SKU w kolumnie A, a wartości zapasu w kolumnie B. Utwórz tabelę i posortuj malejąco od największej do najmniejszej wartości według kolumny B. Dodaj nową kolumnę jako udział danej pozycji zapasu w sumie całkowitej wartości zapasu jako kolumnę C:
``` excel
B2/SUM($B$2:$B$9000)
```
8. Dodaj kolumnę sumy skumulowanej jako D, blokując wybór komórki początkowej:
``` excel
SUM(C$2:C2)
```
9. Przypisz grupy ABC na podstawie wartości sum skumulowanych z kolumny D. Analiza Pareto będzie kolejną kolumną "ABC" jako kolumną E:
``` excel
IF(D2<=0,8;"A";(IF(D2<=0,95;"B";"C")))
```
10. Skopiuj kolumny SKU i ABC i wklej je jako wartości w nowym arkuszu w celu bezpiecznego przechowywania i powtórz operacje analizy ABC.
11. Wykonaj ponownie całą analizę ABC dla danych sprzedażowych dla poszczególnych SKU i okresów.
12. Porównaj grupy ABC dla tych samych okresów dla zapasów i sprzedaży. Jeżeli SKU znajduje się w grupie A w sprzedaży i C w zapasach, może to prowadzić do braku towaru (stock-out). Jeżeli SKU znajduje się w grupie C w sprzedaży i A w zapasach, może to prowadzić do utylizacji z powodu upływu terminu przydatności.
13. Użyj formatowania warunkowego dla komórek klasyfikacji ABC, przyjmując A jako zielony, B jako żółty, a C jako czerwony, lub odwrotnie.
    Użyj `Green Fill with Dark Green Text` oraz `Yellow Fill with Dark Yellow Text` oraz `Light Red Fill with Dark Red Text`
```
Excel -> Home -> Conditional Formatting -> Highlight Cell Rules -> Text that Contains
```
