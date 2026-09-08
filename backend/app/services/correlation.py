import pandas as pd
import numpy as np
from scipy import stats

#This file finds which pairs of columns are most strongly related to each other.
# For example — when energy E1 goes up, does mass M also go up?
# We use Spearman correlation because physics data is not normally distributed.
# We also run a significance test on each pair to make sure the correlation is real and not just random chance.

def find_top_correlations(df):
    NumColumns = df.select_dtypes(include=[np.number]).dropna()

    # Sample down to 5,000 rows for speed — correlation is stable on large samples
    if len(NumColumns) > 5000:
        NumColumns = NumColumns.sample(n=5000, random_state=42)

    corr_matrix = NumColumns.corr(method='spearman')

    correlations = []

    for i in range(0, len(NumColumns.columns)-1):
        for j in range(i+1, len(NumColumns.columns)):
            r_value = corr_matrix.iloc[i, j]
            if pd.isna(r_value):
                continue

            p_value = stats.spearmanr(NumColumns.iloc[:, i], NumColumns.iloc[:, j], nan_policy='omit')

            correlation_entry = {
                "variable_1": NumColumns.columns[i],
                "variable_2": NumColumns.columns[j],
                "correlation": float(round(r_value, 4)),
                "p_value": float(round(p_value.pvalue, 4)),
                "is_significant": float(round(p_value.pvalue, 4)) < 0.05,
                "direction": "positive" if r_value > 0 else "negative",
                "strength": "strong" if abs(r_value) > 0.7 else "moderate" if abs(r_value) > 0.4 else "weak"
            }
            correlations.append(correlation_entry)

    correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
    significant_correlations = [c for c in correlations if c["is_significant"] == True]
    return significant_correlations[:10]
