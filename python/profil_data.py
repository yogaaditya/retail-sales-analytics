from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "raw" / "retail_transactions.csv"
OUTPUT_DIR = ROOT / "report" / "data_profile"

Required_columns = [
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
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"File dataset tidak ditemukan: {DATA_FILE}"
        )
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Membaca data sumber tanpa memodifikasi CSV.
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")

    # Mengecek permintaan kolom
    missing_columns = [
        col for col in Required_columns if col not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            f"Kolom wajib tidak ditemukan: {missing_columns}"
        )

    # memisahkan tanggal dan numerik untuk analisis
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["Unit_Price"] = pd.to_numeric(df["Unit_Price"], errors="coerce")

    # tambahkan kolom yang dihitung untuk salinan analisa
    df["Sales"] = df["Quantity"] * df["Unit_Price"]

    # Profil kolom
    column_profile = pd.DataFrame({
        "Column": df.columns,
        "Data_Type": [str(dtype) for dtype in df.dtypes],
        "Missing_Count": df.isna().sum().values,
        "Unique_Count": df.nunique(dropna=True).values,
    })

    # Nilai yang kosong pada kolom
    missing_profile = pd.DataFrame({
        "Column": df.columns,
        "Missing_Count": df.isna().sum().values,
        "Missing_Percent": (
            df.isna().mean().values * 100
        ).round(2)
    })

    # Ringkasan Metrik
    summary = {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_transaction_ids": int(df["Transaction_ID"].duplicated().sum()),
        "missing_cells": int(df.isna().sum().sum()),
        "total_sales": round(float(df["Sales"].sum()), 2),
        "total_units": int(df["Quantity"].sum()),
        "unique_products": int(df["Product"].nunique()),
        "unique_cities": int(df["City"].nunique()),
        "date_min": str(df["Date"].min().date()),
        "date_max": str(df["Date"].max().date()),
        "sales_by_product": {
            str(k): round(float(v), 2)
            for k, v in df.groupby("Product")["Sales"]
            .sum().sort_values(ascending=False).items()
        },
        "sales_by_payment": {
            str(k): round(float(v), 2)
            for k, v in df.groupby("Payment_Method")["Sales"]
            .sum().sort_values(ascending=False).items()
        },
    }

    # Menyimpan file report
    column_profile.to_csv(
        OUTPUT_DIR / "column_profile.csv", index=False
    )
    missing_profile.to_csv(
        OUTPUT_DIR / "missing_values.csv", index=False
    )
    df.to_csv(
        OUTPUT_DIR / "profiled_transactions.csv", index=False,
        date_format="%Y-%m-%d"
    )
    with (OUTPUT_DIR / "dataset_profile.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)
    with (OUTPUT_DIR / "summary.txt").open(
        "w", encoding="utf-8"
    ) as file:
        file.write("RETAIL TRANSACTION DATA PROFILE\n")
        file.write("=" * 35 + "\n")
        for key, value in summary.items():
            file.write(f"{key}: {value}\n")

    # Output.

    print("=== RETAIL DATA PROFILING COMPLETE ===")
    print(f"Rows                  : {summary['row_count']}")
    print(f"Columns               : {summary['column_count']}")
    print(f"Duplicate rows        : {summary['duplicate_rows']}")
    print(
        "Duplicate transaction IDs: "
        f"{summary['duplicate_transaction_ids']}"
    )
    print(f"Missing cells         : {summary['missing_cells']}")
    print(f"Total units           : {summary['total_units']}")
    print(f"Total sales           : Rp{summary['total_sales']:,.0f}")
    print(f"Unique products       : {summary['unique_products']}")
    print(f"Unique cities         : {summary['unique_cities']}")
    print(f"Reports saved to      : {OUTPUT_DIR}")

if __name__ == "__main__":
    main()