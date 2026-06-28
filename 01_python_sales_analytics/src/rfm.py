"""
rfm.py
RFM (Recency, Frequency, Monetary) scoring and K-Means segmentation pipeline.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns


SEGMENT_LABELS = {
    0: "Champions",
    1: "Loyal Customers",
    2: "At-Risk",
    3: "Lost",
    4: "New Customers",
}

SEGMENT_COLOURS = {
    "Champions":       "#2ecc71",
    "Loyal Customers": "#3498db",
    "At-Risk":         "#e67e22",
    "Lost":            "#e74c3c",
    "New Customers":   "#9b59b6",
}


def compute_rfm(
    df: pd.DataFrame,
    snapshot_date: datetime | None = None,
    customer_col: str = "customer_id",
    date_col:     str = "date",
    revenue_col:  str = "revenue",
) -> pd.DataFrame:
    """
    Compute RFM scores for each customer.

    Parameters
    ----------
    df            : Transaction DataFrame.
    snapshot_date : Reference date for recency. Defaults to max date + 1 day.
    customer_col  : Name of the customer ID column.
    date_col      : Name of the transaction date column.
    revenue_col   : Name of the revenue column.

    Returns
    -------
    DataFrame indexed by customer_id with columns:
      recency (days), frequency (count), monetary (£ total),
      R, F, M scores (1-5), RFM_score (string), rfm_total.
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    if snapshot_date is None:
        snapshot_date = df[date_col].max() + pd.Timedelta(days=1)

    rfm = (
        df.groupby(customer_col)
        .agg(
            recency   = (date_col,    lambda x: (snapshot_date - x.max()).days),
            frequency = (date_col,    "count"),
            monetary  = (revenue_col, "sum"),
        )
        .reset_index()
    )

    # Score 1-5 (5 = best)
    rfm["R"] = pd.qcut(rfm["recency"],   5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"), 5,
                        labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M"] = pd.qcut(rfm["monetary"],  5, labels=[1, 2, 3, 4, 5]).astype(int)

    rfm["RFM_score"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)
    rfm["rfm_total"] = rfm["R"] + rfm["F"] + rfm["M"]

    return rfm


def kmeans_segment(
    rfm: pd.DataFrame,
    n_clusters: int = 5,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Apply K-Means clustering on normalised RFM values.
    Adds 'cluster' and 'segment' columns to the rfm DataFrame.
    """
    features = rfm[["recency", "frequency", "monetary"]].copy()
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    rfm = rfm.copy()
    rfm["cluster"] = km.fit_predict(X_scaled)

    sil = silhouette_score(X_scaled, rfm["cluster"])
    print(f"Silhouette score (k={n_clusters}): {sil:.3f}")

    # Map clusters to interpretable labels by sorting on rfm_total centroid mean
    cluster_means = rfm.groupby("cluster")["rfm_total"].mean().sort_values(ascending=False)
    label_map     = {old: new for new, old in enumerate(cluster_means.index)}
    rfm["cluster"] = rfm["cluster"].map(label_map)
    rfm["segment"] = rfm["cluster"].map(SEGMENT_LABELS)

    return rfm


def plot_rfm_distribution(rfm: pd.DataFrame, save_path: str = "outputs/rfm_segments.png"):
    """3-panel RFM distribution by segment."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("RFM Distribution by Customer Segment", fontsize=14, fontweight="bold")

    for ax, metric, label in zip(
        axes,
        ["recency", "frequency", "monetary"],
        ["Recency (days)", "Frequency (orders)", "Monetary (£)"],
    ):
        for seg, grp in rfm.groupby("segment"):
            colour = SEGMENT_COLOURS.get(seg, "#888")
            ax.hist(grp[metric], bins=30, alpha=0.6, label=seg, color=colour)
        ax.set_xlabel(label)
        ax.set_ylabel("Customers")
        ax.set_title(label)

    handles = [mpatches.Patch(color=c, label=s) for s, c in SEGMENT_COLOURS.items()]
    fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=9, frameon=False)
    plt.tight_layout(rect=[0, 0.08, 1, 1])
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"Saved → {save_path}")
    return fig


def segment_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    """Revenue and size summary table by segment."""
    summary = (
        rfm.groupby("segment")
        .agg(
            customers      = ("customer_id", "count"),
            avg_recency    = ("recency",   "mean"),
            avg_frequency  = ("frequency", "mean"),
            avg_monetary   = ("monetary",  "mean"),
            total_revenue  = ("monetary",  "sum"),
        )
        .round(2)
        .sort_values("total_revenue", ascending=False)
    )
    summary["revenue_pct"] = (summary["total_revenue"] /
                               summary["total_revenue"].sum() * 100).round(1)
    return summary


if __name__ == "__main__":
    df = pd.read_csv("data/transactions.csv", parse_dates=["date"])
    df = df[df["is_returned"] == 0]

    rfm = compute_rfm(df)
    rfm = kmeans_segment(rfm)

    print("\nSegment Summary:")
    print(segment_summary(rfm).to_string())

    plot_rfm_distribution(rfm)
    rfm.to_csv("outputs/rfm_scored.csv", index=False)
