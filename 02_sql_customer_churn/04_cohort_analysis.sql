-- =============================================================
-- 04_cohort_analysis.sql
-- Monthly cohort retention table — pivoted
-- =============================================================
SET search_path = churn;


WITH cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', join_date)::date   AS cohort_month
    FROM customers
),
customer_months AS (
    SELECT
        c.customer_id,
        c.cohort_month,
        DATE_TRUNC('month', e.event_month)::date AS activity_month,
        EXTRACT(YEAR FROM AGE(e.event_month, c.cohort_month)) * 12
          + EXTRACT(MONTH FROM AGE(e.event_month, c.cohort_month))
                                               AS month_number
    FROM cohorts c
    JOIN usage_events e USING (customer_id)
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_size
    FROM cohorts
    GROUP BY cohort_month
),
retention AS (
    SELECT
        cm.cohort_month,
        cm.month_number,
        COUNT(DISTINCT cm.customer_id)         AS active_customers
    FROM customer_months cm
    GROUP BY cm.cohort_month, cm.month_number
)
SELECT
    r.cohort_month,
    cs.cohort_size,
    r.month_number,
    r.active_customers,
    ROUND(r.active_customers * 100.0 / cs.cohort_size, 1) AS retention_rate
FROM retention r
JOIN cohort_sizes cs USING (cohort_month)
ORDER BY r.cohort_month, r.month_number;


-- =============================================================
