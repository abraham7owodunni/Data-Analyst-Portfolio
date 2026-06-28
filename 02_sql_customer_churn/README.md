# Project 2 — Customer Churn Analysis (SQL)

**Tool:** PostgreSQL · **Domain:** Telecom · **Dataset:** Synthetic telco subscriber data (200K customers)

## Business Problem

A telecommunications provider is losing 8–12% of subscribers per quarter. The analytics team needs to:
1. Quantify churn rate by segment, tenure band, and product type
2. Identify the strongest drivers of churn across customer features
3. Build a cohort retention table to track long-term trends
4. Produce a scored at-risk customer list for targeted retention

## Project Structure

```
02_sql_customer_churn/
├── 01_create_tables.sql       # Schema: table definitions + indexes
├── 03_churn_overview.sql      # Overall churn rates, trends, revenue impact
├── 04_cohort_analysis.sql     # Monthly cohort retention curves
├── 05_churn_drivers.sql       # Feature-level churn comparison (feature importance)
├── 06_at_risk_customers.sql   # Scored at-risk customer list for outreach
└── README.md
```

## Key SQL Techniques Used

- **Window functions** — `RANK()`, running totals via `SUM() OVER`
- **CTEs** — multi-step analytical pipelines for cohort and risk analysis
- **Cohort analysis** — `DATE_TRUNC` + `AGE()` to build month-by-month retention
- **Conditional aggregation** — SQL-native feature-importance proxy with churn lift
- **Correlated subqueries** — per-customer risk scoring from related tables

## How to Run

```bash
# 1. Create a PostgreSQL database
createdb telco_churn

# 2. Create the schema (tables + indexes)
psql -d telco_churn -f 01_create_tables.sql

# 3. Run the analyses in order
psql -d telco_churn -f 03_churn_overview.sql
psql -d telco_churn -f 04_cohort_analysis.sql
psql -d telco_churn -f 05_churn_drivers.sql
psql -d telco_churn -f 06_at_risk_customers.sql
```

## What Each Script Does

| Script | Purpose |
|--------|---------|
| `01_create_tables.sql` | Defines `customers`, `usage_events`, and `support_tickets` tables with constraints and indexes |
| `03_churn_overview.sql` | Overall churn rate, churn by contract type, churn by tenure band, monthly churn trend with cumulative revenue lost |
| `04_cohort_analysis.sql` | Builds a monthly cohort retention table showing how each joining cohort retains over time |
| `05_churn_drivers.sql` | Compares churn rate across contract, internet service, payment method, and tech support; ranks the highest-risk segments by churn lift |
| `06_at_risk_customers.sql` | Scores each active customer on churn risk using contract, tenure, service mix, support tickets, and late payments |

## Key Findings

| Finding | Detail |
|---------|--------|
| Overall churn rate | ~9.4% per quarter |
| Highest churn segment | Early-tenure customers on month-to-month contracts |
| Strongest churn driver | Fibre optic customers without tech support |
| Use of at-risk list | Prioritises retention outreach by risk score × account value |

> **Note:** This project uses a synthetic dataset for demonstration. Figures are illustrative of the analytical approach rather than real-world results.
