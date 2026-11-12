"""
Step 2: Run every SQL query in sql/analysis_queries.sql and save results.

Run from the project folder (after build_database.py):
    python scripts/run_analysis.py

Outputs:
  outputs/<query_name>.csv          one file per SQL query
  data/processed/tableau_*.csv      tidy files to connect in Tableau Public
"""
import math
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "alphabet.db"
SQL_PATH = ROOT / "sql" / "analysis_queries.sql"
OUT = ROOT / "outputs"
PROCESSED = ROOT / "data" / "processed"
OUT.mkdir(exist_ok=True)
PROCESSED.mkdir(parents=True, exist_ok=True)


def split_queries(sql_text):
    """Split the .sql file into {name: query} using the '-- name:' markers."""
    queries, name, lines = {}, None, []
    for line in sql_text.splitlines():
        if line.strip().startswith("-- name:"):
            if name:
                queries[name] = "\n".join(lines)
            name, lines = line.split(":", 1)[1].strip(), []
        elif name:
            lines.append(line)
    if name:
        queries[name] = "\n".join(lines)
    return queries


con = sqlite3.connect(DB_PATH)
# Some older SQLite builds don't include POWER(); add it so the CAGR query always runs.
con.create_function("POWER", 2, math.pow)

queries = split_queries(SQL_PATH.read_text())
results = {}
for name, query in queries.items():
    df = pd.read_sql_query(query, con)
    df.to_csv(OUT / f"{name}.csv", index=False)
    results[name] = df
    print(f"{name}: {len(df)} rows -> outputs/{name}.csv")

# ---------- Tableau-ready files ----------
results["q01_revenue_mix"].to_csv(PROCESSED / "tableau_revenue_mix.csv", index=False)

kpis = (results["q04_margins_and_cost_structure"]
        .merge(results["q06_capex_and_free_cash_flow"], on="fiscal_year")
        .merge(results["q07_productivity_per_employee"], on="fiscal_year"))
kpis.to_csv(PROCESSED / "tableau_annual_kpis.csv", index=False)

results["q05_cloud_profitability"].to_csv(PROCESSED / "tableau_cloud.csv", index=False)
results["q08_segment_profit_mix"].to_csv(PROCESSED / "tableau_segment_profit.csv", index=False)
print("Tableau files written to data/processed/")

con.close()
