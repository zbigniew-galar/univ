### Definitions
- **CSV** - Comma-Separated Values. The most common text data format.
- **Days of Inventory** - also called days of supply or days of sales a forward-looking supply chain inventory measure of number of days of business operations that can be supported with the inventory on hand. The information of for how long our supply will last assumes that no more inventory is bought or produced.
  
$$  
\text{Days of Inventory} = \frac{\text{Stock month end}}{\text{Sales of the month}} \quad*30
$$
- **Inventory turnover** - a backward-looking financial inventory measure of how many times capital frozen in inventory turns in a year. Sometimes formula no 3 is used for the calculation as quantity when both the cost of an item and its selling price change significantly during a year (i.e. gasoline).

$$  
\text{Inventory Turnover} = \frac{\text{Cost of Goods Sold}}{\text{Average Inventory at Cost}} \quad (1)  
$$

$$  
\text{Inventory Turnover} = \frac{\text{Net Sales}}{\text{Average Inventory at Selling Price}} \quad (2)  
$$

$$  
\text{Inventory Turnover} = \frac{\text{Unit Sales}}{\text{Average Inventory in Units}} \quad (3)  
$$
- **Long and wide data format** - Long (narrow or stacked or vertical) format means each row is an observation, while wide (horizontal or unstacked) format spreads variables across columns.
- **Melting** - transposes the data from horizontal to vertical format. Melt function in Python. Transpose tool in Alteryx.
- **Pivoting** - transposes the data from vertical to horizontal format. Creates columns from rows. Pivot function in Python. Cross Tab tool in Alteryx.
- **SKU** - Stock Keeping Unit. Alphanumeric symbol for a type of physical good a company uses. Basis for masterdata management.
### Techniques
- **Period from Date field:**
``` excel
=IF(MONTH(B2)<10;YEAR(B2)&"-0"&MONTH(B2);YEAR(B2)&"-"&MONTH(B2))
or
=TEXT(B2;"yyyy-mm")
// polish version
=TEKST(B2;"rrrr-mm")
```
- **Pivoting division of stock data (C column) and sales data (D column) from long to wide format per SKU (B column) by period (A column)  multiplied by 30:**
``` excel
=SUMIFS('Stock history and sales'!$C$2:$C$90000;
'Stock history and sales'!$B$2:$B$90000;$A2;'Stock history and sales'!$A$2:$A$90000;B$1)
/
SUMIFS('Stock history and sales'!$D$2:$D$90000;
'Stock history and sales'!$B$2:$B$90000;$A2;'Stock history and sales'!$A$2:$A$90000;B$1)
*30
```
- **Connecting price data from B column of `COGS` table to the stock table based on the SKUs from B column that can be found in A column of `COGS` table:**
``` excel
=IFERROR(INDEX(COGS!$B$2:$B$90000;MATCH(B2;COGS!$A$2:$A$90000;0));0)
```
### Excel Functions
- **Adds values. You can add individual values, cell references or ranges or a mix of all three:**
``` excel
SUM(number1,[number2],...)
```
- **Adds all of its arguments that meet multiple criteria. Sum many rows based on intersection of many criteria. Value 1 in column 1, value 2 in column 2 etc.:**
``` excel
SUMIFS(sum_range, criteria_range1, criteria1, [criteria_range2, criteria2], ...)
```
- **Find things in a table or a range by row. Value you want to look up must be in the first column of the range. The column number that contains the return value. Use last value as 0 for exact match:**
``` excel
VLOOKUP (lookup_value, table_array, col_index_num, [range_lookup])
```
- **Look in one column for a search term and return a result from the same row in another column, regardless of which side the return column is on:**
``` excel
XLOOKUP(lookup_value, lookup_array, return_array, [if_not_found], [match_mode], [search_mode])
```
- **Searches for a specified item in a range of cells, and then returns the relative position of that item in the range:**
``` excel
MATCH(lookup_value, lookup_array, [match_type])
```
- **Returns a value or the reference to a value from within a table or range:**
``` excel
INDEX(array, row_num, [column_num])
```
- **Show a certain value when error like zero `0` or empty cell `""`. Errors are a friend. They are like a pain signal giving feedback. Remove them only if you understand the analysis deeply:**
``` excel
IFERROR(value, value_if_error)
```
- **INDEX with MATCH as improved VLOOKUP (it does what VLOOKUP and more like intersection). Find value from A2 in the column of A up to A200 and show value from the same row but from column B:**
``` excel
IFERROR(INDEX(Sheet1'!$B$2:$B$200;MATCH(A2;'Sheet1'!$A$2:$A$200;0));"")
```
- **The TEXT function lets you change the way a number appears by applying formatting to it with format codes. It's useful in situations where you want to display numbers in a more readable format, or you want to combine numbers with text or symbols.**
``` excel
=TEXT(Value you want to format, "Format code you want to apply")
```
### Power BI functions
- **Returns the first expression that does not evaluate to BLANK. If all expressions evaluate to BLANK, BLANK is returned.:**
``` excel
COALESCE(<expression>, <expression>[, <expression>]…)
```
- **Returns a related value from another table. When the RELATED function performs a lookup, it examines all values in the specified table regardless of any filters that may have been applied.`RELATED(<Table>[Column])` fetches the _single value_ of `<Column>` from a table that is related to the current table via a model relationship. Conceptually it performs a lookup from the current row (row context) to the related table following the relationship path defined in the data model. It is designed to be used where a one-to-many relationship exists and you are on the many side (e.g., `Stock` many → `COGS` one).:**
``` excel
RELATED(<column>)
```
- **Returns the value for the row that meets all criteria specified by one or more search conditions. The value of `result_columnName` at the row where all pairs of `search_columnName` and `search_value` have an exact match. If there isn't a match that satisfies all the search values, BLANK or `alternateResult` (if specified) is returned. In other words, the function doesn't return a lookup value if only some of the criteria match. If multiple rows match the search values and the values in the `result_columnName` for these rows are identical, then that value is returned. However, if `result_columnName` returns different values, an error or `alternateResult` (if specified) is returned.:**

|Term|Definition|
|---|---|
|`result_columnName`|The name of an existing column that contains the value you want to return. It cannot be an expression.|
|`search_columnName`|The name of an existing column. It can be in the same table as result_columnName or in a related table. It cannot be an expression. Multiple pairs of search_columnName and search_value can be specified.|
|`search_value`|The value to search for in search_columnName. Multiple pairs of search_columnName and search_value can be specified.|
|`alternateResult`|(Optional) The value returned when the context for result_columnName has been filtered down to zero or more than one distinct value. If not specified, the function returns BLANK when result_columnName is filtered down to zero values or an error when there is more than one distinct value in the context for result_columnName.|
``` excel
LOOKUPVALUE (
    <result_columnName>,
    <search_columnName>,
    <search_value>
    [, <search2_columnName>, <search2_value>]…
    [, <alternateResult>]
)
```
- **Converts a value to text according to the specified format.:**
``` excel
FORMAT(<value>, <format_string>[, <locale_name>])
```
- **Adds all the numbers in a column.:**
``` excel
SUM(<column>)
```
- **Evaluates an expression in a modified filter context.:**
``` excel
CALCULATE(<expression>[, <filter1> [, <filter2> [, …]]])
```
- **Applies the result of a table expression as filters to columns from an unrelated table.:**
``` excel
TREATAS(table_expression, <column>[, <column>[, <column>[,…]]]} )
```
- **Stores the result of an expression as a named variable, which can then be passed as an argument to other measure expressions. Once resultant values have been calculated for a variable expression, those values do not change, even if the variable is referenced in another expression.:**
``` excel
VAR <name> = <expression>
```
- **Returns a blank.:**
``` excel
BLANK()
```
- **Performs division and returns alternate result or BLANK() on division by 0.:**
``` excel
DIVIDE(<numerator>, <denominator> [,<alternateresult>])
```
- **Checks a condition, and returns one value when it's `TRUE`, otherwise it returns a second value.:**
``` excel
IF(<logical_test>, <value_if_true>[, <value_if_false>])
```
## Days of Inventory analysis in Power BI
### Analysis in Power BI execution steps
1. Load Sales table, Stock table and COGS table as separate Excel files. Connect SKU from Sales to COGS and SKU from Stock to COGS as many to one relation. 
```
Cardinality: Many to one
```
2. Add new column of data in Stock table and Sales table getting the COGS corresponding values:
``` excel
COGS = RELATED(COGS[COGS])
```
or the same but with error handling (in both tables Stock and Sales the formulas are the same):
``` excel
COGS = 
VAR RelatedCOGS = RELATED(COGS[COGS])
RETURN
    // Use COALESCE to handle cases where no match is found for SKU
    COALESCE(RelatedCOGS, 0)

// --- Explanation ---
// RELATED: Fetches the single related value from COGS table for each SKU
// COALESCE: Replaces BLANK values with 0 if there's no matching SKU
// This column now holds the corresponding COGS amount for each Stock row.
```
3. Based on provided corresponding value per unit column (COGS) we can now calculate the value of the stock and sales as new columns:
``` excel
Stock_Value = Stock[Stock]*Stock[COGS]
```
and for the Sales table:
``` excel
Sales_Value = Sales[Sales]*Sales[COGS]
```
4. In both tables extract the year and month values as new Period columns:
``` excel
Period = FORMAT('Stock'[Date], "yyyy-MM")
```
and for the Sales table:
``` excel
Period = FORMAT('Sales'[Date], "yyyy-MM")
```
5. The Sales table is on the day of sales level therefore we need to create a dynamic measure that will aggregate all the sales on the period level:
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
// Explanation:
// Given the current SKU and Period coming from the Stock table, calculate total Sales  
// for the same SKU and Period, even though there is no relationship between the tables.
```
6. The main formula for the Days of Inventory measure should be applied to the Stock table:
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
### Days of Inventory calculation using ETL data transformation primitives
``` mermaid
graph TD
    subgraph "Phase 1: Data Ingestion"
        A["input_data: Sales_Data.csv"]
        B["input_data: Stock_Data.csv"]
        C["input_data: Prices.csv"]
    end

    subgraph "Phase 2: Valuation (Monetization)"
        %% Enrich Sales with Cost
        A --> D["join: other=Prices, on=SKU, type=left"]
        C --> D
        D --> E["formula: Mth_Sales_Value = Sales_quantity * COGS"]

        %% Enrich Stock with Cost
        B --> F["join: other=Prices, on=SKU, type=left"]
        C --> F
        F --> G["formula: Month_End_Stock_Value = Stock_quantity * COGS"]
    end

    subgraph "Phase 3: Merging Streams"
        E --> H["select: keep=SKU, Period, Mth_Sales_Value"]
        G --> I["select: keep=SKU, Period, Month_End_Stock_Value"]
        
        %% Join Sales and Stock by Time and Item
        H --> J["join: other=Stock_Stream, on=SKU, Period, type=inner"]
        I --> J
    end

    subgraph "Phase 4: DOI Calculation"
        J --> K["formula: DOI_Value_Based = (Month_End_Stock_Value / Mth_Sales_Value) * 30"]
        K --> L["output_data: SKU_Period_DOI_Report.csv"]
    end
```
