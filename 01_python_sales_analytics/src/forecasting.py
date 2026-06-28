"""
forecasting.py
90-day revenue forecasting using Facebook Prophet with
seasonality, UK bank holidays, and promotional regressors.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
import warnings
warnings.filterwarnings("ignore")


UK_BANK_HOLIDAYS = pd.DataFrame({
    "holiday": [
        "New Year", "Good Friday", "Easter Monday", "Early May Bank Holiday",
        "Spring Bank Holiday", "Summer Bank Holiday", "Christmas Day", "Boxing Day",
        "New Year", "Good Friday", "Easter Monday", "Early May Bank Holiday",
        "Spring Bank Holiday", "Summer Bank Holiday", "Christmas Day", "Boxing Day",
        "New Year", "Good Friday", "Easter Monday", "Early May Bank Holiday",
        "Spring Bank Holiday", "Summer Bank Holiday", "Christmas Day", "Boxing Day",
    ],
    "ds": pd.to_datetime([
        "2021-01-01", "2021-04-02", "2021-04-05", "2021-05-03",
        "2021-05-31", "2021-08-30", "2021-12-27", "2021-12-28",
        "2022-01-03", "2022-04-15", "2022-04-18", "2022-05-02",
        "2022-06-02", "2022-08-29", "2022-12-27", "2022-12-26",
        "2023-01-02", "2023-04-07", "2023-04-10", "2023-05-01",
        "2023-05-29", "2023-08-28", "2023-12-25", "2023-12-26",
    ]),
    "lower_window": 0,
    "upper_window": 1,
})


def prepare_prophet_df(
    df: pd.DataFrame,
    date_col: str = "date",
    revenue_col: str = "revenue",
) -> pd.DataFrame:
    """Aggregate daily revenue and format for Prophet (ds, y)."""
    daily = (
        df.groupby(date_col)[revenue_col]
        .sum()
        .reset_index()
        .rename(columns={date_col: "ds", revenue_col: "y"})
    )
    daily["ds"] = pd.to_datetime(daily["ds"])
    # Apply log transform to stabilise variance
    daily["y"] = np.log1p(daily["y"])
    return daily.sort_values("ds").reset_index(drop=True)


def build_model(add_regressors: bool = False) -> Prophet:
    """Instantiate and return a configured Prophet model."""
    model = Prophet(
        holidays=UK_BANK_HOLIDAYS,
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
        changepoint_prior_scale=0.05,
        holidays_prior_scale=10.0,
        interval_width=0.95,
    )
    model.add_seasonality(name="monthly", period=30.5, fourier_order=5)
    return model


def train_and_forecast(
    daily_df: pd.DataFrame,
    horizon_days: int = 90,
) -> tuple[Prophet, pd.DataFrame]:
    """
    Train Prophet on all available data and return (model, forecast).
    Forecast includes confidence intervals; revenue is back-transformed from log scale.
    """
    model = build_model()
    model.fit(daily_df)

    future = model.make_future_dataframe(periods=horizon_days)
    forecast = model.predict(future)

    # Back-transform from log scale
    for col in ["yhat", "yhat_lower", "yhat_upper"]:
        forecast[col] = np.expm1(forecast[col])

    return model, forecast


def evaluate_model(
    daily_df: pd.DataFrame,
    initial: str = "730 days",
    period:  str = "30 days",
    horizon: str = "30 days",
) -> pd.DataFrame:
    """
    Cross-validate Prophet and return performance metrics.
    Uses expanding window CV.
    """
    model = build_model()
    model.fit(daily_df)

    df_cv     = cross_validation(model, initial=initial, period=period, horizon=horizon)
    df_cv["y_exp"]    = np.expm1(df_cv["y"])
    df_cv["yhat_exp"] = np.expm1(df_cv["yhat"])

    metrics = performance_metrics(df_cv)
    print("\nCross-Validation Metrics (30-day horizon):")
    print(metrics[["horizon", "mse", "rmse", "mae", "mape"]].tail(5).to_string(index=False))
    return metrics


def plot_forecast(
    model: Prophet,
    forecast: pd.DataFrame,
    daily_df: pd.DataFrame,
    save_path: str = "outputs/forecast_90day.png",
):
    """Plot actual vs forecast with confidence interval."""
    fig, ax = plt.subplots(figsize=(14, 5))

    actuals = daily_df.copy()
    actuals["y"] = np.expm1(actuals["y"])

    ax.plot(actuals["ds"], actuals["y"], color="#2c3e50", lw=1.2, label="Actual revenue")
    ax.plot(forecast["ds"], forecast["yhat"], color="#e74c3c", lw=1.5, label="Forecast")
    ax.fill_between(
        forecast["ds"], forecast["yhat_lower"], forecast["yhat_upper"],
        alpha=0.15, color="#e74c3c", label="95% confidence interval",
    )

    # Shade forecast period
    cutoff = actuals["ds"].max()
    ax.axvline(cutoff, color="#888", linestyle="--", lw=0.8)
    ax.text(cutoff, ax.get_ylim()[1] * 0.95, " Forecast →", fontsize=9, color="#888")

    ax.set_title("90-Day Revenue Forecast — UK E-Commerce Retailer", fontsize=13)
    ax.set_xlabel("Date")
    ax.set_ylabel("Daily Revenue (£)")
    ax.legend(frameon=False)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"£{x:,.0f}"))
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"Saved → {save_path}")
    return fig


if __name__ == "__main__":
    import os
    os.makedirs("outputs", exist_ok=True)

    df = pd.read_csv("data/transactions.csv", parse_dates=["date"])
    df = df[df["is_returned"] == 0]

    daily = prepare_prophet_df(df)
    model, forecast = train_and_forecast(daily)

    metrics = evaluate_model(daily)
    plot_forecast(model, forecast, daily)

    forecast.to_csv("outputs/forecast_90day.csv", index=False)
    print("\nForecasting complete.")
