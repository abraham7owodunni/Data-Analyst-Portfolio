-- =============================================================
-- 06_at_risk_customers.sql
-- Score current customers by churn risk for targeted outreach
-- =============================================================
SET search_path = churn;


WITH risk_scores AS (
    SELECT
        c.customer_id,
        c.contract_type,
        c.tenure_months,
        c.monthly_charges,
        c.internet_service,
        c.tech_support,

        -- Base risk from contract type
        CASE c.contract_type
            WHEN 'Month-to-month' THEN 40
            WHEN 'One year'       THEN 15
            WHEN 'Two year'       THEN 5
        END

        -- Tenure risk (early-life customers are highest risk)
        + CASE
            WHEN c.tenure_months <=  3 THEN 25
            WHEN c.tenure_months <=  6 THEN 20
            WHEN c.tenure_months <= 12 THEN 10
            ELSE 0
          END

        -- Service risk
        + CASE
            WHEN c.internet_service = 'Fiber optic'
              AND c.tech_support IN ('No', 'No internet service') THEN 20
            ELSE 0
          END

        -- Support ticket risk (3-month lookback)
        + COALESCE((
            SELECT SUM(s.support_tickets) * 3
            FROM usage_events s
            WHERE s.customer_id = c.customer_id
              AND s.event_month >= CURRENT_DATE - INTERVAL '3 months'
          ), 0)

        -- Late payment risk
        + COALESCE((
            SELECT COUNT(*) * 5
            FROM usage_events e
            WHERE e.customer_id = c.customer_id
              AND e.payment_late = TRUE
              AND e.event_month >= CURRENT_DATE - INTERVAL '6 months'
          ), 0)                                           AS risk_score

    FROM customers c
    WHERE c.churn = FALSE
)
SELECT
    customer_id,
    contract_type,
    tenure_months,
    monthly_charges,
    ROUND(monthly_charges * 12, 0)                        AS annual_value,
    risk_score,
    CASE
        WHEN risk_score >= 70 THEN 'High'
        WHEN risk_score >= 40 THEN 'Medium'
        ELSE 'Low'
    END                                                   AS risk_tier
FROM risk_scores
ORDER BY risk_score DESC, annual_value DESC;
