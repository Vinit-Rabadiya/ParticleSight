import pandas as pd
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    @staticmethod
    def find_outliers(df: pd.DataFrame, contamination: float = 0.01):
        """
        Uses Isolation Forest to find the 1% most 'unusual' events.
        """
        df.columns = df.columns.str.strip()  # Remove any leading/trailing whitespace from column names
        features = ['E1', 'px1', 'py1', 'pz1', 'E2', 'px2', 'py2', 'pz2', 'M']
        
        data_numeric = df[features].apply(pd.to_numeric, errors='coerce').dropna()

        model = IsolationForest(contamination=contamination, random_state=42)

        data_numeric['anomaly_score'] = model.fit_predict(data_numeric)

        return data_numeric[data_numeric['anomaly_score'] == -1]
     