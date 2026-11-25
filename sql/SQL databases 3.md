## Pipeline version 2
### Making the pipeline production ready in version 1
#### Problems when running the basic code
When we run the basic code again we get the `sqlite3.IntegrityError` is occurring because we set a **PRIMARY KEY** on `(sku, date)`. When you run the script a second time, Python tries to "append" the exact same data again. SQL blocks this to prevent duplicate records, which is actually a great safety feature for production environments.

The problem can be solved by deleting the database file and populating it again with input data. 

However to make the Database the more professional way instead of deleting the entire database file (which would lose your configuration), we will modify the `save_to_sql` logic. In professional data pipelines, we often use a **"Delete then Insert"** or **"Replace"** strategy for specific tables.

Let's update the way the database is populated in `src/database_manager.py` by modifying the function from `append` to `replace`:
``` python
def save_to_sql(df, table_name):
    conn = sqlite3.connect(DB_PATH)
    # Changed if_exists from 'append' to 'replace'
    # This clears the table and inserts fresh data every time you run the script
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
```
To ensure one bad SKU doesn't crash your whole pipeline, we should wrap the model call in a `try-except` block. This is standard practice for production-ready code.

For that we update the loop in `src/main.py`:
``` python
for sku in unique_skus:
    sku_data = df_monthly[df_monthly['sku'] == sku].sort_values('date')
    series = sku_data['sales_volume']
    
    # Requirement: At least 2 non-zero data points for a meaningful forecast
    if len(series[series > 0]) < 2:
        continue

    try:
        # Generate forecast dates
        last_date = sku_data['date'].max()
        forecast_dates = pd.date_range(start=last_date, periods=25, freq='MS')[1:]

        # Run Models
        ses_pred = run_ses_forecast(series, months=24)
        ma_pred = run_moving_average(series, months=24)

        # ... (rest of your logic to append to all_forecasts) ...

    except Exception as e:
        # Log the error but keep moving to the next SKU
        print(f"Skipping SKU {sku} due to model error: {e}")
        continue
```
We can also silence the "divide by zero" and "invalid value" warnings come from `statsmodels` when it tries to calculate logs or trends on SKUs that have long periods of zero sales. We can suppress these using the `warnings` library.
To remove warnings update the top of your `src/main.py`:
``` python
import warnings

# Add this at the very top of the script
warnings.filterwarnings("ignore")
```
#### Solution
New versions of two files are required.
1. New version of `src/database_manager.py`:
``` python
import sqlite3
import pandas as pd

DB_PATH = "src/output_data/sales_forecast.db"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table for Actual Sales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actual_sales (
            sku TEXT,
            date DATE,
            sales_volume INTEGER,
            PRIMARY KEY (sku, date)
        )
    ''')
    
    # Create table for Forecasts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forecasts (
            sku TEXT,
            forecast_date DATE,
            predicted_value REAL,
            model_name TEXT,
            execution_date DATE
        )
    ''')
    conn.commit()
    conn.close()

def save_to_sql(df, table_name):
    conn = sqlite3.connect(DB_PATH)
    # This automatically maps Pandas columns to SQL columns
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
```
2. New version of `src/main.py`:
``` python
import os
import pandas as pd
import warnings
from datetime import datetime

# Import modular components
from database_manager import create_tables, save_to_sql
from data_ingestion import process_excel
from models import run_ses_forecast, run_moving_average

# 1. Professional Setup: Silence mathematical warnings (Divide by zero, etc.)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def run_pipeline(file_name):
    # Setup Database (creates file if not exists)
    print("--- [1/4] Initializing Database ---")
    create_tables()

    # Data Ingestion & Cleaning
    if file_name.startswith("~$"):
        return

    input_path = os.path.join("src", "input_data", file_name)
    print(f"--- [2/4] Processing {file_name} ---")
    
    try:
        df_monthly = process_excel(input_path)
        # We use 'replace' here to ensure a clean state for production runs
        save_to_sql(df_monthly, 'actual_sales')
    except Exception as e:
        print(f"CRITICAL ERROR during ingestion: {e}")
        return

    # Forecasting Engine
    all_forecasts = []
    unique_skus = df_monthly['sku'].unique()
    execution_date = datetime.now().date()
    
    success_count = 0
    fail_count = 0

    print(f"--- [3/4] Generating Forecasts for {len(unique_skus)} SKUs ---")
    
    for sku in unique_skus:
        sku_data = df_monthly[df_monthly['sku'] == sku].sort_values('date')
        series = sku_data['sales_volume']
        
        # Filter: Skip SKUs with insufficient history (need at least 2 data points)
        if len(series[series > 0]) < 2:
            fail_count += 1
            continue

        try:
            last_date = sku_data['date'].max()
            forecast_dates = pd.date_range(start=last_date, periods=25, freq='MS')[1:]

            # Model Execution
            ses_pred = run_ses_forecast(series, months=24)
            ma_pred = run_moving_average(series, months=24)

            # Data Formatting for SQL
            for date, ses_val, ma_val in zip(forecast_dates, ses_pred, ma_pred):
                # SES Record
                all_forecasts.append({
                    'sku': sku, 'forecast_date': date.date(),
                    'predicted_value': round(float(ses_val), 2),
                    'model_name': 'Simple Exponential Smoothing',
                    'execution_date': execution_date
                })
                # MA Record
                all_forecasts.append({
                    'sku': sku, 'forecast_date': date.date(),
                    'predicted_value': round(float(ma_val), 2),
                    'model_name': 'Moving Average (3M)',
                    'execution_date': execution_date
                })
            success_count += 1

        except Exception:
            # Silently fail for the SKU and move to next
            fail_count += 1
            continue

    # 4. Final Output to SQL
    print(f"--- [4/4] Saving Results ---")
    if all_forecasts:
        forecast_df = pd.DataFrame(all_forecasts)
        # Using 'replace' to ensure old forecasts don't mix with new ones
        save_to_sql(forecast_df, 'forecasts')
        
    print(f"\nPipeline Complete:")
    print(f" - Successfully forecasted: {success_count} SKUs")
    print(f" - Skipped (Incomplete Data): {fail_count} SKUs")
    print(f" - Total rows saved to SQL: {len(all_forecasts)}")

if __name__ == "__main__":
    run_pipeline("Sales.xlsx")
```
Improved analysis function `src/analysis.py`:
``` python
import sqlite3
import pandas as pd

conn = sqlite3.connect("src/output_data/sales_forecast.db")
query = """
SELECT sku, SUM(sales_volume) as total_volume 
FROM actual_sales 
GROUP BY sku 
ORDER BY total_volume DESC;
"""
print(pd.read_sql(query, conn))
conn.close()
```
## Pipeline version 3
### Adding backtesting for the best forecasting available
#### Implementing application of the best forecasting model to each SKU (backtesting)
We can assess which is the best model for every SKU based on the accuracy of the model once we go few month into the past and try to predict the latest months of sales. 
- How many month we go back is a parameter we should be able to change.
- What is the best metric to assess which model is the better is a parameter we should be able to change.
We can start with the most popular and most biased metric of Mean Absolute Percentage Error (MAPE) and its less biased counterpart the Symmetric Mean Absolute Percentage Error (SMAPE)

The best forecasting model will be evaluated based on forecast accuracy metric defined in `src/evaluation.py`:
``` python
import numpy as np
import pandas as pd
import inspect

def metric_mape(actual, forecast):
    """Mean Absolute Percentage Error"""
    actual, forecast = np.array(actual), np.array(forecast)
    mask = actual != 0
    if not np.any(mask): return np.inf
    return np.mean(np.abs((actual[mask] - forecast[mask]) / actual[mask])) * 100

def metric_smape(actual, forecast):
    """Symmetric Mean Absolute Percentage Error"""
    actual, forecast = np.array(actual), np.array(forecast)
    denominator = (np.abs(actual) + np.abs(forecast))
    mask = denominator != 0
    if not np.any(mask): return np.inf
    return np.mean(2.0 * np.abs(actual[mask] - forecast[mask]) / denominator[mask]) * 100

def get_available_metrics():
    """Dynamically finds all functions starting with 'metric_'"""
    current_module = inspect.getmodule(inspect.currentframe())
    functions = inspect.getmembers(current_module, inspect.isfunction)
    return {name.replace('metric_', '').upper(): func for name, func in functions if name.startswith('metric_')}

def calculate_error(actual, forecast, metric='MAPE'):
    """Universal caller for dynamic metrics"""
    metrics_map = get_available_metrics()
    metric_key = metric.upper()
    
    if metric_key not in metrics_map:
        raise ValueError(f"Metric {metric_key} not found. Available: {list(metrics_map.keys())}")
    
    return metrics_map[metric_key](actual, forecast)

def get_best_model(performance_list, metric='MAPE'):
    """Selects the winner based on the chosen metric key"""
    if not performance_list: return None
    key = metric.lower() # Assumes dictionary keys in backtest_hub are lowercase metric names
    try:
        return min(performance_list, key=lambda x: x.get(key, np.inf))
    except Exception:
        return performance_list[0]
```
This script acts as the "orchestrator" for the backtesting phase. It handles splitting the data, running the models, calculating errors via `evaluation.py`, and preparing the results for SQL tables. `src/backtesting_hub.py`:
``` python
import pandas as pd
import numpy as np
import inspect
import models 
import evaluation

def get_dynamic_members(module, prefix):
    """Helper to find functions in a module by prefix"""
    return [func for name, func in inspect.getmembers(module, inspect.isfunction) if name.startswith(prefix)]

def run_backtest_for_sku(sku_data, backtest_months, metric='MAPE'):
    sku_data = sku_data.sort_values('date').copy()
    sku = sku_data['sku'].iloc[0]
    
    if len(sku_data) <= backtest_months:
        return None, None

    train_data = sku_data.iloc[:-backtest_months]
    test_data = sku_data.iloc[-backtest_months:]
    actual_values = test_data['sales_volume'].values
    test_dates = test_data['date'].values
    
    backtest_details = []
    summary_results = []
    
    available_models = get_dynamic_members(models, 'run_')
    available_metrics = evaluation.get_available_metrics() # Dict of {NAME: func}

    for model_func in available_models:
        model_name = model_func.__name__.replace('run_', '').replace('_', ' ').title()
        
        try:
            preds = model_func(train_data['sales_volume'], months=backtest_months)
            preds = np.array(preds).flatten()
            
            # 1. Collect Granular Results (Detail Table)
            for i in range(len(test_dates)):
                row = {
                    'sku': sku,
                    'date': test_dates[i],
                    'model_name': model_name,
                    'predicted_value': round(float(preds[i]), 2),
                    'actual_value': float(actual_values[i])
                }
                # Dynamically add every metric found in evaluation.py
                for m_name, m_func in available_metrics.items():
                    row[m_name.lower()] = round(m_func([actual_values[i]], [preds[i]]), 4)
                backtest_details.append(row)
            
            # 2. Collect Aggregate Performance (Summary Table)
            summary_row = {'sku': sku, 'model_name': model_name}
            for m_name, m_func in available_metrics.items():
                summary_row[m_name.lower()] = round(m_func(actual_values, preds), 4)
            summary_results.append(summary_row)
            
        except Exception as e:
            print(f"Error skipping {model_name} for SKU {sku}: {e}")
            continue

    return backtest_details, summary_results
```
Two new Python files require to make changes in `database_manager.py`. Added `get_connection()` function to make it easier for your future reporting application to talk to the database without rewriting connection strings:
``` python
import sqlite3
import pandas as pd

DB_PATH = "src/output_data/sales_forecast.db"

def create_tables():
    """Initializes the analytical framework schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. ACTUAL SALES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actual_sales (
            sku TEXT,
            date DATE,
            sales_volume REAL,
            PRIMARY KEY (sku, date)
        )
    ''')
    
    # 2. BACKTEST_DETAILS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS backtest_details (
            sku TEXT,
            date DATE,
            model_name TEXT,
            predicted_value REAL,
            actual_value REAL,
            mape REAL,
            smape REAL
        )
    ''')
    
    # 3. MODEL_PERFORMANCE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_performance (
            sku TEXT,
            model_name TEXT,
            avg_mape REAL,
            avg_smape REAL,
            is_best INTEGER DEFAULT 0
        )
    ''')

    # 4. FINAL FORECASTS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forecasts (
            sku TEXT,
            forecast_date DATE,
            predicted_value REAL,
            model_name TEXT,
            execution_date DATE,
            PRIMARY KEY (sku, forecast_date, execution_date)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_to_sql(df, table_name, if_exists='replace'):
    """Universal saver for dynamic tables."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
    except Exception as e:
        print(f"Error saving to {table_name}: {e}")
    finally:
        conn.close()

def get_connection():
    """Utility used by accuracy_report.py to run SQL queries."""
    return sqlite3.connect(DB_PATH)
```
Two new Python files require to make changes also in `main.py`. 
But we will do it as last step after we run all the scripts with analytical reporting.

As basis for better understanding the historical sales data we produce another analytical deep dive focused only on the past via `sales_analytics.py`.
This time we will show how advanced the Python analytics can be on top SQL analytical queries.

Since SQLite does not have built-in functions for percentiles (quartiles) or Pearson correlation, we will use a hybrid approach: **SQL** for data extraction and aggregation, and **Pandas** for the more complex statistical calculations, then save them as cleaned-up analytical tables via `sales_analytics.py`:
``` python
import pandas as pd
import numpy as np
import os
from database_manager import get_connection

def calculate_pearson_logic(df):
    """
    Calculates the specific 6-month YoY correlation requested.
    """
    # Pivot to get SKU as rows and Dates as columns
    pivot_df = df.pivot(index='sku', columns='date', values='sales_volume').fillna(0)
    dates = sorted(pivot_df.columns)
    
    if len(dates) < 18:  # Need at least 18 months for a 6-month YoY check
        return pd.DataFrame()

    # Define windows
    last_6 = dates[-6:]
    last_year_6 = dates[-18:-12]
    
    results = []
    for sku in pivot_df.index:
        y_current = pivot_df.loc[sku, last_6].values
        y_prior = pivot_df.loc[sku, last_year_6].values
        
        # Pearson Calculation
        if np.std(y_current) == 0 or np.std(y_prior) == 0:
            corr = 0
        else:
            corr = np.corrcoef(y_current, y_prior)[0, 1]
        
        # Logic Flags
        direction = "Positive" if corr > 0 else "Negative" if corr < 0 else "Neutral"
        is_strong = "Yes" if corr > 0.7 else "No"
        r_sq = f"{round(corr**2 * 100, 2)}%" if corr > 0.7 else "-"
        
        results.append({
            'sku': sku,
            'pearson_correlation': round(corr, 4),
            'direction': direction,
            'strong_positive_70': is_strong,
            'r_squared_pct': r_sq
        })
    
    return pd.DataFrame(results)

def run_analytics():
    print("--- Starting Historical Sales Analytics ---")
    conn = get_connection()
    output_folder = os.path.join("src", "output_data")
    
    # 1. Descriptive Statistics (Quartiles & Distribution)
    # Since SQLite lacks percentiles, we pull to Pandas for the heavy lifting
    df_raw = pd.read_sql("SELECT * FROM actual_sales", conn)
    
    desc_stats = df_raw.groupby('sku')['sales_volume'].describe(percentiles=[.25, .5, .75])
    desc_stats = desc_stats.rename(columns={'25%': '1st_quartile', '50%': 'median', '75%': '3rd_quartile'})
    desc_stats.to_excel(os.path.join(output_folder, "sku_distribution_stats.xlsx"))
    print("Exported: sku_distribution_stats.xlsx")

    # 2. Pearson Correlation Table
    corr_df = calculate_pearson_logic(df_raw)
    if not corr_df.empty:
        corr_df.to_excel(os.path.join(output_folder, "sales_seasonality_correlation.xlsx"), index=False)
        print("Exported: sales_seasonality_correlation.xlsx")

    # 3. Rolling Statistics (3M & 6M)
    df_raw['date'] = pd.to_datetime(df_raw['date'])
    df_raw = df_raw.sort_values(['sku', 'date'])
    df_raw['rolling_avg_3m'] = df_raw.groupby('sku')['sales_volume'].transform(lambda x: x.rolling(3).mean())
    df_raw['rolling_std_3m'] = df_raw.groupby('sku')['sales_volume'].transform(lambda x: x.rolling(3).std())
    df_raw.to_excel(os.path.join(output_folder, "rolling_stats.xlsx"), index=False)
    print("Exported: rolling_stats.xlsx")

    # 4. Lag Features (t-1, t-12)
    df_lags = df_raw.copy()
    df_lags['sales_lag_1'] = df_lags.groupby('sku')['sales_volume'].shift(1)
    df_lags['sales_lag_12'] = df_lags.groupby('sku')['sales_volume'].shift(12)
    df_lags.to_excel(os.path.join(output_folder, "lag_features.xlsx"), index=False)
    print("Exported: lag_features.xlsx")

    # 5. Outlier Detection (Z-Score > 3)
    df_outliers = df_raw.copy()
    df_outliers['mean'] = df_outliers.groupby('sku')['sales_volume'].transform('mean')
    df_outliers['std'] = df_outliers.groupby('sku')['sales_volume'].transform('std')
    df_outliers['z_score'] = (df_outliers['sales_volume'] - df_outliers['mean']) / df_outliers['std']
    df_outliers['is_outlier'] = df_outliers['z_score'].apply(lambda x: "Yes" if abs(x) > 3 else "No")
    # Brute Force Capping
    df_outliers['capped_sales'] = np.where(df_outliers['z_score'] > 3, df_outliers['mean'] + (3 * df_outliers['std']), 
                                           np.where(df_outliers['z_score'] < -3, df_outliers['mean'] - (3 * df_outliers['std']), df_outliers['sales_volume']))
    
    df_outliers.to_excel(os.path.join(output_folder, "outlier_detection_capping.xlsx"), index=False)
    print("Exported: outlier_detection_capping.xlsx")

    conn.close()
    print("--- Analytics Complete ---")

if __name__ == "__main__":
    run_analytics()
```
ABC XYZ analysis with animal segmentation of sales table from the database via `abc_xyz.py`. We also update SQL database for additional SQL query reporting:
``` python
import pandas as pd
import numpy as np
import os
from database_manager import get_connection

def run_segmentation():
    print("--- Starting Dynamic ABC/XYZ Animal Segmentation ---")
    conn = get_connection()
    output_folder = os.path.join("src", "output_data")
    
    # Extract data for processing
    df = pd.read_sql("SELECT * FROM actual_sales", conn)
    
    # Calculate Metrics per SKU
    sku_stats = df.groupby('sku')['sales_volume'].agg(['sum', 'mean', 'std']).reset_index()
    sku_stats.columns = ['sku', 'total_volume', 'mean_sales', 'std_dev']
    
    # Coefficient of Variation (CV) = Standard Deviation / Mean
    sku_stats['cv'] = sku_stats['std_dev'] / sku_stats['mean_sales']
    sku_stats['cv'] = sku_stats['cv'].fillna(0)

    # 1. ABC Analysis (Volume-based Ranking)
    sku_stats = sku_stats.sort_values('total_volume', ascending=False)
    sku_stats['cum_vol'] = sku_stats['total_volume'].cumsum()
    total_vol = sku_stats['total_volume'].sum()
    sku_stats['cum_pct'] = sku_stats['cum_vol'] / total_vol
    
    def abc_classify(pct):
        if pct <= 0.80: return 'A' 
        if pct <= 0.95: return 'B' 
        return 'C'                 

    sku_stats['abc'] = sku_stats['cum_pct'].apply(abc_classify)

    # 2. Dynamic XYZ Analysis (Quantile-based Thresholds)
    # Instead of hardcoded values, we calculate the spectrum based on your data
    lower_threshold = sku_stats['cv'].quantile(0.33)
    upper_threshold = sku_stats['cv'].quantile(0.66)
    
    print(f"XYZ Thresholds determined: X <= {lower_threshold:.2f}, Z > {upper_threshold:.2f}")

    def xyz_classify(cv):
        if cv <= lower_threshold: return 'X'  # Stable (Bottom 33% of CV)
        if cv <= upper_threshold: return 'Y'  # Fluctuating (Middle 33% of CV)
        return 'Z'                            # Highly Volatile (Top 33% of CV)

    sku_stats['xyz'] = sku_stats['cv'].apply(xyz_classify)
    
    # 3. Animal Segmentation Logic
    # Mapping based on your specific table
    animal_map = {
        'AX': 'Horses',   'BX': 'Horses',
        'AY': 'Mad Bulls', 'AZ': 'Mad Bulls', 'BY': 'Mad Bulls', 'BZ': 'Mad Bulls',
        'CX': 'Turtles',
        'CY': 'Rabbits',  'CZ': 'Rabbits'
    }
    
    sku_stats['segment_code'] = sku_stats['abc'] + sku_stats['xyz']
    sku_stats['animal_persona'] = sku_stats['segment_code'].map(animal_map)

    # 4. Save and Export
    sku_stats.to_excel(os.path.join(output_folder, "abc_xyz_segmentation.xlsx"), index=False)
    
    # Update SQL table for analytical use
    conn = get_connection()
    sku_stats[['sku', 'abc', 'xyz', 'animal_persona', 'cv']].to_sql('sku_segmentation', conn, if_exists='replace', index=False)
    conn.close()
    
    print("Exported: abc_xyz_segmentation.xlsx and updated SQL table 'sku_segmentation'")
    print("--- Segmentation Complete ---")

if __name__ == "__main__":
    run_segmentation()
```
Once the forecast and the backtesting of the forecast is saved as SQL database we can run queries for analytical reporting.

**Accuracy report from backtesting using the SQL queries and assuming the following:**
- **Backtest Granular Analysis:** Use this file in Power BI to create "Actual vs. Predicted" line charts for specific SKUs to see where the models deviate.
- **Model Comparison:** This is your primary tool for seeing if one model (like SES) is consistently better than another (like Moving Average) across your entire catalog.
- **Dynamic Expansion:** If you add a new metric like `BIAS` to your `evaluation.py`, you simply update the `REPORTS_CONFIG` strings in this file to include `bias` in the `SELECT` statements.
- **Animal-Level Benchmarking**: The `model_comparison_by_animal.xlsx` report is your most powerful tool. It tells you, for example, if **SES** is significantly better for **Horses** than **Moving Average**, or if all models are failing equally for **Rabbits**.
- **Segmentation Context**: By joining `sku_segmentation` into the granular analysis, you can filter your Power BI dashboards by "Animal Persona" to isolate the high-risk SKUs (**Mad Bulls**) from the steady ones.
- **Strategic Forecasts**: The `future_forecast_with_segments.xlsx` allows the supply chain team to prioritize their review. They may choose to manually adjust a **Mad Bull** forecast while auto-approving a **Turtle** forecast.
via `accuracy_report.py`:
``` python
import pandas as pd
import os

# Handle import regardless of execution context
try:
    from database_manager import get_connection
except ImportError:
    from src.database_manager import get_connection

# Configuration: Analytical SQL Queries
# We leverage JOINs between model_performance and sku_segmentation
REPORTS_CONFIG = {
    "backtest_granular_analysis.xlsx": """
        SELECT 
            b.sku, 
            s.animal_persona,
            b.date, 
            b.model_name, 
            b.actual_value, 
            b.predicted_value,
            b.mape,
            b.smape
        FROM backtest_details b
        LEFT JOIN sku_segmentation s ON b.sku = s.sku
        ORDER BY s.animal_persona, b.sku, b.date
    """,
    
    "model_comparison_by_animal.xlsx": """
        SELECT 
            s.animal_persona,
            m.model_name, 
            AVG(m.mape) as avg_mape, 
            AVG(m.smape) as avg_smape,
            COUNT(DISTINCT m.sku) as sku_count
        FROM model_performance m
        JOIN sku_segmentation s ON m.sku = s.sku
        GROUP BY s.animal_persona, m.model_name
        ORDER BY s.animal_persona, avg_mape ASC
    """,
    
    "best_model_per_sku_full_context.xlsx": """
        SELECT 
            m.sku,
            s.abc,
            s.xyz,
            s.animal_persona,
            m.model_name,
            m.mape,
            m.smape
        FROM model_performance m
        JOIN sku_segmentation s ON m.sku = s.sku
        WHERE m.is_best = 1
        ORDER BY s.abc, s.xyz
    """,
    
    "future_forecast_with_segments.xlsx": """
        SELECT 
            f.sku, 
            s.animal_persona,
            f.forecast_date, 
            f.predicted_value, 
            f.model_name
        FROM forecasts f
        LEFT JOIN sku_segmentation s ON f.sku = s.sku
        ORDER BY s.animal_persona, f.sku, f.forecast_date
    """
}

def export_report_to_excel(query, filename):
    """
    Executes a SQL query and saves the result as an Excel file in the output folder.
    """
    output_folder = os.path.join("src", "output_data")
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    full_path = os.path.join(output_folder, filename)
    
    try:
        conn = get_connection()
        df = pd.read_sql(query, conn)
        conn.close()
        
        if not df.empty:
            df.to_excel(full_path, index=False)
            print(f"Successfully exported: {filename}")
        else:
            print(f"Report {filename} skipped: No data returned.")
            
    except Exception as e:
        print(f"Error generating {filename}: {e}")

def run_all_reports():
    """
    Orchestrates the export of the entire analytical suite.
    """
    print("--- Starting Enhanced Analytical Report Export ---")
    for filename, query in REPORTS_CONFIG.items():
        export_report_to_excel(query, filename)
    print("--- All reports finished ---")

if __name__ == "__main__":
    run_all_reports()
```
Below the update to the main running script `main.py` that ingests the data, runs a backtesting for every SKU to find the most accurate model based on your chosen metric, saves those analytical insights, and finally generates a 24-month production forecast using only the winning models:
``` python
import os
import pandas as pd
import warnings
from datetime import datetime

# Import modular components
from database_manager import create_tables, save_to_sql
from data_ingestion import process_excel
from models import run_ses_forecast, run_moving_average
from backtesting_hub import run_backtest_for_sku
from evaluation import get_best_model
from accuracy_report import run_all_reports
from sales_analytics import run_analytics
from abc_xyz import run_segmentation

# --- CONFIGURATION PARAMETERS ---
BACKTEST_MONTHS = 6          # Number of months to go back for validation
SELECTION_METRIC = 'MAPE'    # Metric to decide the 'Best' model (MAPE or SMAPE)
FORECAST_HORIZON = 24        # Months to forecast into the future
INPUT_FILE = "Sales.xlsx"    # Your source data file
# --------------------------------

# Silence mathematical noise for a clean terminal output
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def run_pipeline(file_name):
    # 1. Setup Database
    print(f"--- [1/6] Initializing Database & Tables ---")
    create_tables()

    # 2. Data Ingestion
    if file_name.startswith("~$"):
        return

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(BASE_DIR, "input_data", file_name)
    
    print(f"--- [2/6] Ingesting {file_name} ---")
    try:
        df_monthly = process_excel(input_path)
        save_to_sql(df_monthly, 'actual_sales')
    except Exception as e:
        print(f"CRITICAL ERROR during ingestion: {e}")
        return

    # 3. Descriptive Analytics & Segmentation
    print(f"--- [3/6] Running Sales Analytics & Animal Segmentation ---")
    run_analytics()      # Generates Lags, Rolling Stats, and Outlier reports
    run_segmentation()   # Assigns Horses, Mad Bulls, Turtles, and Rabbits

    # 4. Backtesting & Model Selection
    all_backtest_details = []
    all_model_performance = []
    final_forecast_output = []
    
    unique_skus = df_monthly['sku'].unique()
    execution_date = datetime.now().date()
    
    print(f"--- [4/6] Backtesting & Selecting Best Models (Metric: {SELECTION_METRIC}) ---")
    
    for sku in unique_skus:
        sku_data = df_monthly[df_monthly['sku'] == sku].sort_values('date')
        
        # Run the dynamic backtesting hub
        details, summary = run_backtest_for_sku(sku_data, BACKTEST_MONTHS, SELECTION_METRIC)
        
        if not details or not summary:
            continue
            
        # Identify the winner for this SKU
        best_model_info = get_best_model(summary, SELECTION_METRIC)
        winner_name = best_model_info['model_name']
        
        # Mark the winner in the performance summary
        for item in summary:
            item['is_best'] = 1 if item['model_name'] == winner_name else 0
            all_model_performance.append(item)
        
        all_backtest_details.extend(details)

        # 5. Production Forecast: Run winner on full dataset
        try:
            last_date = pd.to_datetime(sku_data['date'].max())
            forecast_dates = pd.date_range(start=last_date, periods=FORECAST_HORIZON + 1, freq='MS')[1:]
            
            series = sku_data['sales_volume']
            if "Smoothing" in winner_name:
                preds = run_ses_forecast(series, months=FORECAST_HORIZON)
            else:
                preds = run_moving_average(series, months=FORECAST_HORIZON)
                
            for d, val in zip(forecast_dates, preds):
                final_forecast_output.append({
                    'sku': sku,
                    'forecast_date': d.strftime('%Y-%m-%d'),
                    'predicted_value': round(float(val), 2),
                    'model_name': winner_name,
                    'execution_date': execution_date
                })
        except Exception:
            continue

    # 6. Finalizing SQL & Exporting Reports
    print(f"--- [5/6] Updating SQL Analytical Framework ---")
    if all_backtest_details:
        save_to_sql(pd.DataFrame(all_backtest_details), 'backtest_details')
    if all_model_performance:
        save_to_sql(pd.DataFrame(all_model_performance), 'model_performance')
    if final_forecast_output:
        save_to_sql(pd.DataFrame(final_forecast_output), 'forecasts')

    print(f"--- [6/6] Generating Final Excel Reports ---")
    run_all_reports()

    print(f"\nPipeline Execution Successful.")
    print(f"Processed {len(unique_skus)} SKUs. All outputs saved in 'src/output_data/'.")

if __name__ == "__main__":
    run_pipeline(INPUT_FILE)
```

**Author:**
Zbigniew Galar
