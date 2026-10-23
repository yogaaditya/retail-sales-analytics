import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyodbc

# Lokasi project
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data" / "raw" / "retail_transactions.csv"
CLEAN_FILE = BASE_DIR / "data" / "processed" / "retail_transactions_clean.csv"
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)

# Logging ke file dan terminal
log_file = LOG_DIR / "etl_pipeline.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
    logging.FileHandler(log_file, encoding="utf-8"),
    logging.StreamHandler(sys.stdout),
    ],
    force=True,
)

SERVER = os.getenv("DESKTOP-D9BVEU4", "localhost")
DATABASE = os.getenv("DESKTOP-D9BVEU4", "RetailSalesDB")
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


def extract():
    """Baca data mentah."""
    logging.info("EXTRACT: membaca CSV mentah")

    if not RAW_FILE.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {RAW_FILE}")

    df = pd.read_csv(RAW_FILE, dtype=str)

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Kolom wajib tidak tersedia: {sorted(missing)}")

    logging.info("EXTRACT selesai: %s baris", len(df))
    return df


def transform(df):
    """Validasi dan transformasi data."""
    logging.info("TRANSFORM: membersihkan data")

    df = df[REQUIRED_COLUMNS].copy()

    # Rapikan spasi pada kolom teks
    for column in [
        "Transaction_ID",
        "Product",
        "Category",
        "Payment_Method",
        "City",
    ]:
        df[column] = df[column].str.strip()

    # Konversi tipe data
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["Unit_Price"] = pd.to_numeric(
    df["Unit_Price"], errors="coerce"
    )

    # Baris yang tidak valid tidak boleh masuk ke SQL Server
    valid = (
        df["Transaction_ID"].notna()
        & df["Transaction_ID"].ne("")
        & df["Date"].notna()
        & df["Product"].notna()
        & df["Product"].ne("")
        & df["Category"].notna()
        & df["Category"].ne("")
        & df["Payment_Method"].notna()
        & df["Payment_Method"].ne("")
        & df["City"].notna()
        & df["City"].ne("")
        & df["Quantity"].notna()
        & df["Unit_Price"].notna()
        & df["Quantity"].gt(0)
        & (df["Quantity"] % 1 == 0)
        & df["Unit_Price"].gt(0)
    )

    rejected_count = int((~valid).sum())
    df = df.loc[valid].copy()

    # Satu ID transaksi hanya boleh muncul sekali
    duplicate_mask = df["Transaction_ID"].duplicated(keep="first")
    rejected_count += int(duplicate_mask.sum())
    df = df.loc[~duplicate_mask].copy()

    df["Quantity"] = df["Quantity"].astype(int)
    df["Unit_Price"] = df["Unit_Price"].round(2)
    df["Sales"] = df["Quantity"] * df["Unit_Price"]

    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    logging.info(
        "TRANSFORM selesai: %s valid, %s ditolak",
        len(df),
        rejected_count,
    )

    return df, rejected_count


def load(df):
    """Muat transaksi baru ke SQL Server."""
    logging.info("LOAD: menghubungkan ke SQL Server")

    connection_string = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )

    inserted = 0
    skipped = 0

    insert_sql = """
        INSERT INTO dbo.RetailTransactions
        (
            Transaction_ID, [Date], Product, Category,
            Quantity, Unit_Price, Payment_Method, City
        )
        SELECT ?, ?, ?, ?, ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1
            FROM dbo.RetailTransactions
            WHERE Transaction_ID = ?
        );
    """

    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()

        # Pastikan tabel target tersedia
        cursor.execute("""
        SELECT OBJECT_ID('dbo.RetailTransactions', 'U')
        """)
        if cursor.fetchone()[0] is None:
            raise RuntimeError(
                "Tabel dbo.RetailTransactions tidak ditemukan. "
                "Buat tabel pada Tahap 4 terlebih dahulu."
            )

        for row in df.itertuples(index=False):
            params = (
                row.Transaction_ID,
                row.Date,
                row.Product,
                row.Category,
                int(row.Quantity),
                float(row.Unit_Price),
                row.Payment_Method,
                row.City,
                row.Transaction_ID,
            )

            cursor.execute(insert_sql, params)

            # @@ROWCOUNT menunjukkan apakah INSERT dilakukan
            cursor.execute("SELECT @@ROWCOUNT")
            affected = cursor.fetchone()[0]

            if affected:
                inserted += 1
            else:
                skipped += 1

        conn.commit()

    logging.info(
        "LOAD selesai: %s ditambahkan, %s dilewati",
        inserted,
        skipped,
    )

    return inserted, skipped


def main():
    start = datetime.now()
    logging.info("===== ETL PIPELINE DIMULAI =====")

    try:
        raw_df = extract()
        clean_df, rejected_count = transform(raw_df)

        # Simpan hasil transformasi untuk audit
        CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
        clean_df.to_csv(CLEAN_FILE, index=False)

        inserted, skipped = load(clean_df)

        logging.info(
            "RINGKASAN: input=%s, valid=%s, ditolak=%s, "
            "ditambahkan=%s, dilewati=%s",
            len(raw_df),
            len(clean_df),
            rejected_count,
            inserted,
            skipped,
        )
        logging.info(
            "ETL BERHASIL dalam %s",
            datetime.now() - start,
        )

    except Exception:
        logging.exception("ETL GAGAL")
        raise


if __name__ == "__main__":
 main()