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
// for sales data
=MAX(0;SUMIFS(SalesHistory[Sales];SalesHistory[SKU];$A2;SalesHistory[Period];B$1))
```
5. Calculate the coefficient of variation in column T. As the data source, use the quantity for every period per SKU.
   - **Which standard deviation:** Use the population standard deviation (`STDEV.P`), the same as Python `ddof=0`.
     - The population version answers the question: how much did this SKU's sales _actually_ vary during these 18 months?
     - The sample version (`STDEV.S`) is the standard for _inferential statistics_. It provides an **unbiased estimator** of the true, underlying population variance.
     - With 18 periods the difference is about 3 %. It only matters with fixed thresholds, but use the same version everywhere.
   - **Zero mean:** returns blank text. `PERCENTILE.INC` ignores text, so these SKUs do not distort the thresholds.
``` excel
=IF(AVERAGE(B2:S2)=0;"";STDEV.P(B2:S2)/AVERAGE(B2:S2))
```
   Optional lifecycle variant (Excel 365). CV is calculated only between the first and last period with demand, so pre-launch and post-discontinuation zeros do not push new or phased-out SKUs into Z. SKUs with fewer than 2 active periods stay blank:
``` excel
=LET(r;B2:S2;idx;SEQUENCE(1;COLUMNS(r));
 IF(SUM(r)=0;"";
 LET(nz;FILTER(idx;r<>0);w;FILTER(r;(idx>=MIN(nz))*(idx<=MAX(nz)));
 IF(COUNT(w)<2;"";STDEV.P(w)/AVERAGE(w)))))
```
6. Select the CV column and create a histogram chart in the "Charts" sheet to find the best boundary conditions for the XYZ groups. Blank CVs are ignored.
7. Calculate the thresholds.
   - X is the 33rd percentile and Y is the 66th percentile of the CV population, with a fallback to 0,5 / 1,0 when the 66th percentile is 0 or no CV exists. This is identical to the Python logic.
   - W1 = "x_threshold", X1 = "y_threshold":
``` excel
// W2 – x_threshold
=IFERROR(IF(PERCENTILE.INC($T:$T;0,66)=0;0,5;PERCENTILE.INC($T:$T;0,33));0,5)
// X2 – y_threshold
=IFERROR(IF(PERCENTILE.INC($T:$T;0,66)=0;1;PERCENTILE.INC($T:$T;0,66));1)
```
   - Manual version: type the values read from the histogram directly into W2 and X2. For example 0,5 / 1 (textbook), or 2,16 / 2,4 (cut-offs of one specific dataset).
8. Calculate the XYZ groups in column U:
``` excel
=IF(T2="";"";IF(T2<=$W$2;"X";IF(T2<=$X$2;"Y";"Z")))
```
9. Use conditional formatting for the XYZ classification cells: X as Green, Y as Yellow, Z as Red, or vice versa.
```
Excel -> Home -> Conditional Formatting -> Highlight Cell Rules -> Text that Contains
```
10. Build the ABC-XYZ matrix in a "Matrix" sheet. Use the aggregate (Total) ABC run of the same data source.
``` excel
// A = SKU (unique list), B2 – ABC
=IFERROR(INDEX('ABC Sales Total'!$B:$B;MATCH(\$A2;'ABC Sales Total'!$A:$A;0));"C")
// C2 – XYZ (&"" prevents an empty cell from returning 0)
=IFERROR(INDEX('XYZ Table'!$U:$U;MATCH(\$A2;'XYZ Table'!$A:$A;0))&"";"")
// D2 – Segment
=B2&C2
// Grid: F2:F4 = A, B, C; G1:I1 = X, Y, Z; G2 filled right and down
=COUNTIFS($B:$B;$F2;$C:$C;G$1)
```

###### XYZ analysis in Excel using Pivot Tables execution steps
1. Select the source Table and create a Pivot Table:
```
Insert -> Pivot Table -> New Worksheet
```
2. Arrange the fields:
   - Stock only: drag **MonthEnd** to Filters and select 1.
   - Drag **SKU** to Rows and **Period** to Columns.
   - Drag the **quantity** field (Stock or Sales, not Value) to Values as Sum.
3. Turn off grand totals, so that the total column is not included in the CV range:
```
PivotTable Design -> Grand Totals -> Off for Rows and Columns
```
4. Show empty cells as 0. `AVERAGE` and `STDEV.P` ignore blanks, so without this setting missing periods would be skipped (sparse) instead of counted as zero demand (dense, as in Python):
```
PivotTable Analyze -> Options -> Layout & Format -> For empty cells show: 0
```
5. Calculate the coefficient of variation in column U, next to the pivot, leaving column T empty as a gap.
   - Start in the first data row (row 5 in this layout) and fill down well beyond the maximum number of SKUs.
   - B5:S5 covers 18 periods; adjust it to your period count.
   - Excel 365 version, which clips negative net values to 0:
``` excel
=IF(A5="";"";LET(r;IF(B5:S5<0;0;B5:S5);IF(AVERAGE(r)=0;"";STDEV.P(r)/AVERAGE(r))))
```
   - Without LET (only when the data has no negative values):
``` excel
=IF(A5="";"";IF(AVERAGE(B5:S5)=0;"";STDEV.P(B5:S5)/AVERAGE(B5:S5)))
```
6. Select the CV column and create a histogram chart in the "Charts" sheet to find the best boundary conditions for the XYZ groups.
7. Calculate the thresholds in X2 / Y2, with labels in X1 / Y1:
``` excel
// X2 – x_threshold
=IFERROR(IF(PERCENTILE.INC($U:$U;0,66)=0;0,5;PERCENTILE.INC($U:$U;0,33));0,5)
// Y2 – y_threshold
=IFERROR(IF(PERCENTILE.INC($U:$U;0,66)=0;1;PERCENTILE.INC($U:$U;0,66));1)
```
8. Calculate the XYZ groups in column V:
``` excel
=IF(U5="";"";IF(U5<=$X$2;"X";IF(U5<=$Y$2;"Y";"Z")))
```
9. Use conditional formatting for the XYZ classification cells: X as Green, Y as Yellow, Z as Red, or vice versa.
```
Excel -> Home -> Conditional Formatting -> Highlight Cell Rules -> Text that Contains
```

#### ABC Analysis in Python
##### Explanation
The Python code performs the analysis for all periods provided in long format, plus one aggregate run over all periods.

**Input files** (semicolon-separated, decimal comma):
- `Sales.csv` or `Stock.csv` with columns `Date;SKU;Sales` or `Date;SKU;Stock`
- `COGS.csv` with columns `SKU;COGS`

**Processing:**
- Dates are parsed with an explicit `DATE_FORMAT`, so day and month are never swapped silently.
- For stock, only the month-end snapshot per SKU is kept.
- Duplicate COGS SKUs keep the first price, the same as Excel `MATCH`.
- Negative SKU/period values are clipped to 0.
- Internally the classification uses the schema `('SKU', 'Period', 'Value')`. Period is in `YYYY-MM` format.

**Output:**
- `abc_<Sales|Stock>.xlsx` (per period)
- `abc_total_<Sales|Stock>.xlsx` (aggregate)

Edit the configuration block and run once for `Stock` and once for `Sales`:
``` python
# Configuration:
value_field = 'Sales'   # 'Sales' or 'Stock'
input_dir = "C:/Python repositories/Test 2/data/input_data/"
DATE_FORMAT = '%d.%m.%Y'  # '%Y-%m-%d' for ISO dates
```
##### Python code
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

#### XYZ Analysis in Python
##### Explanation
The Python code performs the analysis over all periods provided in long format. XYZ always uses **quantity**.

**Input file:** `Sales.csv` or `Stock.csv` with columns `Date;SKU;Sales` or `Date;SKU;Stock`. The same parsing rules as in the ABC script apply: explicit date format, month-end snapshot for stock, negative values clipped to 0. Internally the schema is `('SKU', 'Period', 'Value')`.

**Statistics:**
- Population standard deviation (`ddof=0`), identical to Excel `STDEV.P`.
- Thresholds are the 33rd and 66th percentile (`PERCENTILE.INC`) of all SKUs with demand.
- Fallback to 0,5 / 1,0 when the 66th percentile is 0 or no eligible SKU exists.
- SKUs with zero mean are not classified (blank).

**`DATA_MODE` options:**
- `"dense"` (default, identical to the Excel table): missing periods are counted as 0.
- `"sparse"`: only the periods present in the data are used.
- `"lifecycle"`: dense, but only between each SKU's first and last period with demand. This is identical to the Excel 365 lifecycle formula.

**Output:**
- `xyz_<Sales|Stock>.xlsx` (long format)
- `xyz_wide_<Sales|Stock>.xlsx` (one row per SKU)

Both outputs come from the same calculation, so they always contain identical classes.
``` python
# Configuration:
value_field = 'Sales'
file_path = "C:\\Python repositories\\Education project\\src\\data\\input\\" + value_field + ".csv"
DATA_MODE = 'dense'
MANUAL_THRESHOLDS = None   # e.g. (0.5, 1.0) textbook or (2.16, 2.4) read from a histogram
```
##### Python code
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

#### ABC-XYZ Matrix and Stock vs Sales Comparison in Python
##### Explanation
This script combines the outputs of the two scripts above. It reads them from the working folder, so run them first:
1. ABC with `value_field = 'Stock'`
2. ABC with `value_field = 'Sales'`
3. XYZ with `value_field = MATRIX_VALUE_FIELD`

**Outputs** (all in `abc_xyz_report.xlsx`):
- **Stock_vs_Sales:** per period, flags `Stock-out risk` (Sales A / Stock C) and `Write-off risk (shelf life)` (Sales C / Stock A). An SKU missing on one side has zero value there and is treated as C.
- **Segments:** ABC (aggregate run) + XYZ per SKU, for example `AX`.
- **Matrix:** count of SKUs per ABC × XYZ cell (`n/a` = no demand).

**Typical interpretation:**

| | X (stable) | Y (less stable) | Z (not stable) |
|---|---|---|---|
| **A** | automate replenishment, low safety stock | forecast + review | high attention, safety stock or make-to-order |
| **B** | automate | periodic review | case-by-case |
| **C** | automate, bulk ordering | periodic review | make-to-order / delisting candidate |

##### Python code
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
