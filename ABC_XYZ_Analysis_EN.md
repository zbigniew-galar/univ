#### ABC analysis in Excel
##### Definitions
**Pareto analysis definition:**
Pareto analysis sets priorities for action based on the assumption that roughly 80 percent of problems typically result from 20 percent of the possible causes. Thus, not all possible causes of problems are equally important. Pareto analysis identifies the most critical (most frequent) causes of problems so that improvement efforts can be focused where the investment of time, effort, and money will yield the largest return.
**Pareto analysis consists of a four-step procedure:**
1. Identify categories about which to collect information. For example, specify categories that describe possible causes or types of defects. Such categories could come from a cause-and-effect analysis.
2. Gather the data and calculate the frequency of observations in each category for an appropriate time period. A check sheet could be used to guide data collection.
3. Sort the categories in descending order based on their percentages.
4. Present the data graphically

**Source:** Swink, M., Melnyk, S. and Hartley, J.L. (2024) _Managing Operations Across the Supply Chain_. New York: McGraw Hill. p. 212.

- **Cardinality** - refers to the uniqueness of values within a relationship in a data model and describes how many occurrences of one entity connect to occurrences of another entity.
- **CSV** - Comma-Separated Values. The most common text data format.
- **Long and wide data format** - Long (narrow or stacked or vertical) format means each row is an observation, while wide (horizontal or unstacked) format spreads variables across columns.
- **Pivoting** - transposes the data from vertical to horizontal format. Creates columns from rows. Pivot function in Python. Cross Tab tool in Alteryx.
- **SKU** - Stock Keeping Unit. Alphanumeric symbol for a type of physical good a company uses. Basis for masterdata management.

##### Main formula
**Boundary rule:** an SKU is classified by the cumulative share of all SKUs ranked **before** it (`D2-C2`).
- The SKU that crosses the 80 % line therefore still belongs to A.
- A single dominant SKU (for example 85 % of total value) is correctly classified as A instead of B.
- Periods with a total value of 0 put every SKU in C.

``` mermaid
flowchart TD
    A[Start] --> T{"Is total value of the period = 0?"}
    T -- Yes --> C0["Return 'C'"]
    T -- No --> B{"Is previous cumulative share D2-C2 < 0,8?"}
    B -- Yes --> CatA["Return 'A'"]
    B -- No --> C{"Is previous cumulative share D2-C2 < 0,95?"}
    C -- Yes --> CatB["Return 'B'"]
    C -- No --> CatC["Return 'C'"]
    C0 --> End[End]
    CatA --> End
    CatB --> End
    CatC --> End
```
``` excel
=IF(SUM($B:$B)=0;"C";IF(D2-C2<0,8;"A";IF(D2-C2<0,95;"B";"C")))
```

##### ABC Analysis execution steps
**ABC groups definition:**
- A - most important SKUs
- B - less important SKUs
- C - not important SKUs

**Opening data:**
- Double-click the file or use File > Open in Excel.
- If Unicode characters, dates or decimals are not displayed correctly, import via Data > Get Data > From Text/CSV. In Power Query, set the column types with right-click > Change Type > Using Locale… (for example Date / Polish for `DD.MM.YYYY` and decimal comma).
- Convert every source range into an Excel Table (Insert > Table) and name it in Table Design > Table Name. Tables expand automatically, so no hard-coded row limits are needed.

**Source table layouts (used by all steps below):**

| Table name | Columns |
|---|---|
| StockHistory | Date, SKU, Stock (quantity), Period, MonthEnd |
| SalesHistory | Date, SKU, Sales (quantity), Period |
| COGS | SKU, COGS, Duplicate |

**Period column** (data on daily granularity). Add it as a calculated column in StockHistory and SalesHistory:
``` excel
=TEXT([@Date];"yyyy-mm")
// if default language is polish
=TEXT([@Date];"rrrr-mm")
// alternative without TEXT
=IF(MONTH([@Date])<10;YEAR([@Date])&"-0"&MONTH([@Date]);YEAR([@Date])&"-"&MONTH([@Date]))
```

**MonthEnd column** (StockHistory only).
- Stock is a level, not a flow. Only the last snapshot per SKU and month may be used. Multiple rows on that same date (warehouses, batches) are still summed.
- If the dump already contains exactly one date per month, MonthEnd is 1 everywhere.
``` excel
=IF([@Date]=MAXIFS([Date];[SKU];[@SKU];[Period];[@Period]);1;0)
```
Fast alternative for very large dumps (more than about 50k rows):
1. Sort the table by SKU A→Z, Period A→Z, Date Newest→Oldest, and keep this order.
2. Add the helper column F `LatestDate`: `=IF(AND(B2=B1;D2=D1);F1;A2)`.
3. Set MonthEnd to `=IF(A2=F2;1;0)`.

**Duplicate column** (COGS table). Flags SKUs with more than one price. Excel `MATCH` and Python both use the **first** price, but duplicates should be cleaned in master data:
``` excel
=COUNTIF([SKU];[@SKU])>1
```

###### ABC analysis in Excel using formulas
**"ABC Table" sheet layout:**
- A = SKU
- B = COGS (unit price)
- C:T = periods (18 periods in this example; adjust the ranges to your period count)
- U = Total over all periods

**Steps:**
1. Prepare the "StockHistory" Table: an ERP data dump in long format, with stock quantity at the end of the calendar month (MonthEnd = 1).
2. Prepare the "COGS" Table for prices and check the Duplicate column.
3. Copy all SKUs, paste them as values into column A of the "ABC Table" sheet, and remove duplicates.
```
Excel -> Data -> Remove Duplicates
```
4. Add the price from COGS for every SKU in column B (first match, 0 if missing):
``` excel
=IFERROR(INDEX(COGS[COGS];MATCH(\$A2;COGS[SKU];0));0)
```
   SKUs with price 0 have zero value and fall into C. Review them with a filter on column B = 0.
5. Copy all periods from StockHistory and remove duplicates. Paste them transposed as headers into C1:T1.
   - Headers must stay **text** (`2024-01`). If Excel converts them to dates, format C1:T1 as Text before pasting.
6. Populate stock value with SUMIFS in C2 and fill right and down. MAX(0;…) clips negative ERP stock and net returns to 0:
``` excel
=MAX(0;SUMIFS(StockHistory[Stock];StockHistory[SKU];$A2;StockHistory[Period];C$1;StockHistory[MonthEnd];1))*\$B2
```
   Total over all periods in U2 (for the aggregate ABC run, see step 7):
``` excel
=SUM(C2:T2)
```
7. Run the ABC analysis.
   1. Copy SKU (column A) and the value column of **one period** and paste them as values into the "ABC" sheet: SKU in column A, Value in column B.
      - Classical ABC uses the value aggregated over 6–12 months, while monthly classes can flip between months. For the aggregate run, paste column U (Total) instead of a single period.
   2. Make a table and sort with two levels: Value Largest to Smallest, then SKU A to Z. The second level is the tie-breaker, so results are reproducible and identical to Python.
```
Excel -> Data -> Sort -> Add Level
```
   3. Add the share of total value as column C:
``` excel
=IF(SUM($B:$B)=0;0;B2/SUM($B:$B))
```
8. Add the cumulative share as column D by fixing the starting cell:
``` excel
=SUM(C\$2:C2)
```
9. Assign ABC groups in column E. `D2-C2` is the cumulative share of all SKUs ranked before the current one:
``` excel
=IF(SUM($B:$B)=0;"C";IF(D2-C2<0,8;"A";IF(D2-C2<0,95;"B";"C")))
```
10. Copy the SKU and ABC columns and paste them as values into a new sheet for safe keeping, named for example "ABC Stock 2024-01" (SKU in A, ABC in B). Repeat steps 7–9 for every period. Name the aggregate run, for example, "ABC Stock Total".
11. Redo the entire ABC analysis for sales data per SKU and period.
   - Use the SalesHistory Table without the MonthEnd criterion, because sales are a flow and all rows are summed:
``` excel
=MAX(0;SUMIFS(SalesHistory[Sales];SalesHistory[SKU];$A2;SalesHistory[Period];C$1))*\$B2
```
   - Save the results as "ABC Sales 2024-01" … and "ABC Sales Total".
12. Compare ABC groups for the **same period** for stock and sales in a "Compare" sheet.
   - Column A: the union of SKUs from both result sheets, with duplicates removed.
   - An SKU missing on one side has zero value there and is treated as C.
``` excel
// B2 – ABC Stock
=IFERROR(INDEX('ABC Stock 2024-01'!$B:$B;MATCH(\$A2;'ABC Stock 2024-01'!$A:$A;0));"C")
// C2 – ABC Sales
=IFERROR(INDEX('ABC Sales 2024-01'!$B:$B;MATCH(\$A2;'ABC Sales 2024-01'!$A:$A;0));"C")
// D2 – Risk
=IF(AND(C2="A";B2="C");"Stock-out risk";IF(AND(C2="C";B2="A");"Write-off risk (shelf life)";""))
```
   - An SKU in A in sales and C in stock could lead to a stock-out.
   - An SKU in C in sales and A in stock could lead to a write-off or scrapping because of shelf life.
13. Use conditional formatting for the ABC classification cells: A as Green, B as Yellow, C as Red, or vice versa.
   Use `Green Fill with Dark Green Text`, `Yellow Fill with Dark Yellow Text` and `Light Red Fill with Dark Red Text`.
```
Excel -> Home -> Conditional Formatting -> Highlight Cell Rules -> Text that Contains
```

##### ABC analysis in Excel using Pivot Tables execution steps
1. Add the corresponding COGS value as a new calculated column "COGS" in the source Table (first match, 0 if missing):
``` excel
=IFERROR(INDEX(COGS[COGS];MATCH([@SKU];COGS[SKU];0));0)
```
2. Create a new calculated column "Value" by multiplying the quantity by COGS:
``` excel
=[@Stock]*[@COGS]
```
3. Select the source Table and create a Pivot Table:
```
Insert -> Pivot Table -> New Worksheet
```
4. Arrange the fields:
   - Drag **Period** to Filters and select a single period. Select (All) for the aggregate run.
   - Stock only: drag **MonthEnd** to Filters and select 1.
   - Drag **SKU** to Rows.
   - Drag **Value** to Values **three times**. You get three columns: B = Sum of Value, C = running total, D = share.
5. Set the value display options:
   - Second Value field (column C): right-click > Show Values As > % Running Total In… > SKU.
   - Third Value field (column D): right-click > Show Values As > % of Column Total.
```
Sum of Value (Mouse Right click) -> Show Values As -> % Running Total In... -> SKU
Sum of Value2 (Mouse Right click) -> Show Values As -> % of Column Total
```
6. Turn off grand totals so that no total row gets a class:
```
PivotTable Design -> Grand Totals -> Off for Rows and Columns
```
7. Sort the Row Labels descending by the plain "Sum of Value" field:
```
Row Labels (Sort button click) -> More Sort Options -> Descending (Z to A) by: -> Sum of Value
```
8. Exclude negative-value SKUs, which is equivalent to clipping them to 0. The totals and percentages are then recalculated on the visible SKUs. SKUs without a class are treated as C.
```
Row Labels (Filter button click) -> Value Filters -> Sum of Value -> is greater than -> 0
```
9. Add a formula column E next to the pivot, starting in the first data row of the pivot. With two report filters this is row 5; with one filter (Sales) it is row 4. Fill it down well beyond the maximum number of SKUs. When you change the Period filter, the ABC analysis updates dynamically:
``` excel
=IF(A5="";"";IF(ISERROR(C5);"C";IF(C5-D5<0,8;"A";IF(C5-D5<0,95;"B";"C"))))
```

#### XYZ Analysis in Excel
##### Definitions
- **Coefficient of Variation (CV)** - a dispersion measure. The ratio of the standard deviation and the mean. This document uses the population version in both Excel (`STDEV.P`) and Python (`ddof=0`).
Population coefficient of variation: $$ CV = \frac{\sigma}{\mu} $$Sample coefficient of variation: $$ CV = \frac{s}{\bar{x}} $$
- **CSV** - Comma-Separated Values. The most common text data format.
- **Decile** - a ten group quantile. Values that divide a data set, ordered from smallest to largest, into ten equal parts, representing 10% of the data points in each segment.
- **Distribution** - describes the possible values of a random variable and how often each value occurs within a dataset. It provides a framework for understanding the frequency, likelihood, and spread of different outcomes.
- **Histogram** - a visual representation of the distribution of quantitative data. A diagram consisting of rectangles whose area is proportional to the frequency of a variable and whose width is equal to the class interval.
- **Long and wide data format** - Long (narrow or stacked or vertical) format means each row is an observation, while wide (horizontal or unstacked) format spreads variables across columns.
- **Median** - the second of four group quantiles, or the second quartile. The value that divides a data set, ordered from smallest to largest, into two equal parts, representing 50% of the data points in each segment.
- **Melting** - transposes the data from horizontal to vertical format. Melt function in Python. Transpose tool in Alteryx.
- **Quartile** - a four group quantile. Values that divide a data set, ordered from smallest to largest, into four equal parts, representing 25% of the data points in each segment.
- **Quantile** - a point that divides a dataset into equal-sized subgroups, such that a certain percentage of the data falls below that point. Common quantiles have special names, such as quartiles (four groups), deciles (ten groups), and percentiles (100 groups).
- **Percentile** - a hundred group quantile. Values that divide a data set, ordered from smallest to largest, into a hundred equal parts, representing 1% of the data points in each segment. Excel `PERCENTILE.INC` equals pandas `quantile()` (linear interpolation).
- **Pivoting** - transposes the data from vertical to horizontal format. Creates columns from rows. Pivot function in Python. Cross Tab tool in Alteryx.
- **Standard deviation** - a statistical measure of data spread around the mean, indicating how much individual data points vary from the average.
Population standard deviation:
$$
\sigma =\sqrt{\frac{\sum_{i=1}^{N} (x_i - \mu)^2}{N}}
$$
Sample standard deviation:
$$
s = \sqrt{\frac{\sum_{i=1}^{n} (x_i - \bar{x})^2}{n-1}}
$$
- **Variance** - a statistical measure of the _spread or dispersion_ of data points in a set relative to their mean (average).
Population variance: $$ \sigma^2 = \frac{\sum_{i=1}^{N} (x_i - \mu)^2}{N} $$ Sample variance: $$ s^2 = \frac{\sum_{i=1}^{n} (x_i - \bar{x})^2}{n-1} $$
- **SKU** - Stock Keeping Unit. Alphanumeric symbol for a type of physical good a company uses. Basis for masterdata management.

##### XYZ analysis in Excel
###### Main formula
**Thresholds:**
- `$W$2` = x_threshold and `$X$2` = y_threshold (see step 7). The default is the 33rd and 66th percentile of CV.
- Fixed values such as 2,16 / 2,4 are cut-offs read from the histogram of **one specific dataset**. They are not general rules. Textbook defaults are X ≤ 0,5 and Y ≤ 1,0.
- SKUs without demand (mean = 0) get a blank CV and are **not classified**. They are not "stable".

``` mermaid
flowchart TD
    A[Start] --> M{"Is CV blank (mean = 0)?"}
    M -- Yes --> N["Return blank (no demand)"]
    M -- No --> B{"Is T2 <= x_threshold?"}
    B -- Yes --> X["Return 'X'"]
    B -- No --> C{"Is T2 <= y_threshold?"}
    C -- Yes --> Y["Return 'Y'"]
    C -- No --> Z["Return 'Z'"]
    N --> End[End]
    X --> End
    Y --> End
    Z --> End
```
``` excel
=IF(T2="";"";IF(T2<=$W$2;"X";IF(T2<=$X$2;"Y";"Z")))
```

###### XYZ Analysis execution steps
**XYZ groups definition:**
- X - stable SKUs
- Y - less stable SKUs
- Z - not stable SKUs
- blank - no demand in the analysed horizon (not classified)

**Opening data:**
Same as in the ABC analysis: Get Data with Change Type Using Locale if dates or decimals are misread, and convert the sources into the Tables StockHistory / SalesHistory (including the Period and MonthEnd columns).

###### XYZ analysis in Excel execution steps
**"XYZ Table" sheet layout:**
- A = SKU
- B:S = quantity per period (18 periods)
- T = CV
- U = XYZ
- W1/W2 = x_threshold
- X1/X2 = y_threshold

XYZ always uses **quantity**, not value.

**Steps:**
1. Prepare the "StockHistory" Table: an ERP data dump in long format, with stock quantity at the end of the calendar month (MonthEnd = 1).
2. Copy all SKUs, paste them into column A of the "XYZ Table" sheet as values, and remove duplicates.
```
Excel -> Data -> Remove Duplicates
```
3. Copy all periods from StockHistory and remove duplicates. Paste them transposed into B1:S1 as **text** headers.
4. Populate stock quantity in B2 with SUMIFS and fill right and down. Missing SKU/period combinations return 0 (dense data), and negative values are clipped to 0:
``` excel
=MAX(0;SUMIFS(StockHistory[Stock];StockHistory[SKU];$A2;StockHistory[Period];B$1;StockHistory[MonthEnd];1))
// for
