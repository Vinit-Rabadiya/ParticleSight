import pandas as pd
import numpy as np
from scipy import stats

def profile_distributions(df):
    NumColumns = df.select_dtypes(include=[np.number]).columns

    results = {}
    for col in NumColumns:
        series = df[col].dropna()
        if len(series) < 10:
            continue  # Skip columns with too few data points
        mean = float(round(series.mean(), 4))
        std = float(round(series.std(), 4))
        median = float(round(series.median(), 4))
        min_val = float(round(series.min(), 4))
        max_val = float(round(series.max(), 4))

        missing_values = int(df[col].isnull().sum())

        skewness = float(round(stats.skew(series), 4))
        kurtosis = float(round(stats.kurtosis(series), 4))

        counts, bin_edges = np.histogram(series, bins=50)
        counts = counts.tolist()
        bin_edges = [float(round(edge, 4)) for edge in bin_edges.tolist()]

        is_unusual = True if abs(skewness) > 2.0 else False

        results[col] ={
            "mean": mean,
            "std_dev": std,
            "median": median,
            "min": min_val,
            "max": max_val,
            "missing_values": missing_values,
            "skewness": skewness,
            "kurtosis": kurtosis,
            "histogram": {
                "counts": counts,
                "bin_edges": bin_edges
            },
            "is_unusual": is_unusual
        }
    return results