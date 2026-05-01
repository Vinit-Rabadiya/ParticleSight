import pandas as pd
import numpy as np
from scipy import stats

# This file looks at each numeric column in the dataset and computes
# basic statistics about it — things like the average, how spread out
# the values are, and the shape of the distribution.
# The results are used later by the AI to generate plain-English insights.

def profile_distributions(df):
    #fet only the numeric columns, we can't compute stats on text like "PP" or "MM"
    NumColumns = df.select_dtypes(include=[np.number]).columns

    #this dict will hold the stats for every column keys arecolumn name and values are dict of stats
    results = {}

    for col in NumColumns:
        series = df[col].dropna()

        # Skip this column if it has too few data points — stats won't be meaningful
        if len(series) < 10:
            continue

        mean = float(round(series.mean(), 4))
        std = float(round(series.std(), 4))          # how spread out the values are
        median = float(round(series.median(), 4))    # middle value (less affected by outliers than mean)
        min_val = float(round(series.min(), 4))
        max_val = float(round(series.max(), 4))

        #Count how many values were missing in the original column (before dropna)
        missing_values = int(df[col].isnull().sum())

        #skewness is the distribution lopsided? 0 is perfectly symmetric, >2 or <-2 is very lopsided
        skewness = float(round(stats.skew(series), 4))

        #Kurtosis is how heavy are the tails? Are there lots of extreme values?
        kurtosis = float(round(stats.kurtosis(series), 4))

        #build histogram data — splits values into 50 buckets and counts how many fall in each counts is the how many values in each bucket,50 numbers, while bin_edges is the boundaries of each bucket (51 numbers — one more than counts)
        counts, bin_edges = np.histogram(series, bins=50)
        counts = counts.tolist()
        bin_edges = [float(round(edge, 4)) for edge in bin_edges.tolist()]

        # flag this column as unusual if it is very skewed, the AI will highlight these columns to the user
        is_unusual = True if abs(skewness) > 2.0 else False

        # Store everything for this column
        results[col] = {
            "mean": mean,
            "std_dev": std,
            "median": median,
            "min": min_val,
            "max": max_val,
            "missing_values": missing_values,
            "skewness": skewness,
            "kurtosis": kurtosis,
            "histogram": {
                "counts": counts,       #used by the frontend to draw bar charts
                "bin_edges": bin_edges  #the x-axis values for each bar
            },
            "is_unusual": is_unusual
        }

    return results
