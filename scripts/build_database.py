"""
Step 1: Check the raw 10-K data and load it into a SQLite database.

Run from the project folder:
    python scripts/build_database.py

What it does:
  1. Reads the three raw CSV files in data/raw/
  2. Runs "tie-out" checks (do the pieces add up to the reported totals?)
  3. Writes everything into data/alphabet.db so the SQL queries can run on it
"""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "alphabet.db"

revenue = pd.read_csv(RAW / "revenue_by_line.csv")
financials = pd.read_csv(RAW / "annual_financials.csv")
segments = pd.read_csv(RAW / "segment_operating_income.csv")

# ---------- Tie-out checks ----------
errors = []
for _, row in financials.iterrows():
    year = row["fiscal_year"]

    # Check 1: revenue lines add up to total revenue
    lines_total = revenue.loc[revenue.fiscal_year == year, "revenue_musd"].sum()
    if lines_total != row["total_revenue_musd"]:
        errors.append(f"{year}: revenue lines {lines_total} != total {row['total_revenue_musd']}")

    # Check 2: revenue minus all expenses = operating income
    expenses = (row["cost_of_revenues_musd"] + row["rd_musd"] + row["sales_marketing_musd"]
                + row["general_admin_musd"] + row["ec_fines_musd"])
    if row["total_revenue_musd"] - expenses != row["operating_income_musd"]:
        errors.append(f"{year}: revenue - expenses != operating income")

    # Check 3: segment operating income adds up to total operating income
    seg_total = segments.loc[segments.fiscal_year == year, "operating_income_musd"].sum()
    if seg_total != row["operating_income_musd"]:
        errors.append(f"{year}: segments {seg_total} != operating income {row['operating_income_musd']}")

if errors:
    raise SystemExit("Tie-out FAILED:\n" + "\n".join(errors))
print(f"All tie-out checks passed for {len(financials)} fiscal years.")

# ---------- Load into SQLite ----------
DB_PATH.unlink(missing_ok=True)
with sqlite3.connect(DB_PATH) as con:
    revenue.to_sql("revenue_by_line", con, index=False)
    financials.to_sql("annual_financials", con, index=False)
    segments.to_sql("segment_operating_income", con, index=False)
print(f"Database written to {DB_PATH.relative_to(ROOT)}")
