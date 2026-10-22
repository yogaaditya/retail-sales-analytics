
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "raw" / "retail_transactions.csv"
OUTPUT_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "report" / "data_profile"

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

VALID_CATEGORIES = {"Makanan", "Minuman"}
VALID_PAYMENTS = {"Tunai", "QRIS", "Debit"}


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset tidak ditemukan: {INPUT_FILE}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Load source data. Never overwrite the raw CSV.
    df = pd.read_csv(INPUT_FILE, dtype=str, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    missing_columns = [
        col for col in REQUIRED_COLUMNS if col not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            f"Kolom wajib tidak ditemukan: {missing_columns}"
        )

    # Normalize text fields.
    text_columns = [
        "Transaction_ID",
        "Product",
        "Category",
        "Payment_Method",
        "City",
    ]
    for column in text_columns:
        df[column] = df[column].str.strip()

    # Parse dates and numeric values.
    df["Date"] = pd.to_datetime(
        df["Date"], errors="coerce", format="%Y-%m-%d"
    )
    df["Quantity"] = pd.to_numeric(
        df["Quantity"], errors="coerce"
    )
    df["Unit_Price"] = pd.to_numeric(
        df["Unit_Price"], errors="coerce"
    )

    # Record every validation issue per row.
    issues = pd.Series("", index=df.index, dtype="string")

    def add_issue(mask, message):
        nonlocal issues
        mask = mask.fillna(True)
        issues.loc[mask] = issues.loc[mask].apply(
            lambda current: (
                f"{current}; {message}" if current else message
            )
        )

    # Required values must be present.
    for column in REQUIRED_COLUMNS:
        add_issue(
            df[column].isna() | df[column].eq(""),
            f"{column} kosong",
        )

    # Validate date and numeric values.
    add_issue(df["Date"].isna(), "Tanggal tidak valid")
    add_issue(
        df["Quantity"].isna(),
        "Quantity bukan angka atau kosong",
    )
    add_issue(
        df["Unit_Price"].isna(),
        "Unit_Price bukan angka atau kosong",
    )

    # Business rules.
    add_issue(
        df["Quantity"].notna()
        & (df["Quantity"] <= 0),
        "Quantity harus lebih besar dari 0",
    )
    add_issue(
        df["Quantity"].notna()
        & (df["Quantity"] % 1 != 0),
        "Quantity harus bilangan bulat",
    )
    add_issue(
        df["Unit_Price"].notna()
        & (df["Unit_Price"] <= 0),
        "Unit_Price harus lebih besar dari 0",
    )
    add_issue(
        ~df["Category"].isin(VALID_CATEGORIES),
        "Category tidak dikenal",
    )
    add_issue(
        ~df["Payment_Method"].isin(VALID_PAYMENTS),
        "Payment_Method tidak dikenal",
    )

    # Transaction ID must be unique.
    valid_id = df["Transaction_ID"].notna() & (
        df["Transaction_ID"] != ""
    )
    duplicate_id = (
        valid_id
        & df["Transaction_ID"].duplicated(keep=False)
    )
    add_issue(duplicate_id, "Transaction_ID duplikat")

    # Exact duplicate records are also flagged.
    duplicate_row = df.duplicated(keep=False)
    add_issue(duplicate_row, "Baris duplikat identik")

    # Separate accepted and rejected records.
    rejected_mask = issues.ne("")
    clean = df.loc[~rejected_mask].copy()
    rejected = df.loc[rejected_mask].copy()

    # Add calculated sales only to accepted records.
    clean["Sales"] = clean["Quantity"] * clean["Unit_Price"]
    clean["Date"] = clean["Date"].dt.strftime("%Y-%m-%d")
    clean["Quantity"] = clean["Quantity"].astype("int64")
    clean["Unit_Price"] = clean["Unit_Price"].astype("int64")
    rejected["Validation_Issues"] = issues.loc[rejected_mask]

    clean_file = OUTPUT_DIR / "retail_transactions_clean.csv"
    rejected_file = OUTPUT_DIR / "retail_transactions_rejected.csv"
    report_file = REPORT_DIR / "cleaning_summary.txt"
    quality_file = REPORT_DIR / "data_quality_report.csv"

    clean.to_csv(clean_file, index=False, encoding="utf-8-sig")
    rejected.to_csv(
        rejected_file, index=False, encoding="utf-8-sig"
    )

    # Summary of the cleaning process.
    summary = [
        "RETAIL DATA CLEANING SUMMARY", "=" * 32,
        f"Input rows: {len(df)}",
        f"Accepted rows: {len(clean)}",
        f"Rejected rows: {len(rejected)}",
        f"Rows with issues: {int(rejected_mask.sum())}",
        f"Total sales in accepted rows: {clean['Sales'].sum():,.0f}","",
        f"Clean file: {clean_file}",
        f"Rejected file: {rejected_file}",
    ]
    report_file.write_text(
    "\n".join(summary), encoding="utf-8"
    )

    quality_checks = {
        "Required fields populated": (
            df[REQUIRED_COLUMNS].isna()
            | df[REQUIRED_COLUMNS].eq("")
        ).any(axis=1),
        "Date valid": df["Date"].isna(),
        "Quantity positive integer": (
            df["Quantity"].isna()
            | (df["Quantity"] <= 0)
            | (df["Quantity"] % 1 != 0)
        ),
        "Unit price positive": (
            df["Unit_Price"].isna()
            | (df["Unit_Price"] <= 0)
        ),
        "Category recognized": ~df["Category"].isin(
            VALID_CATEGORIES
        ),
        "Payment method recognized": ~df["Payment_Method"].isin(
            VALID_PAYMENTS
        ),
        "Transaction ID unique": duplicate_id,
        "No exact duplicate rows": duplicate_row,
    }
    quality = pd.DataFrame([
        {
            "Rule": rule,
            "Failed_Rows": int(mask.sum()),
            "Status": "PASS" if not mask.any() else "CHECK",
        }
        for rule, mask in quality_checks.items()
  ])
    quality.to_csv(quality_file, index=False)

    print("=== DATA CLEANING COMPLETE ===")
    print(f"Input rows : {len(df)}")
    print(f"Accepted rows : {len(clean)}")
    print(f"Rejected rows : {len(rejected)}")
    print(f"Total sales : Rp{clean['Sales'].sum():,.0f}")
    print(f"Clean file : {clean_file}")
    print(f"Rejected file : {rejected_file}")
    print(f"Summary : {report_file}")
    print(f"Quality report: {quality_file}")


if __name__ == "__main__":
    main()