Query languages are much easier to learn and use than programming languages.

Although query languages are easy to learn and use, they lack the power and versatility of programming languages. To make up for this deficiency, most database management systems also provide a special **data manipulation language** consisting of commands that may be embedded in applications programs to add, retrieve, or change data values.

We can use Python for that.
### Forecasting project with SQL
Example of loading Excel file as basis for a database.

SQLite is a starting point. It’s "serverless"—the entire database is just a file in project folder, and Python has a built-in library (`sqlite3`) to talk to it.

Start the project by making the main folder "Database project" with subfolder "src" and "input_data" and "output_data" folder inside. 
**Copy Excel with daily sales data per SKU:**
src -> input_data -> Salex.xlsx

**What libraries are used in the project - save it as requirements.txt:**
``` python
et_xmlfile==2.0.0
numpy==2.4.2
openpyxl==3.1.5
packaging==26.0
pandas==3.0.1
patsy==1.0.2
python-dateutil==2.9.0.post0
scipy==1.17.1
six==1.17.0
statsmodels==0.14.6
tzdata==2025.3
```
**Installing all the requirements for the project from saved file:**
``` powershell
>>> pip install -r requirements.txt
```
**Planned structure of the project:**
```
DATABASE PROJECT/
# Folders
├── input_data/         # Keep data here
├── output_data/        # Keep DB here
# Main execution file
├── main.py

# Modules

# Database connection
├── database_manager.py 
# Reading input sales data into database format
├── data_ingestion.py  
# Forecasting models
├── models.py       
# Test and sql queries file
├── output_check.py  
    
└── requirements.txt
```
**Excel has daily sales, we need to aggregate them to monthly totals before forecasting with data_ingestion.py:**
``` python
import pandas as pd

def process_excel(file_path):
    df = pd.read_excel(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Aggregate daily to monthly per SKU
    df_monthly = df.groupby(['SKU', pd.Grouper(key='Date', freq='MS')]).sum().reset_index()
    
    # Standardize column names for SQL
    df_monthly.columns = ['sku', 'date', 'sales_volume']
    return df_monthly
```
**The "bridge" between Python and `.db` file. database_manager.py handles the connection:**
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
    df.to_sql(table_name, conn, if_exists='append', index=False)
    conn.close()
```
**Forecasting logic in models.py with two basic models of single exponential smoothing and moving average:**
``` python
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

def run_ses_forecast(series, months=24):
    model = SimpleExpSmoothing(series, initialization_method="estimated").fit()
    return model.forecast(months)

def run_moving_average(series, window=3, months=24):
    last_ma = series.tail(window).mean()
    return [last_ma] * months # Simple MA assumes a flat forecast
```
**Execution of basic setup via main.py:**
``` python
import os
import pandas as pd
from datetime import datetime
from database_manager import create_tables, save_to_sql
from data_ingestion import process_excel
from models import run_ses_forecast, run_moving_average

def run_pipeline(file_name):
    # 1. Setup Database
    print("--- Initializing Database ---")
    create_tables()

    # 2. Data Ingestion & Cleaning
    # Ignore the ~$ temporary files Excel creates
    if file_name.startswith("~$"):
        print("Skipping temporary Excel file.")
        return

    input_path = os.path.join("src", "input_data", file_name)
    print(f"--- Processing {file_name} ---")
    df_monthly = process_excel(input_path)
    
    # Save historical data to SQL
    save_to_sql(df_monthly, 'actual_sales')

    # 3. Forecasting Loop
    all_forecasts = []
    unique_skus = df_monthly['sku'].unique()
    execution_date = datetime.now().date()

    print(f"--- Generating Forecasts for {len(unique_skus)} SKUs ---")
    
    for sku in unique_skus:
        # Get historical data for this specific SKU
        sku_data = df_monthly[df_monthly['sku'] == sku].sort_values('date')
        series = sku_data['sales_volume']
        
        # We need at least 2 data points for SES
        if len(series) < 2:
            continue

        # Generate Dates for the next 24 months
        last_date = sku_data['date'].max()
        forecast_dates = pd.date_range(start=last_date, periods=25, freq='MS')[1:]

        # Run Models
        ses_pred = run_ses_forecast(series, months=24)
        ma_pred = run_moving_average(series, months=24)

        # Prepare SES data for SQL
        for date, val in zip(forecast_dates, ses_pred):
            all_forecasts.append({
                'sku': sku,
                'forecast_date': date.date(),
                'predicted_value': round(val, 2),
                'model_name': 'Simple Exponential Smoothing',
                'execution_date': execution_date
            })

        # Prepare MA data for SQL
        for date, val in zip(forecast_dates, ma_pred):
            all_forecasts.append({
                'sku': sku,
                'forecast_date': date.date(),
                'predicted_value': round(val, 2),
                'model_name': 'Moving Average (3M)',
                'execution_date': execution_date
            })

    # 4. Save Forecasts to SQL
    if all_forecasts:
        forecast_df = pd.DataFrame(all_forecasts)
        save_to_sql(forecast_df, 'forecasts')
        print(f"--- Pipeline Complete. {len(all_forecasts)} forecast rows saved. ---")

if __name__ == "__main__":
    # Point to your specific file name from the screenshot
    run_pipeline("Sales.xlsx")
```
**Checking the contents of the database file sales_forecast.db via output_check.py**
``` python
import sqlite3
import pandas as pd
conn = sqlite3.connect("src/output_data/sales_forecast.db")
print(pd.read_sql("SELECT * FROM forecasts LIMIT 5", conn))
conn.close()
```

**Author:**
Zbigniew Galar
