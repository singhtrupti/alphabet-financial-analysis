/* =====================================================================
   Alphabet Inc. Financial Analysis, FY2019 to FY2025
   Source: Alphabet Form 10-K filings (SEC EDGAR). All $ in millions.
   Dialect: SQLite (standard SQL; runs in BigQuery with small changes)

   Tables:
     revenue_by_line           (fiscal_year, segment, revenue_line, revenue_musd)
     annual_financials         (one row per year: P&L, cash flow, headcount)
     segment_operating_income  (fiscal_year, segment, operating_income_musd, basis)

   Each query starts with a "-- name:" line so scripts/run_analysis.py
   can run it and save the result to outputs/<name>.csv
   ===================================================================== */


-- name: q01_revenue_mix
-- Business question: How much of Alphabet's revenue comes from each business line,
-- and how has that mix shifted?
SELECT
    r.fiscal_year,
    r.revenue_line,
    r.revenue_musd,
    ROUND(100.0 * r.revenue_musd / f.total_revenue_musd, 1) AS pct_of_total_revenue
FROM revenue_by_line AS r
JOIN annual_financials AS f
    ON r.fiscal_year = f.fiscal_year
WHERE r.revenue_line <> 'Hedging gains (losses)'
ORDER BY r.fiscal_year, r.revenue_musd DESC;


-- name: q02_yoy_growth_by_line
-- Business question: Which business lines are growing fastest year over year?
-- Technique: LAG() window function to pull the prior year's value.
WITH lagged AS (
    SELECT
        fiscal_year,
        revenue_line,
        revenue_musd,
        LAG(revenue_musd) OVER (PARTITION BY revenue_line ORDER BY fiscal_year) AS prior_year_musd
    FROM revenue_by_line
    WHERE revenue_line <> 'Hedging gains (losses)'
)
SELECT
    fiscal_year,
    revenue_line,
    revenue_musd,
    prior_year_musd,
    ROUND(100.0 * (revenue_musd - prior_year_musd) / prior_year_musd, 1) AS yoy_growth_pct
FROM lagged
WHERE prior_year_musd IS NOT NULL
ORDER BY revenue_line, fiscal_year;


-- name: q03_cagr_and_growth_contribution
-- Business question: Over 2019 to 2025, which lines grew fastest (CAGR),
-- and which contributed the most dollars to total revenue growth?
WITH endpoints AS (
    SELECT
        revenue_line,
        SUM(CASE WHEN fiscal_year = 2019 THEN revenue_musd END) AS rev_2019,
        SUM(CASE WHEN fiscal_year = 2025 THEN revenue_musd END) AS rev_2025
    FROM revenue_by_line
    WHERE revenue_line <> 'Hedging gains (losses)'
    GROUP BY revenue_line
)
SELECT
    revenue_line,
    rev_2019,
    rev_2025,
    rev_2025 - rev_2019 AS dollar_growth_musd,
    ROUND(100.0 * (POWER(1.0 * rev_2025 / rev_2019, 1.0 / 6) - 1), 1) AS cagr_6yr_pct,
    ROUND(100.0 * (rev_2025 - rev_2019)
          / SUM(rev_2025 - rev_2019) OVER (), 1) AS pct_of_total_growth
FROM endpoints
ORDER BY dollar_growth_musd DESC;


-- name: q04_margins_and_cost_structure
-- Business question: Is Alphabet getting more profitable? Where does each revenue dollar go?
SELECT
    fiscal_year,
    total_revenue_musd,
    ROUND(100.0 * cost_of_revenues_musd  / total_revenue_musd, 1) AS cost_of_rev_pct,
    ROUND(100.0 * (total_revenue_musd - cost_of_revenues_musd) / total_revenue_musd, 1) AS gross_margin_pct,
    ROUND(100.0 * rd_musd                / total_revenue_musd, 1) AS rd_pct,
    ROUND(100.0 * sales_marketing_musd   / total_revenue_musd, 1) AS sales_marketing_pct,
    ROUND(100.0 * general_admin_musd     / total_revenue_musd, 1) AS general_admin_pct,
    ROUND(100.0 * operating_income_musd  / total_revenue_musd, 1) AS operating_margin_pct,
    ROUND(100.0 * net_income_musd        / total_revenue_musd, 1) AS net_margin_pct
FROM annual_financials
ORDER BY fiscal_year;


-- name: q05_cloud_profitability
-- Business question: When did Google Cloud turn profitable, and how fast is its margin improving?
SELECT
    r.fiscal_year,
    r.revenue_musd                              AS cloud_revenue_musd,
    s.operating_income_musd                     AS cloud_operating_income_musd,
    ROUND(100.0 * s.operating_income_musd / r.revenue_musd, 1) AS cloud_operating_margin_pct,
    CASE WHEN s.operating_income_musd > 0 THEN 'Profitable' ELSE 'Loss' END AS status,
    s.basis
FROM revenue_by_line AS r
JOIN segment_operating_income AS s
    ON  r.fiscal_year = s.fiscal_year
    AND s.segment = 'Google Cloud'
WHERE r.revenue_line = 'Google Cloud'
ORDER BY r.fiscal_year;


-- name: q06_capex_and_free_cash_flow
-- Business question: How much is Alphabet investing in AI infrastructure (capex),
-- and what does that do to free cash flow?
SELECT
    fiscal_year,
    operating_cash_flow_musd,
    capex_musd,
    operating_cash_flow_musd - capex_musd                               AS free_cash_flow_musd,
    ROUND(100.0 * capex_musd / total_revenue_musd, 1)                   AS capex_pct_of_revenue,
    ROUND(100.0 * (operating_cash_flow_musd - capex_musd) / total_revenue_musd, 1) AS fcf_margin_pct,
    ROUND(1.0 * capex_musd / depreciation_musd, 2)                      AS capex_to_depreciation_ratio,
    ROUND(100.0 * (capex_musd - LAG(capex_musd) OVER (ORDER BY fiscal_year))
          / LAG(capex_musd) OVER (ORDER BY fiscal_year), 1)             AS capex_yoy_growth_pct
FROM annual_financials
ORDER BY fiscal_year;


-- name: q07_productivity_per_employee
-- Business question: How efficiently does Alphabet turn headcount into revenue and profit?
SELECT
    fiscal_year,
    employees,
    ROUND(1000.0 * total_revenue_musd    / employees, 0) AS revenue_per_employee_kusd,
    ROUND(1000.0 * operating_income_musd / employees, 0) AS op_income_per_employee_kusd,
    employees - LAG(employees) OVER (ORDER BY fiscal_year) AS headcount_change
FROM annual_financials
ORDER BY fiscal_year;


-- name: q08_segment_profit_mix
-- Business question: Which segments generate the profit, and which consume it?
SELECT
    s.fiscal_year,
    s.segment,
    s.operating_income_musd,
    ROUND(100.0 * s.operating_income_musd / f.operating_income_musd, 1) AS pct_of_total_operating_income,
    RANK() OVER (PARTITION BY s.fiscal_year ORDER BY s.operating_income_musd DESC) AS profit_rank
FROM segment_operating_income AS s
JOIN annual_financials AS f
    ON s.fiscal_year = f.fiscal_year
ORDER BY s.fiscal_year, profit_rank;
