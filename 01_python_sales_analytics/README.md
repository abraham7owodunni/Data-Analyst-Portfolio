# Project 1 — E-Commerce Sales Analytics & Forecasting (Python)

**Tool:** Python · **Domain:** Retail / E-commerce · **Dataset:** Synthetic UK e-commerce transactions (500K rows, generated locally)

## Business Problem

A mid-size UK online retailer wants to understand:
1. Which customer segments drive the most revenue — and which are at risk of churning?
2. What will revenue look like over the next 90 days?
3. How do seasonal patterns affect different product categories?

## Project Structure

```
01_python_sales_analytics/
├── data/
│   └── generate_data.py     # Synthetic dataset generator (creates 500K transactions)
├── src/
│   ├── rfm.py               # RFM scoring + K-Means customer segmentation
│   └── forecasting.py       # Prophet 90-day revenue forecasting
├── requirements.txt
└── README.md
```

> **Note:** The dataset is generated locally by running `data/generate_data.py` rather than
> committed to the repo, to keep it lightweight. Run that script first to produce the CSV files.

## What Each Script Does

| Script | Purpose |
|--------|---------|
| `data/generate_data.py` | Generates 500K synthetic transactions with realistic seasonality (Christmas spikes, summer dips), a heavy-tail customer distribution, returns, and UK regional patterns |
| `src/rfm.py` | Computes Recency / Frequency / Monetary scores per customer, then applies K-Means clustering to produce five interpretable segments (Champions, Loyal, At-Risk, Lost, New) with a summary table and distribution plots |
| `src/forecasting.py` | Trains a Facebook Prophet model with weekly/annual seasonality and UK bank-holiday effects, produces a 90-day revenue forecast with confidence intervals, and cross-validates accuracy |

## Key Techniques

- **RFM segmentation** — quantile-based scoring of customer value
- **K-Means clustering** — unsupervised segmentation on standardised RFM features, validated with silhouette score
- **Time-series forecasting** — Facebook Prophet with multiplicative seasonality, holiday effects, and log-transformed targets
- **Cross-validation** — expanding-window CV for forecast accuracy (MAPE)
- **Data engineering** — synthetic data generation with realistic statistical properties

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate the dataset (creates data/transactions.csv)
python data/generate_data.py

# 3. Run customer segmentation
python src/rfm.py

# 4. Run revenue forecasting
python src/forecasting.py
```

## Libraries Used

```
pandas · numpy · scikit-learn · prophet · matplotlib · seaborn
```

## What This Project Demonstrates

- Translating business questions into an analytical pipeline
- Customer segmentation using both rule-based (RFM) and ML (K-Means) methods
- Production-style code organised into reusable, documented modules
- Time-series forecasting with proper validation
- Clear communication of methodology and results

> **Note:** This project uses a synthetic dataset for demonstration. The analytical
> approach mirrors real-world e-commerce analytics work.
