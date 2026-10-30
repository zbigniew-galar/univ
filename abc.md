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

##### Definitions
**Pareto analysis definition:**
Pareto analysis sets priorities for action based on the assumption that roughly 80 percent of problems typically result from 20 percent of the possible causes. Thus, not all possible causes of problems are equally important. Pareto analysis identifies the most critical (most frequent) causes of problems so that improvement efforts can be focused where the investment of time, effort, and money will yield the largest return.
**Pareto analysis consists of a four-step procedure:**
1. Identify categories about which to collect information. For example, specify categories that describe possible causes or types of defects. Such categories could come from a cause-and-effect analysis.
2. Gather the data and calculate the frequency of observations in each category for an appropriate time period. A check sheet could be used to guide data collection.
3. Sort the categories in descending order based on their percentages.
4. Present the data graphically

**Source:** Swink, M., Melnyk, S. and Hartley, J.L. (2024) _Managing Operations Across the Supply Chain_. New York: McGraw Hill. p. 212.

- **Cardinality** -  refers to the uniqueness of values within a relationship in a data model and describes how many occurrences of one entity connect to occurrences of another entity.
- **CSV** - Comma-Separated Values. The most common text data format.
- **Long and wide data format** - Long (narrow or stacked or vertical) format means each row is an observation, while wide (horizontal or unstacked) format spreads variables across columns.
- **Pivoting** - transposes the data from vertical to horizontal format. Creates columns from rows. Pivot function in Python. Cross Tab tool in Alteryx.
- **SKU** - Stock Keeping Unit. Alphanumeric symbol for a type of physical good a company uses. Basis for masterdata management.
##### Main formula
``` mermaid
flowchart TD
    A[Start] --> B{Is F2 <= 0,8?}
    B -- Yes --> CatA["Return 'A'"]
    B -- No --> C{Is F2 <= 0,95?}
    C -- Yes --> CatB["Return 'B'"]
    C -- No --> CatC["Return 'C'"]
    CatA --> End[End]
    CatB --> End
    CatC --> End
```
``` excel
=IF(C2<=0,8;"A";IF(C2<=0,95;"B";"C"))
```
##### ABC Analysis execution steps
**ABC groups definition:**
- A - most important SKUs
- B - less important SKUs
- C - not important SKUs

**Opening data:**
Double-click it or use File > Open in Excel. If Unicode characters don't display correctly, import it via Excel's Data tab > Get Data > From Text/CSV.
###### ABC analysis in Excel using formulas
1. "Stock history" table usually as ERP data dump in long format. Stock quantity at the end of the calendar month.
2. Cost of Goods Sold "COGS" table for prices.
3. Copy all SKUs and paste to "Table" sheet as values and remove duplicates. 
```
Excel -> Data -> Remove Duplicates
```
4. Add prices from "COGS" for every index via INDEX(MATCH).
``` excel
IFERROR(INDEX(COGS!$B$2:$B$90000;MATCH(C2;COGS!$A$2:$A$90000;0));0)
```
5. Copy all periods from "Stock history" and remove duplicates. Paste them transposed as columns in "Table". 
6. Use SUMIFS function to populate stock value in COGS per SKU and Period.
``` excel
=SUMIFS('Stock history'!$B$2:$B$90000;'Stock history'!$C$2:$C$90000;$A2;'Stock history'!$A$2:$A$90000;B$1)*$T2
```
7. For ABC analysis copy and paste value of stock for the first period to "ABC" sheet. SKU in column A and Values of stock in column B. Make a table and sort descending from Largest to Smallest value by column B. Add a new column as ratio of a particular stock in the sum of entire stock value as column C:
``` excel
B2/SUM($B$2:$B$9000)
```
8. Add cumulative SUM column as D by blocking starting cell selection:
``` excel
SUM(C$2:C2)
```
9. Assign ABC groups based on column D cumulative sum values. Pareto Analysis will be the next "ABC" column as column E:
``` excel
IF(D2<=0,8;"A";(IF(D2<=0,95;"B";"C")))
```
10. Copy SKU and ABC columns and paste them as values in the new sheet for safe keeping and repeat the ABC analysis operations. 
11. Redo the entire ABC analysis for sales data per SKU and Period. 
12. Compare ABC groups for the same periods for stock and sales. Whenever an SKU is in A in sales and C in stock it could lead to stock-out. Whenever an SKU is in C in sales and A in stock it could lead to utilization because of shelf life. 
13. Use conditional formatting for ABC classification cells with A as Green, B as Yellow and C as Red or vice versa. 
    Use `Green Fill with Dark Green Text` and `Yellow Fill with Dark Yellow Text` and `Light Red Fill with Dark Red Text`
```
Excel -> Home -> Conditional Formatting -> Highlight Cell Rules -> Text that Contains
```

