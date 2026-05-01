import pandas as pd
import numpy as np
from scipy import stats

#This file finds which pairs of columns are most strongly related to each other.
# For example — when energy E1 goes up, does mass M also go up?
# We use Spearman correlation because physics data is not normally distributed.
# We also run a significance test on each pair to make sure the correlation is real and not just random chance.

def find_top_correlations(df):
    #get only numeric columns and drop any rows with missing values
    #we need complete rows because we're comparing columns against each other
    NumColumns = df.select_dtypes(include=[np.number]).dropna()

    #Build the full Spearman correlation matrix
    #this is a grid where every column is compared to every other column
    #values range from -1 (perfect negative) to 1 (perfect positive)
    corr_matrix = NumColumns.corr(method='spearman')

    # This list will hold one dict per column pair
    correlations = []

    # loop through the upper triangle of the matrix only
    # We do this to avoid duplicates — "E1 vs M" is the same as "M vs E1"
    # the outer loop picks the first column, inner loop picks everything after it
    for i in range(0, len(NumColumns.columns)-1):
        for j in range(i+1, len(NumColumns.columns)):

            # Get the correlation value for this pair from the matrix
            r_value = corr_matrix.iloc[i, j]

            # Skip if the value is NaN, can happen with constant columns
            if pd.isna(r_value) is True:
                continue

            # Run the significance test for this pair of columns,p_value < 0.05 means the correlation is statistically significant,(very unlikely to be random chance)
            p_value = stats.spearmanr(NumColumns.iloc[:, i], NumColumns.iloc[:, j], nan_policy='omit')

            #building a dict describing this correlation pair
            correlation_entry = {
                "variable_1": NumColumns.columns[i],
                "variable_2": NumColumns.columns[j],
                "correlation": float(round(r_value, 4)),
                "p_value": float(round(p_value.pvalue, 4)),
                "is_significant": float(round(p_value.pvalue, 4)) < 0.05,  # True if p < 0.05
                "direction": "positive" if r_value > 0 else "negative",    # do they move together or opposite?
                "strength": "strong" if abs(r_value) > 0.7 else "moderate" if abs(r_value) > 0.4 else "weak"
            }
            correlations.append(correlation_entry)

    #sort by absolute correlation value, strongest pairs first
    correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)

    # Keep only the statistically significant ones
    significant_correlations = [c for c in correlations if c["is_significant"] == True]

    #return only the top 10 strongest significant correlations
    return significant_correlations[:10]
