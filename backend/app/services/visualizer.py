import pandas as pd
import numpy as np

class VisualizerService:
    @staticmethod
    def get_mass_distribution(df: pd.DataFrame, bins: int = 50):

        df.columns = df.columns.str.strip()
        masses = df['M'].dropna().values
        counts, bin_edges = np.histogram(masses, bins=bins)

        chart_data = []
        for i in range(len(counts)):
            chart_data.append({
                "range": f"{round(bin_edges[i], 2)} - {round(bin_edges[i+1], 2)}",
                "count": int(counts[i])
            })
        return chart_data