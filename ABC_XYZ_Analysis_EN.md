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
For the sales data provided on daily granularity the sales the period must be extracted from the date field:
``` excel
=IF(MONTH(B2)<10;YEAR(B2)&"-0"&MONTH(B2);YEAR(B2)&"-"&MONTH(B2))
or
=TEXT(B2;"yyyy-mm")
// if default language is polish
=TEXT(B2;"rrrr-mm")
```
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
##### ABC analysis in Excel using Pivot Tables execution steps
1. Add corresponding "COGS" values as new column in source table using VLOOKUP or INDEX MATCH.
``` excel
IFERROR(INDEX(COGS!$B$2:$B$90000;MATCH(C2;COGS!$A$2:$A$90000;0));0)
```
2. Create a new "Value" column by multiplying "COGS" by the "Stock". 
``` excel
B2*D2
```
3. After selecting source table create a Pivot Table:
```
Insert -> Pivot Table -> New Worksheet
```
4. Drag "SKU" column as Rows and "Value" column as Values and sort Row Labels descending by "Value" with "More Sort Options":
```
Row Labels (Sort button click) -> More Sort Options -> Descending (Z to A) by: -> Sum of Value
```
5. Add a running total by "SKU" via "% Running Total in":
```
Sum of Value (Mouse Right click) -> Show Values As -> % Running Total In...
```
6. Select single period in the Pivot table and add a new formula based calculated column next to the Pivot table. By changing the filter we do different ABC analysis dynamically:
``` excel
=IF(B4<=0,8;"A";IF(B4<=0,95;"B";"C"))
```
#### XYZ Analysis in Excel
##### Definitions
- **Coefficient of Variation (CV)** - a dispersion measure. A ratio of standard variation and mean.
Population coefficient of variation: $$ CV = \frac{\sigma}{\mu} $$Sample coefficient of variation: $$ CV = \frac{s}{\bar{x}} $$
- **CSV** - Comma-Separated Values. The most common text data format.
- **Decile** - a ten group quantile. Values that divide a data set, ordered from smallest to largest, into ten equal parts, representing 10% of the data points in each segment. 
- **Distribution** - describes the possible values of a random variable and how often each value occurs within a dataset. It provides a framework for understanding the frequency, likelihood, and spread of different outcomes.
- **Histogram** - a visual representation of the distribution of quantitative data. A diagram consisting of rectangles whose area is proportional to the frequency of a variable and whose width is equal to the class interval.
- **Long and wide data format** - Long (narrow or stacked or vertical) format means each row is an observation, while wide (horizontal or unstacked) format spreads variables across columns.
- **Median** - a second of four group quantile or a second quartile. Values that divide a data set, ordered from smallest to largest, into two equal parts, representing 50% of the data points in each segment. 
- **Melting** - transposes the data from horizontal to vertical format. Melt function in Python. Transpose tool in Alteryx.
- **Quartile** - a four group quantile. Values that divide a data set, ordered from smallest to largest, into four equal parts, representing 25% of the data points in each segment. 
- **Quantile** - a point that divides a dataset into equal-sized subgroups, such that a certain percentage of the data falls below that point. Common quantiles have special names, such as quartiles (four groups), deciles (ten groups), and percentiles (100 groups). 
- **Percentile** - a hundred group quantile. Values that divide a data set, ordered from smallest to largest, into hundred equal parts, representing 1% of the data points in each segment. 
- **Pivoting** - transposes the data from vertical to horizontal format. Creates columns from rows. Pivot function in Python. Cross Tab tool in Alteryx.
- **Standard deviation** - a statistical measure of data spread around the mean, indicating how much individual data points vary from the average
Population standard deviation:
$$
\sigma =\sqrt{\frac{\sum_{i=1}^{N} (x_i - \mu)^2}{N}}
$$
Sample standard deviation:
$$
s = \sqrt{\frac{\sum_{i=1}^{n} (x_i - \bar{x})^2}{n-1}}
$$
- **Variance** - a statistical measure of the _spread or dispersion_ of data points in a set relative to their mean (average).
Population variance: $$ \sigma^2 = \frac{\sum_{i=1}^{N} (x_i - \mu)^2}{N} $$ Sample variance: $$ s^2 = \frac{\sum_{i=1}^{n} (x_i - \bar{x})^2}{n-1} $$
- **SKU** - Stock Keeping Unit. Alphanumeric symbol for a type of physical good a company uses. Basis for masterdata management.
##### XYZ analysis in Excel
###### Main formula

``` mermaid
flowchart TD
    A[Start] --> B{Is V2 <= 2,16?}
    B -- Yes --> X["Return 'X'"]
    B -- No --> C{Is V2 <= 2,4?}
    C -- Yes --> Y["Return 'Y'"]
    C -- No --> Z["Return 'Z'"]
    X --> End[End]
    Y --> End
    Z --> End
```
``` excel
=IF(V2<=2,16;"X";IF(V2<=2,4;"Y";"Z"))
```
###### XYZ Analysis execution steps
**XYZ groups definition:**
- X - stable SKUs
- Y - less stable SKUs
- Z - not stable SKUs

**Opening data:**
Double-click it or use File > Open in Excel. If Unicode characters don't display correctly, import it via Excel's Data tab > Get Data > From Text/CSV.
###### XYZ analysis in Excel execution steps
1. "Stock history" table usually as ERP data dump in long format. Stock quantity at the end of the calendar month.
2. Copy all SKUs and paste to "Table" sheet as values and remove duplicates. 
```
Excel -> Data -> Remove Duplicates
```
3. Copy all periods from "Stock history" and remove duplicates. Paste them transposed as columns in "Table" sheet. 
4. Use SUMIFS function to populate stock quantity:
``` excel
=SUMIFS('Stock history'!$B$2:$B$90000;'Stock history'!$C$2:$C$90000;$A2;'Stock history'!$A$2:$A$90000;B$1)
```
3. For XYZ analysis calculate coefficient of variation as new column. As the data source use quantity for every period per SKU. Use standard deviation of the population if we have whole history of stock or sample standard deviation if we use a subset of history (the difference is not important for the business). Population answers the question of: How much did this SKU's sales _actually_ vary during these 18 months? Sample is the standard for _inferential statistics_. It provides an **unbiased estimator** of the true, underlying population variance.:
``` excel
IF(AVERAGE(C3:T3)=0;0;STDEV.P(C3:T3)/AVERAGE(C3:T3))
or 
IFERROR(STDEV.P(C3:T3)/AVERAGE(C3:T3);0)
```
6. Select CV column and create a histogram chart in "Charts" sheet to find the best boundary conditions for XYZ groups.
7. For XYZ analysis calculate XYZ groups as new column with thresholds based on the manual analysis of the histogram of the population of variability measure (CV) or based on X being the 33rd percentile and Y being between 33rd and 66th percentile of variability measure (CV) population:
``` excel
IF(U2<=2,16;"X";(IF(U2<=2,4;"Y";"Z")))
or 
IF(V3<=PERCENTILE.INC($W$3:$W$3881;0,33);"X";(IF(V3<=PERCENTILE.INC($W$3:$W$3881;0,66);"Y";"Z")))
```
8. Use conditional formatting for XYZ classification cells with X as Green, Y as Yellow and Z as Red or vice versa. 
```
Excel -> Home -> Conditional Formatting -> Highlight Cell Rules -> Text that Contains
```
###### XYZ analysis in Excel using Pivot Tables execution steps
1. After selecting source table create a Pivot Table:
```
Insert -> Pivot Table -> New Worksheet
```
2. Drag "SKU" column as Rows and "Value" column as Values and drag "Period" column as Columns in the Pivot table.
3. For XYZ analysis calculate coefficient of variation as new column. As the data source use quantity for every period per SKU. Use standard deviation of the population if we have whole history of stock or sample standard deviation if we use a subset of history (the difference is not important for the business). Population answers the question of: How much did this SKU's sales _actually_ vary during these 18 months? Sample is the standard for _inferential statistics_. It provides an **unbiased estimator** of the true, underlying population variance.:
``` excel
IF(AVERAGE(C3:T3)=0;0;STDEV.P(C3:T3)/AVERAGE(C3:T3))
or 
IFERROR(STDEV.P(C3:T3)/AVERAGE(C3:T3);0)
```
6. Select CV column and create a histogram chart in "Charts" sheet to find the best boundary conditions for XYZ groups.
7. For XYZ analysis calculate XYZ groups as new column with thresholds based on the manual analysis of the histogram of the population of variability measure (CV) or based on X being the 33rd percentile and Y being between 33rd and 66th percentile of variability measure (CV) population:
``` excel
IF(U2<=2,16;"X";(IF(U2<=2,4;"Y";"Z")))
or 
IF(V3<=PERCENTILE.INC($W$3:$W$3881;0,33);"X";(IF(V3<=PERCENTILE.INC($W$3:$W$3881;0,66);"Y";"Z")))
```
8. Use conditional formatting for XYZ classification cells with X as Green, Y as Yellow and Z as Red or vice versa. 
```
Excel -> Home -> Conditional Formatting -> Highlight Cell Rules -> Text that Contains
```
####  XYZ Analysis in Python
##### Explanation
The Python code performs the analysis for all periods provided in long format.
The input data must follow the column name schema:
`('SKU', 'Period', 'Value')`
Where SKU (Stock Keeping Unit) is the index column, Period is the column of sales periods in year and month format (YYYY-MM), and Value is the column of values (Stock or Sales).
The code requires editing in terms of the data source and specifying whether the calculation will apply to the input file named Sales or Stock.
``` python
#Execution:
value_field = 'Sales'
# File paths for input CSV files
file_path1 = "C:/Python repositories/Test 2/data/input_data/" + value_field + ".csv"
file_path2 = "C:/Python repositories/Test 2/data/input_data/COGS.csv"
```
##### Python code
``` python
import pandas as pd
import numpy as np
import os

# ABC Classification function
def assign_abc_groups(df: pd.DataFrame, a_threshold: float = 0.80, b_threshold: float = 0.95) -> pd.DataFrame:
    """
    Assigns ABC classification groups to SKUs per Period based on cumulative value contribution.

    Enhancements:
    -------------
    - Handles cases where total period value is 0 by assigning all SKUs in that period to group 'C'.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with columns ['SKU', 'Period', 'Value'].
    a_threshold : float, optional
        Cumulative contribution cutoff for class A (default=0.80).
    b_threshold : float, optional
        Cumulative contribution cutoff for class B (default=0.95).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ['SKU', 'Period', 'Value', 'ABC_Group'].

    Raises
    ------
    ValueError
        If required columns are missing.
    TypeError
        If 'Value' is not numeric.
    """

    # === 1. Input validation ===
    required_columns = {'SKU', 'Period', 'Value'}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"Missing required columns: {missing}")

    if not pd.api.types.is_numeric_dtype(df['Value']):
        raise TypeError("'Value' column must be numeric (float or int).")

    # Fill missing values in Value column
    df = df.copy()
    df['Value'] = df['Value'].fillna(0.0)

    # === 2. Aggregate total values per SKU/Period ===
    agg_df = (
        df.groupby(['Period', 'SKU'], as_index=False)['Value']
        .sum()
    )

    # === 3. Sort, rank and compute cumulative metrics ===
    agg_df = agg_df.sort_values(['Period', 'Value'], ascending=[True, False])

    # Compute total value per Period
    agg_df['Total_Period_Value'] = agg_df.groupby('Period')['Value'].transform('sum')

    # Compute cumulative value per Period
    agg_df['Cumulative_Value'] = agg_df.groupby('Period')['Value'].cumsum()

    # Handle division safely: if total = 0, set cumulative percent = 1 (forcing C group)
    agg_df['Cumulative_Percent'] = np.where(
        agg_df['Total_Period_Value'] == 0,
        1.0,
        agg_df['Cumulative_Value'] / agg_df['Total_Period_Value']
    )

    # === 4. ABC Group assignment ===
    def classify_abc(cum_pct: float, total_val: float) -> str:
        """
        Determine ABC class:
        - If total value = 0  → assign 'C'
        - Else apply thresholds normally.
        """
        if total_val == 0:
            return 'C'
        if cum_pct <= a_threshold:
            return 'A'
        elif cum_pct <= b_threshold:
            return 'B'
        else:
            return 'C'

    # Apply classification row-wise
    agg_df['ABC_Group'] = agg_df.apply(
        lambda x: classify_abc(x['Cumulative_Percent'], x['Total_Period_Value']),
        axis=1
    )

    # === 5. Merge results back into original DataFrame ===
    result_df = pd.merge(
        df,
        agg_df[['Period', 'SKU', 'ABC_Group']],
        on=['Period', 'SKU'],
        how='left'
    )

    # === 6. Validation ===
    if result_df['ABC_Group'].isna().any():
        raise RuntimeError("ABC group assignment failed for some rows.")

    return result_df


# Saving in the same folder as the Python (py or ipynb) file using one of two popular Excel libraries
def save_file(data: pd.DataFrame, name: str) -> None:
    """
    Saves a DataFrame to an Excel file using the preferred engine.
    Falls back to openpyxl if xlsxwriter is unavailable.
    """
    dump_file_name = f"{name}.xlsx"
    data_dump = os.path.join(os.getcwd(), dump_file_name)

    try:
        # Try xlsxwriter first (faster, supports formatting)
        writer = pd.ExcelWriter(data_dump, engine="xlsxwriter")
    except ModuleNotFoundError:
        print("⚠️  xlsxwriter not found. Falling back to openpyxl.")
        writer = pd.ExcelWriter(data_dump, engine="openpyxl")

    # Write to Excel
    data.to_excel(writer, sheet_name=name, index=False)

    # Save and close the writer properly
    writer.close()
    print(f"✅ Data successfully saved as: {data_dump}")


#Execution:
value_field = 'Sales'
# File paths for input CSV files
file_path1 = "C:/Python repositories/Test 2/data/input_data/" + value_field + ".csv"
file_path2 = "C:/Python repositories/Test 2/data/input_data/COGS.csv"


# Load input data
abc_table = pd.read_csv(file_path1, sep=';')
cogs = pd.read_csv(file_path2, sep=';')

# Replace comma with dot and convert to float
abc_table[value_field] = abc_table[value_field].str.replace(',', '.').astype(float)
cogs['COGS'] = cogs['COGS'].str.replace(',', '.').astype(float)
# Change Date column to datetime format
abc_table['Date'] = pd.to_datetime(abc_table['Date'])

# Create a string Period column from Date
# New column
abc_table['Period'] = abc_table['Date']
# Change format
abc_table['Period'] = pd.to_datetime(abc_table['Date']).dt.strftime('%Y-%m')
# Delete old column
del abc_table['Date']

# Vlookup COGS column to Stock table
stock_cogs = pd.merge(abc_table, cogs, how='left', on='SKU')

# New Stock Value column creation
stock_cogs['Value'] = stock_cogs[value_field]*stock_cogs['COGS']

# Choose columns in a specific order as copy
required_cols = ['SKU', 'Period', 'Value']
abc_input = stock_cogs[required_cols].copy()

# Aggregate values by on SKU, Period level
aggregation_cols = ['SKU','Period']
abc_input = abc_input.groupby(aggregation_cols, as_index=False).agg(
{'Value':'sum'})

# ABC classification operation
df_result = assign_abc_groups(abc_input)

# Save output file
save_file(df_result, "abc_"+value_field)
```
#### XYZ Analysis in Python
##### Explanation
The Python code performs the analysis for all periods provided in long format.
The input data must follow the column name schema:
`('SKU', 'Period', 'Value')`
Where SKU (Stock Keeping Unit) is the index column, Period is the column of sales periods in year and month format (YYYY-MM), and Value is the column of values (Stock or Sales).
The code requires editing in terms of the data source and specifying whether the calculation will apply to the input file named Sales or Stock.
``` python
#Execution:
value_field = 'Sales'
# File paths for input CSV files
file_path = "C:\\Python repositories\\Education project\\src\\data\\input\\" + value_field + ".csv"
```
##### Python code
``` python
import pandas as pd
import numpy as np
import os
from typing import Literal # Used for type hinting data_mode

def assign_xyz_groups(
    df: pd.DataFrame, 
    data_mode: Literal["dense", "sparse"] = "dense"
) -> pd.DataFrame:
    """
    Add 'XYZ', 'CV', and threshold columns to the original DataFrame.

    This function automatically determines X/Y thresholds based on the 33rd/66th
    percentiles of the Coefficient of Variation (CV) for all *eligible* SKUs.

    NEW PARAMETER:
    - data_mode (str):
        - "dense" (default): Replicates Excel behavior. Calculates mean/std
          across the *entire* period range for *all* SKUs. Missing periods
          for a SKU are filled with 0.0 before calculating stats.
        - "sparse": Calculates mean/std *only* using the periods provided
          for each SKU in the input data.

    Rules:
    - Input DataFrame MUST have columns: ['SKU', 'Period', 'Value'].
    - Aggregation at (SKU, Period) is always SUM.
    - SKUs with < 2 aggregated periods => XYZ = "" (Only applies in "sparse" mode)
    - SKUs with mean == 0 => cv = 0 and XYZ = "".
    - ... (rest of classification logic) ...
    """
    
    # --- 0. Validate new parameter ---
    if data_mode not in ["dense", "sparse"]:
        raise ValueError(f"data_mode must be 'dense' or 'sparse', not '{data_mode}'")
        
    # --- 1. Validate required columns ---
    required = {"SKU", "Period", "Value"}
    if not required.issubset(df.columns):
        missing = required - set(df.columns)
        raise ValueError(f"Missing required column(s): {missing}")

    # Work on a copy to avoid mutating caller's DataFrame
    df_out = df.copy()

    # --- 2. Ensure Value is numeric or convertible ---
    if not pd.api.types.is_numeric_dtype(df_out["Value"]):
        coerced = pd.to_numeric(df_out["Value"], errors="coerce")
        if coerced.isna().all():
            raise TypeError("'Value' column must be numeric or convertible to numeric.")
        df_out["Value"] = coerced.fillna(0.0)
    else:
        df_out["Value"] = df_out["Value"].fillna(0.0)

    # --- 3. Aggregate (SKU, Period) by SUM ---
    # This initial aggregation is always needed to ensure one value per SKU/Period
    period_sum = (
        df_out.groupby(["SKU", "Period"], as_index=False)["Value"]
        .sum()
    )

    # --- 3b. (NEW) Densify data if required ---
    # This block creates the DataFrame used for calculating stats
    
    if data_mode == "dense":
        # 1. Get all unique SKUs and Periods from the *original* data
        all_skus = df_out['SKU'].unique()
        all_periods = df_out['Period'].unique()

        # 2. Create a "scaffold" (Cartesian product) of all possible combinations
        df_scaffold = pd.MultiIndex.from_product(
            [all_skus, all_periods], 
            names=['SKU', 'Period']
        ).to_frame(index=False)

        # 3. Merge the aggregated data (period_sum) onto the scaffold
        # This creates a "dense" DataFrame
        df_dense = pd.merge(
            df_scaffold,
            period_sum,
            on=["SKU", "Period"],
            how="left"
        )

        # 4. Fill missing values (where no sales occurred) with 0.0
        df_dense["Value"] = df_dense["Value"].fillna(0.0)
        
        # 5. This dense DataFrame is now the input for stats calculation
        stats_input_df = df_dense
        
    else: # data_mode == "sparse"
        # Use the original sparse aggregation
        stats_input_df = period_sum


    # --- 4. Compute per-SKU statistics across aggregated periods ---
    # MODIFIED: Uses 'stats_input_df' which is either dense or sparse
    sku_stats = (
        stats_input_df.groupby("SKU", as_index=False)["Value"]
        .agg(n_periods="count", mean_value="mean", std_value="std")
    )
    # Note: In "dense" mode, 'n_periods' will be the total # of periods
    # for all SKUs. In "sparse" mode, it's the count of non-zero periods.
    # The classification logic handles this correctly.

    # Fill std=NaN with 0.0 for single-period SKUs (applies to sparse mode)
    sku_stats["std_value"] = sku_stats["std_value"].fillna(0.0)

    # --- 5. Compute CV (Vectorized) ---
    # (Unchanged)
    sku_stats['cv'] = np.where(
        sku_stats['mean_value'] == 0,
        0.0,  # Set CV to 0 if mean is 0
        sku_stats['std_value'] / np.abs(sku_stats['mean_value'])
    )
    
    # Handle potential inf/-inf results
    sku_stats['cv'] = sku_stats['cv'].replace([np.inf, -np.inf], np.nan)


    # --- 6. Determine Dynamic Thresholds ---
    # (Unchanged)
    MIN_PERIODS = 2 # This rule now only has a real effect in "sparse" mode

    is_eligible = (
        (sku_stats['n_periods'] >= MIN_PERIODS) &
        (sku_stats['mean_value'] != 0)
    )
    
    eligible_cvs = sku_stats.loc[is_eligible, 'cv'].dropna()

    if eligible_cvs.empty:
        x_threshold = 0.0
        y_threshold = 0.0
    else:
        quantiles = eligible_cvs.quantile([0.33, 0.66])
        # Automatic version
        x_threshold = quantiles[0.33]
        y_threshold = quantiles[0.66]
        # Manual version 
        # x_threshold = 0.5
        # y_threshold = 1

        if pd.isna(x_threshold) or pd.isna(y_threshold):
            x_threshold = 0.0
            y_threshold = 0.0

    # --- 7. Classify into X/Y/Z or blank "" (Vectorized) ---
    # (Unchanged)
    # The (n_periods < MIN_PERIODS) rule works correctly:
    # - In "dense" mode, it's always False (as n_periods = total periods)
    # - In "sparse" mode, it works as originally intended
    conditions = [
        (sku_stats['n_periods'] < MIN_PERIODS),
        (sku_stats['mean_value'] == 0),
        (sku_stats['cv'].isna()),
        (sku_stats['cv'] <= x_threshold), # "X"
        (sku_stats['cv'] <= y_threshold)  # "Y"
    ]
    
    choices = ["", "", "", "X", "Y"]
    default_choice = "Z"

    sku_stats['XYZ'] = np.select(conditions, choices, default=default_choice)

    # --- 8. Merge SKU-level labels back into the original DataFrame ---
    # (Unchanged)
    # We merge back onto the *original* df_out, not the dense one
    cols_to_merge = sku_stats[["SKU", "XYZ", "cv"]].rename(
        columns={"cv": "CV"}
    )

    merged = pd.merge(
        df_out,
        cols_to_merge,
        on="SKU",
        how="left",
        validate="m:1"  # many original rows to one sku_stats row
    )

    merged["XYZ"] = merged["XYZ"].fillna("")
    
    # --- 8b. Add threshold columns for debugging ---
    # (Unchanged)
    merged['x_threshold_33'] = x_threshold
    merged['y_threshold_66'] = y_threshold
    
    # --- 9. Final validation: ensure only allowed values present ---
    # (Unchanged)
    allowed = {"", "X", "Y", "Z"}
    unique_vals = set(merged["XYZ"].unique())
    disallowed = unique_vals - allowed
    if disallowed:
        raise RuntimeError(f"Unexpected XYZ values found: {disallowed}")

    # --- 10. Final column ordering ---
    # (Unchanged)
    new_cols = ["XYZ", "CV", "x_threshold_33", "y_threshold_66"]
    
    original_cols_to_keep = [
        c for c in df.columns if c not in new_cols
    ]
    
    final_cols = original_cols_to_keep + new_cols
    final = merged[final_cols]

    return final


def assign_xyz_groups_wide(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates XYZ classification and returns a SKU-level aggregated pivot table.

    REFACTORED: This function now calculates the 'CV' and 'XYZ' columns
    using "dense" data logic. It fills in 0.0 for all missing periods for
    all SKUs *before* calculating the mean, std, and CV. This matches
    Excel's behavior of calculating over a fixed range.
 

    1.  Calculates CV for all SKUs (Dense Method).
    2.  Calculates dynamic 33rd/66th percentile thresholds.
    3.  Applies 0.5/1.0 defaults if dynamic thresholds are 0.
    4.  Assigns 'XYZ' classification.

    OUTPUT:
    - PRINTS the final thresholds used for classification.
    - RETURNS a new DataFrame aggregated at the SKU level.
    
    DataFrame Format:
    - Index: None (standard 0...n)
    - Columns:
      - 'SKU'
      - [Period_1 (oldest)], [Period_2], ... [Period_N (newest)]
      - 'XYZ' (classification)
      - 'CV' (Coefficient of Variation, as the last column)
    """
    
    # --- 1. Validate required columns ---
    required = {"SKU", "Period", "Value"}
    if not required.issubset(df.columns):
        missing = required - set(df.columns)
        raise ValueError(f"Missing required column(s): {missing}")

    # Work on a copy to avoid mutating caller's DataFrame
    df_out = df.copy()

    # --- 2. Ensure Value is numeric or convertible ---
    if not pd.api.types.is_numeric_dtype(df_out["Value"]):
        coerced = pd.to_numeric(df_out["Value"], errors="coerce")
        if coerced.isna().all():
            raise TypeError("'Value' column must be numeric or convertible to numeric.")
        df_out["Value"] = coerced.fillna(0.0)
    else:
        df_out["Value"] = df_out["Value"].fillna(0.0)

    # --- 3. Aggregate (SKU, Period) by SUM ---
    # This sparse aggregation is the source for the pivot table *and*
    # the merge onto the dense scaffold.
    period_sum = (
        df_out.groupby(["SKU", "Period"], as_index=False)["Value"]
        .sum()
    )

    # --- 3b. (NEW) Densify data for stats calculation ---
    # This block creates a dense DataFrame (all SKUs x all Periods)
    # to be used *only* for calculating the CV and XYZ stats.
    
    # 1. Get all unique SKUs and Periods
    all_skus = df_out['SKU'].unique()
    all_periods = df_out['Period'].unique()

    # 2. Create a "scaffold" (Cartesian product)
    df_scaffold = pd.MultiIndex.from_product(
        [all_skus, all_periods], 
        names=['SKU', 'Period']
    ).to_frame(index=False)

    # 3. Merge the actual sales data (period_sum) onto the scaffold
    df_dense_stats_source = pd.merge(
        df_scaffold,
        period_sum,
        on=["SKU", "Period"],
        how="left"
    )

    # 4. Fill missing values (where no sales occurred) with 0.0
    df_dense_stats_source["Value"] = df_dense_stats_source["Value"].fillna(0.0)


    # --- 4. Compute per-SKU statistics across aggregated periods ---
    # MODIFIED: This now uses the 'df_dense_stats_source'
    sku_stats = (
        df_dense_stats_source.groupby("SKU", as_index=False)["Value"]
        .agg(n_periods="count", mean_value="mean", std_value="std")
    )

    # Fill std=NaN with 0.0 (e.g., if only 1 period exists)
    sku_stats["std_value"] = sku_stats["std_value"].fillna(0.0)

    # --- 5. Compute CV (Vectorized) ---
    # This CV is now calculated on the DENSE data
    sku_stats['cv'] = np.where(
        sku_stats['mean_value'] == 0,
        0.0,  # Set CV to 0 if mean is 0
        sku_stats['std_value'] / np.abs(sku_stats['mean_value'])
    )
    
    # Handle potential inf/-inf results
    sku_stats['cv'] = sku_stats['cv'].replace([np.inf, -np.inf], np.nan)


    # --- 6. Determine Dynamic Thresholds ---
    MIN_PERIODS = 2
    # Note: In dense mode, 'n_periods' will be the total count of periods
    # for all SKUs, so (n_periods >= MIN_PERIODS) will always be True.
    is_eligible = (
        (sku_stats['n_periods'] >= MIN_PERIODS) &
        (sku_stats['mean_value'] != 0)
    )
    eligible_cvs = sku_stats.loc[is_eligible, 'cv'].dropna()

    if eligible_cvs.empty:
        # Fallback 1: No eligible SKUs.
        x_threshold = 0.0
        y_threshold = 0.0
    else:
        # Calculate 33rd and 66th quantiles
        quantiles = eligible_cvs.quantile([0.33, 0.66])
        # Automatic version
        x_threshold = quantiles[0.33]
        y_threshold = quantiles[0.66]
        # Manual version 
        # x_threshold = 0.5
        # y_threshold = 1

        # Fallback 2: Handle edge cases
        if pd.isna(x_threshold) or pd.isna(y_threshold):
            x_threshold = 0.0
            y_threshold = 0.0

    # Fallback 3: Override if thresholds are 0
    # *** BUG FIX ***: Corrected to apply 0.5/1.0, not just reassign the same value
    if x_threshold == 0.0 or y_threshold == 0.0:
        x_threshold = 0.5
        y_threshold = 1.0

    # --- 7. Print Final Thresholds ---
    print("--- XYZ Classification Thresholds (Dense) ---")
    print(f"33rd Percentile (x_threshold): {x_threshold}")
    print(f"66th Percentile (y_threshold): {y_threshold}")
    print("---------------------------------------------")


    # --- 8. Classify into X/Y/Z or blank "" (Vectorized) ---
    # This classification is now based on the DENSE stats
    conditions = [
        (sku_stats['n_periods'] < MIN_PERIODS), # Will be False in dense mode
        (sku_stats['mean_value'] == 0),
        (sku_stats['cv'].isna()),
        (sku_stats['cv'] <= x_threshold), # "X"
        (sku_stats['cv'] <= y_threshold)  # "Y"
    ]
    choices = ["", "", "", "X", "Y"]
    default_choice = "Z"
    sku_stats['XYZ'] = np.select(conditions, choices, default=default_choice)

    # --- 9. Create Period Pivot Table ---
    # This step is UNCHANGED. It correctly uses the *original* 'period_sum'
    # to build the pivot, which is what the user wants to see.
    period_pivot = pd.pivot_table(
        period_sum,
        values='Value',
        index='SKU',
        columns='Period',
        aggfunc='sum',
        fill_value=0.0  # Fill missing periods for a SKU with 0
    )

    # --- 10. Sort Pivot Columns Chronologically ---
    period_pivot = period_pivot.sort_index(axis=1)
    
    # Get the sorted list of period columns for final ordering
    period_cols = list(period_pivot.columns)

    # --- 11. Merge Stats into Pivot Table ---
    # This step is UNCHANGED, but 'sku_stats' now contains the
    # CV and XYZ values calculated from the DENSE data.
    stats_to_merge = sku_stats[['SKU', 'XYZ', 'cv']].rename(
        columns={'cv': 'CV'}
    )

    final_df = pd.merge(
        period_pivot.reset_index(),
        stats_to_merge,
        on='SKU',
        how='left'
    )

    # --- 12. Final Column Ordering & Cleanup ---
    final_cols = ['SKU'] + period_cols + ['XYZ', 'CV']
    final_df = final_df[final_cols]
    
    final_df['XYZ'] = final_df['XYZ'].fillna("")

    return final_df


# Saving in the same folder as the Python (py or ipynb) file using one of two popular Excel libraries
def save_file(data: pd.DataFrame, name: str) -> None:
    """
    Saves a DataFrame to an Excel file using the preferred engine.
    Falls back to openpyxl if xlsxwriter is unavailable.
    """
    dump_file_name = f"{name}.xlsx"
    data_dump = os.path.join(os.getcwd(), dump_file_name)

    try:
        # Try xlsxwriter first (faster, supports formatting)
        writer = pd.ExcelWriter(data_dump, engine="xlsxwriter")
    except ModuleNotFoundError:
        print("⚠️  xlsxwriter not found. Falling back to openpyxl.")
        writer = pd.ExcelWriter(data_dump, engine="openpyxl")

    # Write to Excel
    data.to_excel(writer, sheet_name=name, index=False)

    # Save and close the writer properly
    writer.close()
    print(f"✅ Data successfully saved as: {data_dump}")


#Execution:
value_field = 'Sales'
# File paths for input CSV files
file_path = "C:\\Python repositories\\Education project\\src\\data\\input\\" + value_field + ".csv"

# Load input data
xyz_table = pd.read_csv(file_path, sep=';')

# Replace comma with dot and convert to float
xyz_table[value_field] = xyz_table[value_field].str.replace(',', '.').astype(float)

# Change Date column to datetime format
# REFRACTORED: Added dayfirst=False to correctly parse DD.MM.YYYY format
xyz_table['Date'] = pd.to_datetime(xyz_table['Date'], dayfirst=False)

# Create a string Period column from Date
# New column
xyz_table['Period'] = xyz_table['Date']
# Change format
xyz_table['Period'] = pd.to_datetime(xyz_table['Date']).dt.strftime('%Y-%m')
# Delete old column
del xyz_table['Date']

# Renaming column to a default input column for XYZ analysis 'Value'
xyz_table.rename(columns={
                value_field: 'Value',
},inplace=True)

# Choose columns in a specific order as copy
required_cols = ['SKU', 'Period', 'Value']
xyz_input = xyz_table[required_cols].copy()

# Aggregate values by on SKU, Period level
aggregation_cols = ['SKU','Period']
xyz_input = xyz_input.groupby(aggregation_cols, as_index=False).agg(
{'Value':'sum'})

# XYZ classification operation
df_result = assign_xyz_groups(xyz_input)
df_wide_result = assign_xyz_groups_wide(xyz_input)

# Save output file
save_file(df_result, "xyz_"+value_field)
save_file(df_wide_result, "xyz_wide_"+value_field)
```
