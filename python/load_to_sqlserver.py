from pathlib import Path
import os

import pandas as pd
import pyodbc


ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "data" / "processed" / "retail_transactions_clean.csv"

# Sesuaikan dengan nama server yang terlihat di SSMS.
SERVER = os.getenv("DESKTOP-D9BVEU4", r"localhost")
DATABASE = "RetailSalesDB"
DRIVER = os.getenv(
    "DESKTOP-D9BVEU4",
    "ODBC Driver 18 for SQL Server",
)

REQUIRED_COLUMNS = [
    "Transaction_ID",
    "Date",
    "Product",
    "Category",
    "Quantity",
    "Unit_Price",
    "Payment_Method",
    "City",
]


def main():
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"CSV tidak ditemukan: {CSV_FILE}")

    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom CSV tidak lengkap: {missing}")

    df = df[REQUIRED_COLUMNS].copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="raise")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="raise")
    df["Unit_Price"] = pd.to_numeric(
        df["Unit_Price"], errors="raise"
    )

    if df["Transaction_ID"].duplicated().any():
        raise ValueError("CSV mengandung Transaction_ID duplikat")

    if df.isna().any().any():
        raise ValueError("CSV mengandung nilai kosong")

    if (df["Quantity"] <= 0).any() or (df["Unit_Price"] <= 0).any():
        raise ValueError("Quantity dan Unit_Price harus positif")

    connection_string = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )

    insert_sql = """
        INSERT INTO dbo.RetailTransactions
        (
        Transaction_ID, [Date], Product, Category,
        Quantity, Unit_Price, Payment_Method, City
        )
        SELECT ?, ?, ?, ?, ?, ?, ?, ?
        WHERE NOT EXISTS
        (
        SELECT 1
        FROM dbo.RetailTransactions
        WHERE Transaction_ID = ?
        );
    """

    inserted = 0
    skipped = 0

    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()

        for row in df.itertuples(index=False, name=None):
            values = (
                row[0],
                row[1].date(),
                row[2],
                row[3],
                int(row[4]),
                float(row[5]),
                row[6],
                row[7],
                row[0],
            )
            cursor.execute(insert_sql, values)

            if cursor.rowcount == 1:
                inserted += 1
            else:
                skipped += 1

    print("=== SQL SERVER LOAD COMPLETE ===")
    print(f"CSV rows : {len(df)}")
    print(f"Inserted : {inserted}")
    print(f"Skipped : {skipped}")
    print(f"Database : {DATABASE}")
    print("Table : dbo.RetailTransactions")


if __name__ == "__main__":
    main()