import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def _find_anomaly_features(num_cols, anomaly_indices):
    features = []
    normal_indices = np.setdiff1d(np.arange(len(num_cols)), anomaly_indices)

    for col in num_cols.columns:
        normal_mean = num_cols.iloc[normal_indices][col].mean()
        anomaly_mean = num_cols.iloc[anomaly_indices][col].mean()
        mean_diff = abs(anomaly_mean - normal_mean)
        features.append({
            "feature": col,
            "anomaly_mean": round(float(anomaly_mean), 4),
            "normal_mean": round(float(normal_mean), 4),
            "difference": round(float(mean_diff), 4)
        })
    features.sort(key=lambda x: x["difference"], reverse=True)  # Sort by mean difference  
    return features[:5]  # Return top 5 features with the largest mean difference

def detect_anomalies(df):
    # Get only numeric columns and drop rows with missing values
    num_cols = df.select_dtypes(include=[np.number]).dropna()

    if num_cols.empty:
        return []

    # Sample down to 5,000 rows max for speed on free-tier servers
    if len(num_cols) > 5000:
        num_cols = num_cols.sample(n=5000, random_state=42)

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(num_cols)

    # Reduce n_estimators for speed — 50 is sufficient for pattern detection
    model = IsolationForest(n_estimators=50, contamination=0.03, random_state=42)
    model.fit(scaled_data)

    predictions = model.predict(scaled_data)
    anomaly_scores = model.decision_function(scaled_data)
    anomaly_indices = np.where(predictions == -1)[0]

    dictionary = {
        "anomaly_indices": anomaly_indices[:50].tolist(),
        "anomaly_scores": anomaly_scores.tolist(),
        "total_events": len(num_cols),
        "total_anomalies": len(anomaly_indices),
        "anomaly_percentage": round((len(anomaly_indices) / len(num_cols)) * 100, 2),
    }
    most_anomalous_features = _find_anomaly_features(num_cols, anomaly_indices)
    dictionary["most_anomalous_features"] = most_anomalous_features
    return dictionary
