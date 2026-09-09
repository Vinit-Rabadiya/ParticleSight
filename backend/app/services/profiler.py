import pandas as pd
import numpy as np
from scipy import stats

# This file looks at each numeric column in the dataset and computes
# basic statistics about it — things like the average, how spread out
# the values are, and the shape of the distribution.
# The results are used later by the AI to generate plain-English insights.

def _robust_histogram(series, bins=50):
    """
    Equal-width binning across the raw min–max range breaks down when a
    handful of extreme outliers (common in physics data, e.g. pt, MET)
    stretch the axis so far that almost every event lands in bin 1.

    Instead, compute bin edges from the 1st–99th percentile range, then
    let np.histogram's outer bins absorb anything outside that range.
    This keeps every event counted while making the chart legible.
    """
    lo, hi = np.percentile(series, [1, 99])

    # Degenerate case: 98% of values identical (e.g. a near-constant
    # column) — fall back to the full range so we don't get a zero-width
    # bin range.
    if hi <= lo:
        lo, hi = series.min(), series.max()
        if hi <= lo:
            hi = lo + 1.0

    return np.histogram(series, bins=bins, range=(lo, hi))


def profile_distributions(df):
    NumColumns = df.select_dtypes(include=[np.number]).columns
    results = {}

    # Sample down for profiling — statistics are stable on 5k rows
    df_sample = df if len(df) <= 5000 else df.sample(n=5000, random_state=42)

    for col in NumColumns:
        series = df_sample[col].dropna()

        if len(series) < 10:
            continue

        mean = float(round(series.mean(), 4))
        std = float(round(series.std(), 4))
        median = float(round(series.median(), 4))
        min_val = float(round(series.min(), 4))
        max_val = float(round(series.max(), 4))
        missing_values = int(df[col].isnull().sum())
        skewness = float(round(stats.skew(series), 4))
        kurtosis = float(round(stats.kurtosis(series), 4))

        counts, bin_edges = _robust_histogram(series, bins=50)
        counts = counts.tolist()
        bin_edges = [float(round(edge, 4)) for edge in bin_edges.tolist()]
        is_unusual = abs(skewness) > 2.0

        results[col] = {
            "mean": mean,
            "std_dev": std,
            "median": median,
            "min": min_val,
            "max": max_val,
            "missing_values": missing_values,
            "skewness": skewness,
            "kurtosis": kurtosis,
            "histogram": {"counts": counts, "bin_edges": bin_edges},
            "is_unusual": is_unusual
        }

    return results