# Tableau Public dashboard: build guide

Goal: one dashboard called **"Alphabet Financial Performance 2019–2025"** with 4 KPI tiles and 4 charts, published to Tableau Public.

## 1. Connect the data
1. Open Tableau Public → **Connect → Text file** → pick `data/processed/tableau_annual_kpis.csv`.
2. In the Data Source tab, click **Add** (next to Connections) → Text file → add the other three files:
   `tableau_revenue_mix.csv`, `tableau_cloud.csv`, `tableau_segment_profit.csv`.
3. Drag each new file to its own spot on the canvas. They will relate on `fiscal_year` automatically. If Tableau asks, set the relationship to `fiscal_year = fiscal_year`.
4. Right-click `fiscal_year` in each table → **Change Data Type → String** (so years show as labels, not summed numbers).

## 2. Calculated fields
Create these (Analysis → Create Calculated Field):

| Name | Formula |
|---|---|
| Revenue ($B) | `SUM([revenue_musd]) / 1000` |
| Total Revenue ($B) | `SUM([total_revenue_musd]) / 1000` |
| Capex ($B) | `SUM([capex_musd]) / 1000` |
| FCF ($B) | `SUM([free_cash_flow_musd]) / 1000` |
| Cloud Margin | `SUM([cloud_operating_income_musd]) / SUM([cloud_revenue_musd])` (format as %) |

## 3. Sheets
**Sheet 1: Revenue Mix**
- Columns: `fiscal_year` · Rows: `Revenue ($B)` · Color: `revenue_line`
- Marks: Bar. Add `pct_of_total_revenue` to Tooltip.
- Tip: add a filter on `revenue_line` so viewers can isolate one line.

**Sheet 2: Google Cloud Turnaround**
- Columns: `fiscal_year` (from tableau_cloud) · Rows: `Cloud Margin`
- Marks: Line. Add a reference line at 0 (Analytics pane → Constant Line → 0).
- Title: "Google Cloud: from –52% to +24% operating margin"

**Sheet 3: Capex vs Free Cash Flow**
- Columns: `fiscal_year` · Rows: `Measure Values` → keep only `Capex ($B)` and `FCF ($B)`
- Color: `Measure Names` · Marks: Bar, set to side-by-side (drag `Measure Names` to Columns after `fiscal_year`)

**Sheet 4: Operating Margin Trend**
- Columns: `fiscal_year` · Rows: `AVG(operating_margin_pct)` · Marks: Line with labels on

**Sheet 5–8: KPI tiles** (one number each, for FY2025)
- Text marks with: Total Revenue ($B), operating_margin_pct, Cloud revenue, FCF ($B)
- Filter each to `fiscal_year = 2025`

## 4. Dashboard layout
- Size: **Automatic** or 1200 × 900
- Top row: title + 4 KPI tiles
- Middle row: Revenue Mix (wide) | Cloud Turnaround
- Bottom row: Capex vs FCF | Operating Margin
- Add a text box at the bottom: "Source: Alphabet Form 10-K filings (SEC EDGAR). $ in billions."
- Use the same blue for single-series charts so it looks consistent.

## 5. Publish
File → **Save to Tableau Public As…** → name it "Alphabet Financial Performance 2019–2025". Copy the link and paste it into the README where it says *Tableau Public link*.
