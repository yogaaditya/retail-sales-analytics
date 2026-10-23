
# Retail Sales Analytics & Business Intelligence

## Project Overview

This project demonstrates an end-to-end retail data analytics workflow,
from raw transaction data ingestion and data cleaning to SQL Server
analytics and Power BI dashboard reporting.

The project is designed as a portfolio project for an aspiring ETL
Developer / Data Analyst.

## Business Objectives

- Monitor total sales and transaction volume.
- Analyze daily sales trends.
- Identify products with the highest sales.
- Compare sales performance across cities.
- Understand sales distribution by payment method.
- Build a repeatable Python ETL pipeline.

## Tech Stack

- Python
- Pandas
- SQL Server
- SQL Server Management Studio (SSMS)
- Power BI Desktop
- Git and GitHub

## Architecture

1. Extract raw retail transaction data from CSV.
2. Transform and validate records using Python.
3. Load valid transactions into SQL Server.
4. Create SQL views for business analysis.
5. Connect Power BI to SQL Server views.
6. Visualize sales KPIs and trends in a Power BI dashboard.

## Project Structure

```
retail-sales-analytics/
├── data/
│ ├── raw/
│ └── processed/
├── logs/
├── python/
│ ├── profile_data.py
│ ├── clean_data.py
│ ├── load_to_sqlserver.py
│ └── etl_pipeline.py
├── report/
│ ├── data_profile/
│ └── screenshots/
├── sql/
│ ├── 01_create_views.sql
│ ├── 02_validation_queries.sql
│ ├── Analisa data.sql
│ ├── Query membuat dan pengecekan DB.sql
│ └── Verifikasi.sql
├── powerbi/
│ └── Retail_Sales_Analytics.pbix
├── README.md
└── .gitignore
```

## Data

The project uses a small synthetic retail transaction dataset.

Typical fields include:

- Transaction_ID
- Date
- Product
- Category
- Quantity
- Unit_Price
- Payment_Method
- City

Sales amount is calculated as:

`Sales = Quantity * Unit_Price`

The sample data is intended for learning and demonstration, not
for representing real business performance.

## ETL Workflow

### Extract
Read the raw CSV transaction file.

### Transform
Standardize text, convert dates and numeric columns, validate required
fields, and identify invalid or duplicate transaction IDs.

### Load
Insert valid transactions into the SQL Server table
`dbo.RetailTransactions`.

### Analytics
Create SQL views for:

- Daily sales
- Product sales
- City sales
- Payment method sales
- Overall sales KPIs

## Power BI Dashboard

The dashboard includes:

- Total Sales
- Total Transactions
- Units Sold
- Average Transaction Value
- Daily Sales Trend
- Sales by Product
- Sales by City
- Sales by Payment Method

## Setup Requirements

- Windows 10/11
- Python
- SQL Server
- SQL Server ODBC Driver
- Power BI Desktop
- Git

## Running the Python Pipeline

From the project root, activate the virtual environment or use its
Python executable directly.

```powershell
.\.venv\Scripts\python.exe .\python\etl_pipeline.py
```

Before running the pipeline, make sure that:

1. The raw CSV file exists.
2. The SQL Server ODBC driver is installed.
3. The SQL Server instance name is configured correctly.
4. The database `RetailSalesDB` exists.
5. The table `dbo.RetailTransactions` exists.
6. Your Windows account has permission to access the database.

Example PowerShell configuration:

```powershell
$env:RETAIL_SQL_SERVER = "YOUR_SERVER_NAME"
$env:RETAIL_SQL_DATABASE = "RetailSalesDB"
$env:RETAIL_SQL_DRIVER = "ODBC Driver 18 for SQL Server"
```

Replace `YOUR_SERVER_NAME` with the server name shown in SSMS.

## Limitations

- The dataset is small and synthetic.
- The dashboard reports sales revenue, not profit.
- Automated scheduling and production deployment are not included
in this initial version.
- Database connection settings depend on the local environment.

## Future Improvements

- Add automated ETL scheduling.
- Add unit tests and data quality tests.
- Add incremental loading and stronger duplicate handling.
- Implement a dimensional data warehouse model.
- Add CI checks using GitHub Actions.
- Expand the dataset and add more business metrics.

## Author

Created as a data engineering and analytics portfolio project.