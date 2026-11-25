## Pipeline version 4
### Expanding the parametrization of the models
#### Running different parameters as new models to chose from
When running the moving average model the window size (how many months to aggregate as average) is fixed. For some SKU this is a good aggregation but for others it is not the right parameter of the model. 

Once we treat different parametrization of the models as different models (making different forecasts) we can choose the best model for an SKU from the greater variety of models. 

Update of `models.py` with different windows sizes for moving average model:
``` python
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
import pandas as pd
import numpy as np

# --- 1. BACKWARD COMPATIBLE MODELS (Standard Names) ---

def run_ses_forecast(series, months=24):
    """
    Standard Simple Exponential Smoothing (optimized alpha).
    Maintained for backward compatibility with existing main.py imports.
    """
    model = SimpleExpSmoothing(series, initialization_method="estimated").fit()
    return model.forecast(months)

def run_moving_average(series, window=3, months=24):
    """
    Standard 3-Month Moving Average.
    Maintained for backward compatibility with existing main.py imports.
    """
    last_ma = series.tail(window).mean()
    return [last_ma] * months


# --- 2. PARAMETERIZED BRUTE-FORCE MODELS ---

def run_moving_average_6(series, window=6, months=24):
    """6-Month Moving Average."""
    last_ma = series.tail(window).mean()
    return [last_ma] * months

def run_moving_average_9(series, window=9, months=24):
    """9-Month Moving Average."""
    last_ma = series.tail(window).mean()
    return [last_ma] * months

def run_moving_average_12(series, window=12, months=24):
    """12-Month Moving Average."""
    last_ma = series.tail(window).mean()
    return [last_ma] * months
```
In the main execution file we just need to broaden the number of models that we import for the calculation in `main.py`:
**Importing before:**
``` python
# Import modular components
from database_manager import create_tables, save_to_sql
from data_ingestion import process_excel
from models import run_ses_forecast, run_moving_average
from backtesting_hub import run_backtest_for_sku
from evaluation import get_best_model
from accuracy_report import run_all_reports
from sales_analytics import run_analytics
from abc_xyz import run_segmentation
```
**Importing after:**
``` python
# Import modular components
from database_manager import create_tables, save_to_sql
from data_ingestion import process_excel
from models import run_ses_forecast, run_moving_average, run_moving_average_6, run_moving_average_9, run_moving_average_12
from backtesting_hub import run_backtest_for_sku
from evaluation import get_best_model
from accuracy_report import run_all_reports
from sales_analytics import run_analytics
from abc_xyz import run_segmentation
```
Therefore new version of `main.py`:
``` python
import os
import pandas as pd
import warnings
from datetime import datetime

# Import modular components
from database_manager import create_tables, save_to_sql
from data_ingestion import process_excel
from models import run_ses_forecast, run_moving_average, run_moving_average_6, run_moving_average_9, run_moving_average_12
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
We can also expand the number of model parametrization for the Single Exponential Smoothing by assigning the alpha parameter as fixed value on top of the best guess that we currently use on default.
Updated `models.py` with different SES versions:
``` python
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
import pandas as pd
import numpy as np

# --- 1. BACKWARD COMPATIBLE MODELS (Standard Names) ---

def run_ses_forecast(series, months=24):
    """
    Standard SES where alpha is automatically optimized by statsmodels.
    """
    model = SimpleExpSmoothing(series, initialization_method="estimated").fit()
    return model.forecast(months)

def run_moving_average(series, window=3, months=24):
    """
    Standard 3-Month Moving Average.
    """
    last_ma = series.tail(window).mean()
    return [last_ma] * months


# --- 2. PARAMETERIZED MOVING AVERAGES ---

def run_moving_average_6(series, window=6, months=24):
    """6-Month Moving Average."""
    last_ma = series.tail(window).mean()
    return [last_ma] * months

def run_moving_average_9(series, window=9, months=24):
    """9-Month Moving Average."""
    last_ma = series.tail(window).mean()
    return [last_ma] * months

def run_moving_average_12(series, window=12, months=24):
    """12-Month Moving Average."""
    last_ma = series.tail(window).mean()
    return [last_ma] * months


# --- 3. PARAMETERIZED SES (ALPHA SWEEPING) ---

def run_ses_alpha_0_1(series, months=24):
    """SES with Alpha = 0.1 (Extremely smooth/stable)."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.1, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_2(series, months=24):
    """SES with Alpha = 0.2."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.2, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_3(series, months=24):
    """SES with Alpha = 0.3."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.3, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_4(series, months=24):
    """SES with Alpha = 0.4."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.4, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_5(series, months=24):
    """SES with Alpha = 0.5 (Balanced reactivity)."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.5, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_6(series, months=24):
    """SES with Alpha = 0.6."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.6, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_7(series, months=24):
    """SES with Alpha = 0.7."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.7, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_8(series, months=24):
    """SES with Alpha = 0.8."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.8, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_9(series, months=24):
    """SES with Alpha = 0.9 (Highly reactive to latest data)."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.9, optimized=False)
    return model.forecast(months)
```
Now that we have 14 models the best option is to import everything in main.py:
``` python
import models
```
Once we have that we can update the `models.py` for better clarity with backward compatible naming convention:
``` python
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

# --- 1. PARAMETERIZED MOVING AVERAGES ---

def run_moving_average_3(series, window=3, months=24):
    """3-Month Moving Average."""
    last_ma = series.tail(window).mean()
    return [last_ma] * months

def run_moving_average_6(series, window=6, months=24):
    """6-Month Moving Average."""
    last_ma = series.tail(window).mean()
    return [last_ma] * months

def run_moving_average_9(series, window=9, months=24):
    """9-Month Moving Average."""
    last_ma = series.tail(window).mean()
    return [last_ma] * months

def run_moving_average_12(series, window=12, months=24):
    """12-Month Moving Average."""
    last_ma = series.tail(window).mean()
    return [last_ma] * months


# --- 2. PARAMETERIZED SES (ALPHA SWEEPING) ---

def run_ses_forecast(series, months=24):
    """
    Standard SES where alpha is automatically optimized by statsmodels.
    """
    model = SimpleExpSmoothing(series, initialization_method="estimated").fit()
    return model.forecast(months)

def run_ses_alpha_0_1(series, months=24):
    """SES with Alpha = 0.1 (Extremely smooth/stable)."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.1, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_2(series, months=24):
    """SES with Alpha = 0.2."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.2, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_3(series, months=24):
    """SES with Alpha = 0.3."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.3, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_4(series, months=24):
    """SES with Alpha = 0.4."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.4, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_5(series, months=24):
    """SES with Alpha = 0.5 (Balanced reactivity)."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.5, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_6(series, months=24):
    """SES with Alpha = 0.6."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.6, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_7(series, months=24):
    """SES with Alpha = 0.7."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.7, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_8(series, months=24):
    """SES with Alpha = 0.8."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.8, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_9(series, months=24):
    """SES with Alpha = 0.9 (Highly reactive to latest data)."""
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.9, optimized=False)
    return model.forecast(months)
```
Now let's add new more complex model into the mix like Holt Winters into refactored `models.py`:
``` python
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, ExponentialSmoothing
import pandas as pd
import numpy as np

# --- 1. PARAMETERIZED MOVING AVERAGES ---

def run_moving_average_3(series, window=3, months=24):
    """3-Month Moving Average."""
    last_ma = series.tail(window).mean()
    return [last_ma] * months

def run_moving_average_6(series, window=6, months=24):
    """6-Month Moving Average."""
    last_ma = series.tail(window).mean()
    return [last_ma] * months

def run_moving_average_9(series, window=9, months=24):
    """9-Month Moving Average."""
    last_ma = series.tail(window).mean()
    return [last_ma] * months

def run_moving_average_12(series, window=12, months=24):
    """12-Month Moving Average."""
    last_ma = series.tail(window).mean()
    return [last_ma] * months


# --- 2. PARAMETERIZED SES (ALPHA SWEEPING) ---

def run_ses_forecast(series, months=24):
    """Standard SES (optimized alpha)."""
    model = SimpleExpSmoothing(series, initialization_method="estimated").fit()
    return model.forecast(months)

def run_ses_alpha_0_1(series, months=24):
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.1, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_2(series, months=24):
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.2, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_3(series, months=24):
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.3, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_4(series, months=24):
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.4, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_5(series, months=24):
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.5, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_6(series, months=24):
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.6, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_7(series, months=24):
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.7, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_8(series, months=24):
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.8, optimized=False)
    return model.forecast(months)

def run_ses_alpha_0_9(series, months=24):
    model = SimpleExpSmoothing(series).fit(smoothing_level=0.9, optimized=False)
    return model.forecast(months)


# --- 3. HOLT-WINTERS (ADVANCED SEASONAL MODELS) ---

def run_holt_winters_additive(series, months=24):
    """Holt-Winters with Additive Trend and Seasonality."""
    try:
        # Requires at least 24 months for stable seasonal estimation
        model = ExponentialSmoothing(
            series, trend='add', seasonal='add', seasonal_periods=12, 
            initialization_method="estimated"
        ).fit()
        return model.forecast(months)
    except:
        return run_ses_forecast(series, months)

def run_holt_winters_multiplicative(series, months=24):
    """Holt-Winters with Multiplicative Seasonality."""
    try:
        # Multiplicative models require strictly positive data
        if (series <= 0).any():
            return run_holt_winters_additive(series, months)
        model = ExponentialSmoothing(
            series, trend='add', seasonal='mul', seasonal_periods=12, 
            initialization_method="estimated"
        ).fit()
        return model.forecast(months)
    except:
        return run_ses_forecast(series, months)

def run_holt_trend_only(series, months=24):
    """Holt's Linear Trend (No Seasonality)."""
    try:
        model = ExponentialSmoothing(
            series, trend='add', seasonal=None, 
            initialization_method="estimated"
        ).fit()
        return model.forecast(months)
    except:
        return run_ses_forecast(series, months)
```
As final step an updated and naming agnostic `main.py`:
- **`getattr(models, winner_func_name)`**: This is line looks into `models.py` and finds the function that matches the winner's name exactly. No more `if/else` blocks required.
Normally, to run a function, you have to type its name explicitly, like `run_ses_forecast()`. If you have 14 different models, you would usually need a massive `if/elif/else` block to decide which one to run.
`getattr` bypasses this by treating the function name as **data** (a string).
1. **Input:** The string `"run_ses_alpha_0_1"`.
2. **Action:** `getattr` looks inside the `models` module for a function with that exact name.
3. **Result:** It returns the actual executable function object and assigns it to `winning_func`.
4. **Execution:** When you call `winning_func(...)`, Python executes the specific alpha-0.1 logic as if you had hardcoded it.
This allows your project to grow to 100 models without ever needing to change `main.py` again.
- **Agnostic Logic**: Whether a "Mad Bull" wins with `run_ses_alpha_0_9` or a "Horse" wins with `run_moving_average_12`, `main.py` handles them identically.
- **Automatic Cleanup**: The code automatically reconstructs the function name from the SQL display name (`Ses Alpha 0 1` $\rightarrow$ `run_ses_alpha_0_1`).
``` python
import os
import pandas as pd
import warnings
from datetime import datetime
import models  # Import the module to allow dynamic function access

# Import modular components
from database_manager import create_tables, save_to_sql
from data_ingestion import process_excel
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

# Silence mathematical noise
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
    run_analytics()
    run_segmentation()

    # 4. Backtesting & Model Selection
    all_backtest_details = []
    all_model_performance = []
    final_forecast_output = []
    
    unique_skus = df_monthly['sku'].unique()
    execution_date = datetime.now().date()
    
    print(f"--- [4/6] Backtesting {len(unique_skus)} SKUs with All Models ---")
    
    for sku in unique_skus:
        sku_data = df_monthly[df_monthly['sku'] == sku].sort_values('date')
        
        # Run the dynamic backtesting hub (detects all 'run_' functions)
        details, summary = run_backtest_for_sku(sku_data, BACKTEST_MONTHS, SELECTION_METRIC)
        
        if not details or not summary:
            continue
            
        # Identify the winner for this SKU
        best_model_info = get_best_model(summary, SELECTION_METRIC)
        winner_display_name = best_model_info['model_name']
        
        # Convert display name back to function name: 'Ses Alpha 0 1' -> 'run_ses_alpha_0_1'
        winner_func_name = "run_" + winner_display_name.lower().replace(" ", "_")
        
        # Mark the winner in the performance summary for SQL
        for item in summary:
            item['is_best'] = 1 if item['model_name'] == winner_display_name else 0
            all_model_performance.append(item)
        
        all_backtest_details.extend(details)

        # 5. Production Forecast: DYNAMICALLY call the winning function
        try:
            last_date = pd.to_datetime(sku_data['date'].max())
            forecast_dates = pd.date_range(start=last_date, periods=FORECAST_HORIZON + 1, freq='MS')[1:]
            
            # Fetch the actual function from the models module by its string name
            winning_func = getattr(models, winner_func_name)
            
            # Execute the specific winner (SES or MA with specific parameters)
            preds = winning_func(sku_data['sales_volume'], months=FORECAST_HORIZON)
                
            for d, val in zip(forecast_dates, preds):
                final_forecast_output.append({
                    'sku': sku,
                    'forecast_date': d.strftime('%Y-%m-%d'),
                    'predicted_value': round(float(val), 2),
                    'model_name': winner_display_name,
                    'execution_date': execution_date
                })
        except Exception as e:
            print(f"Error forecasting SKU {sku} with {winner_func_name}: {e}")
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
    print(f"Check 'src/output_data/' for results.")

if __name__ == "__main__":
    run_pipeline(INPUT_FILE)
```
### Summary of version 4: Forecasting Engine v1.0
The current system is a "brute-force" statistical forecasting pipeline that automates the transition from raw daily sales to a multi-model 24-month horizon. It utilizes a dynamic "Tournament" logic where 17 different models compete for every SKU based on historical accuracy.
#### 1. Architectural Foundation
- **Dynamic Model Discovery**: The system uses Python’s `inspect` module to automatically detect and run any function in `models.py` starting with `run_`. This allows for infinite model expansion without refactoring the core logic.
- **Winner Selection**: Selection is driven by a backtesting hub that simulates the last 6 months of sales, calculating **MAPE** and **SMAPE** for every candidate.
- **Database-Centric Ingestion**: Currently utilizing SQLite to bridge data ingestion, analytical feature engineering, and reporting.
#### 2. Model Library (The "Menu")
The engine currently tests **17 distinct parametrizations** for every SKU:
- **Moving Averages**: 3, 6, 9, and 12-month windows.
- **Simple Exponential Smoothing (SES)**:
    - One optimized model (Auto-alpha).
    - Nine fixed-alpha models (Grid search from 0.1 to 0.9).
- **Holt-Winters (Seasonal)**:
    - Additive Trend & Seasonality.
    - Multiplicative Seasonality.
    - Holt’s Linear Trend (Trend only).
    - _Note:_ These include robust `try/except` fallbacks to SES for SKUs with insufficient history.
#### 3. Advanced SKU Segmentation (Animal Personas)
SKUs are categorized using a dynamic **ABC/XYZ Matrix** based on the 33rd and 66th percentiles of the Coefficient of Variation (CV):
- **Horses (AX, BX)**: High/Med volume, stable demand.
- **Mad Bulls (AY, AZ, BY, BZ)**: High/Med volume, high volatility.
- **Turtles (CX)**: Low volume, stable.
- **Rabbits (CY, CZ)**: Low volume, highly irregular "hopping" demand.
### 4. Feature Engineering & Analytics
The pipeline generates a suite of historical insights before forecasting:
- **Lags & Rolling Stats**: 1-12 month lags and rolling averages/stdev.
- **Outlier Management**: Z-score detection (>3) and brute-force capping to prevent model skew.
- **Seasonality Check**: Pearson correlation between current 6-month windows and the prior year's window.
##### Database export (all tables as Excel files for smaller datasets) with sqlite_db_excel_export.py
``` python
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("src/output_data/sales_forecast.db")
OUTPUT_DIR = DB_PATH.parent

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(DB_PATH)

tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)['name']

for table in tables:
    pd.read_sql_query(f"SELECT * FROM {table}", conn).to_excel(OUTPUT_DIR / f"{table}.xlsx", index=False)

conn.close()
```
##### Database export (all tables as CSV files for bigger datasets) with sqlite_db_csv_export.py
``` python
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("src/output_data/sales_forecast.db")
OUTPUT_DIR = DB_PATH.parent

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(DB_PATH)

tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)['name']

for table in tables:
    pd.read_sql_query(f"SELECT * FROM {table}", conn).to_csv(OUTPUT_DIR / f"{table}.csv", index=False)

conn.close()
```

**Author:**
Zbigniew Galar
