"""
generate_data.py
Generates a synthetic e-commerce transactions dataset for analysis.
Run: python data/generate_data.py
Outputs: data/transactions.csv (~500K rows)
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

N_CUSTOMERS = 8_000
N_TRANSACTIONS = 500_000
START_DATE = datetime(2021, 1, 1)
END_DATE   = datetime(2023, 12, 31)

CATEGORIES = {
    "Electronics":   {"weight": 0.20, "avg_price": 185, "std": 120},
    "Clothing":      {"weight": 0.25, "avg_price": 45,  "std": 30},
    "Home & Garden": {"weight": 0.15, "avg_price": 70,  "std": 50},
    "Sports":        {"weight": 0.12, "avg_price": 60,  "std": 40},
    "Beauty":        {"weight": 0.10, "avg_price": 25,  "std": 15},
    "Books":         {"weight": 0.08, "avg_price": 12,  "std": 8},
    "Toys":          {"weight": 0.10, "avg_price": 35,  "std": 20},
}

UK_REGIONS = ["London", "South East", "North West", "Yorkshire",
              "West Midlands", "South West", "East", "Scotland",
              "Wales", "North East"]

REGION_WEIGHTS = [0.22, 0.15, 0.13, 0.10, 0.10, 0.08, 0.08, 0.07, 0.04, 0.03]


def seasonal_multiplier(date: datetime) -> float:
    """Christmas spike + summer dip."""
    doy = date.timetuple().tm_yday
    base  = 1.0
    xmas  = np.exp(-((doy - 355) ** 2) / (2 * 15 ** 2)) * 1.8
    summer = np.exp(-((doy - 196) ** 2) / (2 * 25 ** 2)) * 0.3
    return base + xmas - summer


def generate_customers(n: int) -> pd.DataFrame:
    regions = np.random.choice(UK_REGIONS, size=n, p=REGION_WEIGHTS)
    join_dates = [START_DATE + timedelta(days=int(d))
                  for d in np.random.uniform(0, (END_DATE - START_DATE).days, n)]
    return pd.DataFrame({
        "customer_id": [f"C{i:05d}" for i in range(1, n + 1)],
        "region": regions,
        "join_date": join_dates,
        "age_band": np.random.choice(["18-24","25-34","35-44","45-54","55+"],
                                     size=n, p=[0.12, 0.28, 0.25, 0.20, 0.15]),
    })


def generate_transactions(customers: pd.DataFrame, n: int) -> pd.DataFrame:
    cat_names    = list(CATEGORIES.keys())
    cat_weights  = [v["weight"] for v in CATEGORIES.values()]

    # Sample customers with heavy-tail distribution (20% of customers → 80% of txns)
    cust_weights = np.random.pareto(2, len(customers)) + 1
    cust_weights /= cust_weights.sum()

    chosen_customers = customers.sample(n=n, replace=True, weights=cust_weights)
    categories = np.random.choice(cat_names, size=n, p=cat_weights)

    # Dates: random within customer lifetime, with seasonal weighting
    total_days = (END_DATE - START_DATE).days
    raw_days   = np.random.randint(0, total_days, size=n)
    dates      = [START_DATE + timedelta(days=int(d)) for d in raw_days]

    prices = []
    for cat in categories:
        avg = CATEGORIES[cat]["avg_price"]
        std = CATEGORIES[cat]["std"]
        price = max(1.0, np.random.normal(avg, std))
        prices.append(round(price, 2))

    quantities  = np.random.choice([1, 2, 3, 4, 5], size=n, p=[0.60, 0.20, 0.10, 0.06, 0.04])
    is_returned = np.random.choice([0, 1], size=n, p=[0.93, 0.07])

    df = pd.DataFrame({
        "transaction_id": [f"T{i:07d}" for i in range(1, n + 1)],
        "customer_id": chosen_customers["customer_id"].values,
        "region": chosen_customers["region"].values,
        "date": dates,
        "category": categories,
        "unit_price": prices,
        "quantity": quantities,
        "is_returned": is_returned,
    })

    df["revenue"] = (df["unit_price"] * df["quantity"] *
                     (1 - df["is_returned"])).round(2)

    # Apply seasonal multiplier noise
    df["seasonal_factor"] = df["date"].apply(seasonal_multiplier)
    noise = np.random.uniform(0.8, 1.2, size=n)
    df["revenue"] = (df["revenue"] * df["seasonal_factor"] * noise).round(2)
    df.drop(columns=["seasonal_factor"], inplace=True)

    return df.sort_values("date").reset_index(drop=True)


if __name__ == "__main__":
    print("Generating customers...")
    customers = generate_customers(N_CUSTOMERS)
    customers.to_csv("data/customers.csv", index=False)
    print(f"  ✓ {len(customers):,} customers saved to data/customers.csv")

    print("Generating transactions...")
    transactions = generate_transactions(customers, N_TRANSACTIONS)
    transactions.to_csv("data/transactions.csv", index=False)
    print(f"  ✓ {len(transactions):,} transactions saved to data/transactions.csv")

    # Save 1K row sample for repo preview
    sample = transactions.sample(1000, random_state=SEED).sort_values("date")
    sample.to_csv("data/sample_data.csv", index=False)
    print("  ✓ 1,000-row sample saved to data/sample_data.csv")
    print("\nDone.")
