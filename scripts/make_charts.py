"""
Step 3: Make the preview charts shown in the README.

Run from the project folder (after run_analysis.py):
    python scripts/make_charts.py

Saves PNGs to images/. The interactive version of these views lives in Tableau Public.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
IMG = ROOT / "images"
IMG.mkdir(exist_ok=True)

# Colors: fixed categorical order (validated colorblind-safe for adjacent pairs)
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
SURFACE, TEXT, TEXT_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": TEXT_2,
    "xtick.color": TEXT_2, "ytick.color": TEXT_2, "text.color": TEXT,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.axisbelow": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
    "font.size": 11, "axes.titlesize": 14, "axes.titleweight": "bold", "axes.titlelocation": "left",
})


def billions(ax):
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v/1000:,.0f}B"))


# ---------- Chart 1: Revenue by business line (stacked bars) ----------
mix = pd.read_csv(OUT / "q01_revenue_mix.csv")
order = ["Google Search & other", "YouTube ads", "Google Network",
         "Google subscriptions, platforms, and devices", "Google Cloud", "Other Bets"]
labels = ["Search & other", "YouTube ads", "Network",
          "Subscriptions, platforms & devices", "Google Cloud", "Other Bets"]
wide = mix.pivot(index="fiscal_year", columns="revenue_line", values="revenue_musd")[order]

fig, ax = plt.subplots(figsize=(10, 5.5))
bottom = pd.Series(0, index=wide.index)
for col, label, color in zip(order, labels, SERIES):
    ax.bar(wide.index, wide[col], bottom=bottom, color=color, width=0.65,
           edgecolor=SURFACE, linewidth=2, label=label)
    bottom += wide[col]
# Label each bar with the reported total revenue (includes small hedging gains/losses)
totals = pd.read_csv(ROOT / "data" / "raw" / "annual_financials.csv").set_index("fiscal_year")["total_revenue_musd"]
for year, total in totals.items():
    ax.text(year, bottom[year] + 5000, f"${total/1000:,.0f}B", ha="center", color=TEXT, fontsize=10)
fig.text(0.01, 0.01, "Bar labels show total reported revenue. Hedging gains/losses (under 1% of revenue) are not shown as a segment.",
         color=TEXT_2, fontsize=8)
billions(ax)
ax.set_title("Alphabet revenue by business line, 2019–2025")
ax.legend(loc="upper left", frameon=False, fontsize=9)
ax.set_ylim(0, 450000)
fig.tight_layout()
fig.savefig(IMG / "01_revenue_by_line.png", dpi=160)
plt.close(fig)

# ---------- Chart 2: Google Cloud, revenue and margin (two panels, no dual axis) ----------
cloud = pd.read_csv(OUT / "q05_cloud_profitability.csv")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
ax1.bar(cloud.fiscal_year, cloud.cloud_revenue_musd, color=SERIES[0], width=0.65)
for x, y in zip(cloud.fiscal_year, cloud.cloud_revenue_musd):
    ax1.text(x, y + 800, f"${y/1000:.1f}B", ha="center", fontsize=9)
billions(ax1)
ax1.set_title("Google Cloud revenue")
ax2.plot(cloud.fiscal_year, cloud.cloud_operating_margin_pct, color=SERIES[0], linewidth=2,
         marker="o", markersize=8, markeredgecolor=SURFACE, markeredgewidth=2)
ax2.axhline(0, color=TEXT_2, linewidth=1)
ax2.set_ylim(-60, 32); ax2.set_xlim(2018.4, 2025.4)
for x, y in zip(cloud.fiscal_year, cloud.cloud_operating_margin_pct):
    ax2.text(x - 0.1, y + 3, f"{y:.0f}%", ha="right", fontsize=9)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax2.set_title("Google Cloud operating margin")
fig.tight_layout()
fig.savefig(IMG / "02_cloud_profitability.png", dpi=160)
plt.close(fig)

# ---------- Chart 3: Capex vs free cash flow (grouped bars) ----------
cash = pd.read_csv(OUT / "q06_capex_and_free_cash_flow.csv")
fig, ax = plt.subplots(figsize=(10, 5))
w = 0.36
ax.bar(cash.fiscal_year - w/2 - 0.01, cash.capex_musd, width=w, color=SERIES[1], label="Capital expenditures")
ax.bar(cash.fiscal_year + w/2 + 0.01, cash.free_cash_flow_musd, width=w, color=SERIES[0], label="Free cash flow")
last = cash.iloc[-1]
ax.text(last.fiscal_year - w/2, last.capex_musd + 2000, f"${last.capex_musd/1000:.0f}B", ha="center", fontsize=9)
ax.text(last.fiscal_year + w/2, last.free_cash_flow_musd + 2000, f"${last.free_cash_flow_musd/1000:.0f}B", ha="center", fontsize=9)
billions(ax)
ax.set_title("Capex nearly quadrupled since 2019 while free cash flow flattened")
ax.legend(loc="upper left", frameon=False)
fig.tight_layout()
fig.savefig(IMG / "03_capex_vs_fcf.png", dpi=160)
plt.close(fig)

# ---------- Chart 4: Operating margin trend ----------
m = pd.read_csv(OUT / "q04_margins_and_cost_structure.csv")
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(m.fiscal_year, m.operating_margin_pct, color=SERIES[0], linewidth=2, marker="o",
        markersize=8, markeredgecolor=SURFACE, markeredgewidth=2)
for x, y in zip(m.fiscal_year, m.operating_margin_pct):
    ax.text(x, y + 0.8, f"{y:.1f}%", ha="center", fontsize=9)
ax.set_ylim(15, 40)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax.set_title("Alphabet operating margin")
fig.tight_layout()
fig.savefig(IMG / "04_operating_margin.png", dpi=160)
plt.close(fig)

print("Charts saved to images/")
