-- =============================================================
-- 03_churn_overview.sql
-- Overall churn rates, trends, and revenue impact
-- =============================================================
SET search_path = churn;

-- ── 1. Overall churn rate ────────────────────────────────────
SELECT
    COUNT(*)                                              AS total_customers,
    SUM(churn::int)                                       AS churned,
    ROUND(AVG(churn::int) * 100, 2)                       AS churn_rate_pct,
    ROUND(SUM(CASE WHEN churn THEN monthly_charges END)
          * 12, 0)                                        AS annual_revenue_lost
FROM customers;


-- ── 2. Churn rate by contract type ──────────────────────────
SELECT
    contract_type,
    COUNT(*)                                              AS customers,
    SUM(churn::int)                                       AS churned,
    ROUND(AVG(churn::int) * 100, 2)                       AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2)                        AS avg_monthly_charges
FROM customers
GROUP BY contract_type
ORDER BY churn_rate_pct DESC;


-- ── 3. Churn by tenure band ──────────────────────────────────
SELECT
    CASE
        WHEN tenure_months <=  3 THEN '0–3 months'
        WHEN tenure_months <=  6 THEN '4–6 months'
        WHEN tenure_months <= 12 THEN '7–12 months'
        WHEN tenure_months <= 24 THEN '13–24 months'
        ELSE '24+ months'
    END                                                   AS tenure_band,
    COUNT(*)                                              AS customers,
    ROUND(AVG(churn::int) * 100, 2)                       AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2)                        AS avg_monthly_charges
FROM customers
GROUP BY 1
ORDER BY MIN(tenure_months);


-- ── 4. Monthly churn trend (requires usage_events) ──────────
WITH monthly_base AS (
    SELECT
        DATE_TRUNC('month', join_date)     AS cohort_month,
        DATE_TRUNC('month', churn_date)    AS churn_month,
        customer_id,
        monthly_charges
    FROM customers
    WHERE churn = TRUE
)
SELECT
    churn_month,
    COUNT(*)                                              AS churned_customers,
    SUM(monthly_charges * 12)                             AS annual_revenue_lost,
    SUM(SUM(monthly_charges * 12)) OVER (
        ORDER BY churn_month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                                                     AS cumulative_revenue_lost
FROM monthly_base
GROUP BY churn_month
ORDER BY churn_month;


-- =============================================================
