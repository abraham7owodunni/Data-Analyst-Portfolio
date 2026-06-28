-- =============================================================
-- 05_churn_drivers.sql
-- Feature-level churn rate comparison (SQL-based feature importance)
--
-- Purpose: Identify which customer attributes most strongly
-- predict churn by comparing each feature's churn rate against
-- the overall baseline. The "lift" column quantifies how much
-- more (or less) likely a segment is to churn vs the average.
-- =============================================================
SET search_path = churn;


-- ── 1. Baseline churn rate (reference point) ─────────────────
-- Everything below is compared against this number.
SELECT
    ROUND(AVG(churn::int) * 100, 2) AS overall_churn_rate_pct
FROM customers;


-- ── 2. Churn by contract type ────────────────────────────────
SELECT
    'Contract Type'                                       AS feature,
    contract_type                                         AS segment,
    COUNT(*)                                              AS customers,
    ROUND(AVG(churn::int) * 100, 2)                       AS churn_rate_pct,
    ROUND(AVG(churn::int) / NULLIF((SELECT AVG(churn::int) FROM customers), 0), 2) AS churn_lift
FROM customers
GROUP BY contract_type
ORDER BY churn_rate_pct DESC;


-- ── 3. Churn by internet service ─────────────────────────────
SELECT
    'Internet Service'                                    AS feature,
    internet_service                                      AS segment,
    COUNT(*)                                              AS customers,
    ROUND(AVG(churn::int) * 100, 2)                       AS churn_rate_pct,
    ROUND(AVG(churn::int) / NULLIF((SELECT AVG(churn::int) FROM customers), 0), 2) AS churn_lift
FROM customers
GROUP BY internet_service
ORDER BY churn_rate_pct DESC;


-- ── 4. Churn by payment method ───────────────────────────────
SELECT
    'Payment Method'                                      AS feature,
    payment_method                                        AS segment,
    COUNT(*)                                              AS customers,
    ROUND(AVG(churn::int) * 100, 2)                       AS churn_rate_pct,
    ROUND(AVG(churn::int) / NULLIF((SELECT AVG(churn::int) FROM customers), 0), 2) AS churn_lift
FROM customers
GROUP BY payment_method
ORDER BY churn_rate_pct DESC;


-- ── 5. Churn by tech support availability ────────────────────
SELECT
    'Tech Support'                                        AS feature,
    tech_support                                          AS segment,
    COUNT(*)                                              AS customers,
    ROUND(AVG(churn::int) * 100, 2)                       AS churn_rate_pct,
    ROUND(AVG(churn::int) / NULLIF((SELECT AVG(churn::int) FROM customers), 0), 2) AS churn_lift
FROM customers
GROUP BY tech_support
ORDER BY churn_rate_pct DESC;


-- ── 6. Interaction effect: internet service x tech support ──
-- High-risk combinations often hide in feature interactions.
-- Fibre customers WITHOUT tech support are a classic churn trap.
SELECT
    internet_service,
    tech_support,
    COUNT(*)                                              AS customers,
    ROUND(AVG(churn::int) * 100, 2)                       AS churn_rate_pct,
    ROUND(
        AVG(churn::int) / NULLIF((SELECT AVG(churn::int) FROM customers), 0),
        2
    )                                                     AS churn_lift
FROM customers
GROUP BY internet_service, tech_support
ORDER BY churn_rate_pct DESC;


-- ── 7. Unified driver ranking (all features in one table) ────
-- Stacks every feature's segments together and ranks the
-- highest-churn segments across the whole customer base.
-- This is the "feature importance" summary an analyst presents.
WITH feature_churn AS (
    SELECT 'Contract Type'    AS feature, contract_type    AS segment,
           COUNT(*) AS customers, AVG(churn::int) AS churn_rate
    FROM customers GROUP BY contract_type
    UNION ALL
    SELECT 'Internet Service', internet_service,
           COUNT(*), AVG(churn::int)
    FROM customers GROUP BY internet_service
    UNION ALL
    SELECT 'Payment Method', payment_method,
           COUNT(*), AVG(churn::int)
    FROM customers GROUP BY payment_method
    UNION ALL
    SELECT 'Tech Support', tech_support,
           COUNT(*), AVG(churn::int)
    FROM customers GROUP BY tech_support
)
SELECT
    feature,
    segment,
    customers,
    ROUND(churn_rate * 100, 2)                            AS churn_rate_pct,
    ROUND(churn_rate / (SELECT AVG(churn::int) FROM customers), 2) AS churn_lift,
    RANK() OVER (ORDER BY churn_rate DESC)                AS churn_risk_rank
FROM feature_churn
WHERE customers >= 50          -- ignore tiny, noisy segments
ORDER BY churn_rate_pct DESC
LIMIT 15;
