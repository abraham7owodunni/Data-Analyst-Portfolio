-- =============================================================
-- 01_create_tables.sql
-- Telco Customer Churn Analysis — Schema Definition
-- PostgreSQL 15+
-- =============================================================

DROP SCHEMA IF EXISTS churn CASCADE;
CREATE SCHEMA churn;
SET search_path = churn;

-- ------------------------------------------------------------
-- Customers
-- ------------------------------------------------------------
CREATE TABLE customers (
    customer_id         SERIAL PRIMARY KEY,
    gender              VARCHAR(10)  NOT NULL CHECK (gender IN ('Male','Female','Other')),
    senior_citizen      BOOLEAN      NOT NULL DEFAULT FALSE,
    partner             BOOLEAN      NOT NULL DEFAULT FALSE,
    dependents          BOOLEAN      NOT NULL DEFAULT FALSE,
    tenure_months       INT          NOT NULL CHECK (tenure_months >= 0),
    phone_service       BOOLEAN      NOT NULL DEFAULT TRUE,
    multiple_lines      VARCHAR(30),
    internet_service    VARCHAR(20)  CHECK (internet_service IN ('DSL','Fiber optic','None')),
    online_security     VARCHAR(30),
    online_backup       VARCHAR(30),
    device_protection   VARCHAR(30),
    tech_support        VARCHAR(30),
    streaming_tv        VARCHAR(30),
    streaming_movies    VARCHAR(30),
    contract_type       VARCHAR(20)  CHECK (contract_type IN ('Month-to-month','One year','Two year')),
    paperless_billing   BOOLEAN      NOT NULL DEFAULT FALSE,
    payment_method      VARCHAR(40),
    monthly_charges     NUMERIC(8,2) NOT NULL CHECK (monthly_charges >= 0),
    total_charges       NUMERIC(10,2),
    churn               BOOLEAN      NOT NULL DEFAULT FALSE,
    churn_date          DATE,
    join_date           DATE         NOT NULL
);

-- ------------------------------------------------------------
-- Monthly usage events (for pre-churn signal detection)
-- ------------------------------------------------------------
CREATE TABLE usage_events (
    event_id            BIGSERIAL    PRIMARY KEY,
    customer_id         INT          NOT NULL REFERENCES customers(customer_id),
    event_month         DATE         NOT NULL,   -- first day of month
    calls_made          INT          DEFAULT 0,
    data_gb_used        NUMERIC(6,2) DEFAULT 0,
    support_tickets     INT          DEFAULT 0,
    payment_late        BOOLEAN      NOT NULL DEFAULT FALSE,
    plan_change         BOOLEAN      NOT NULL DEFAULT FALSE
);

-- ------------------------------------------------------------
-- Support tickets
-- ------------------------------------------------------------
CREATE TABLE support_tickets (
    ticket_id           BIGSERIAL    PRIMARY KEY,
    customer_id         INT          NOT NULL REFERENCES customers(customer_id),
    opened_date         DATE         NOT NULL,
    closed_date         DATE,
    category            VARCHAR(50),
    resolution          VARCHAR(30)  CHECK (resolution IN ('Resolved','Unresolved','Escalated')),
    satisfaction_score  SMALLINT     CHECK (satisfaction_score BETWEEN 1 AND 5)
);

-- ------------------------------------------------------------
-- Indexes
-- ------------------------------------------------------------
CREATE INDEX idx_customers_churn         ON customers(churn);
CREATE INDEX idx_customers_contract      ON customers(contract_type);
CREATE INDEX idx_customers_tenure        ON customers(tenure_months);
CREATE INDEX idx_usage_customer_month    ON usage_events(customer_id, event_month);
CREATE INDEX idx_tickets_customer        ON support_tickets(customer_id);
CREATE INDEX idx_tickets_opened          ON support_tickets(opened_date);

\echo 'Schema created successfully.'
