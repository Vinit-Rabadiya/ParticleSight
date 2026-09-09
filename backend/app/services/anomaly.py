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
    features.sort(key=lambda x: x["difference"], reverse=True)
    return features[:5]


def _explain_point(row, col_means, col_stds, top_n=3):
    """
    For a single data point (row), return the top_n columns that deviate
    most from the normal mean in units of standard deviations.
    This explains WHY the point was flagged as anomalous.
    """
    deviations = []
    for col in row.index:
        mean = col_means.get(col, 0)
        std = col_stds.get(col, 1)
        if std == 0:
            continue
        z = abs((row[col] - mean) / std)
        direction = "high" if row[col] > mean else "low"
        deviations.append({
            "feature": col,
            "value": round(float(row[col]), 4),
            "normal_mean": round(float(mean), 4),
            "z_score": round(float(z), 2),
            "direction": direction,
        })
    deviations.sort(key=lambda x: x["z_score"], reverse=True)
    return deviations[:top_n]


def detect_anomalies(df):
    num_cols = df.select_dtypes(include=[np.number]).dropna()

    if num_cols.empty:
        return []

    # Sample down to 5,000 rows max for speed on free-tier servers
    if len(num_cols) > 5000:
        num_cols = num_cols.sample(n=5000, random_state=42)

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(num_cols)

    model = IsolationForest(n_estimators=50, contamination=0.03, random_state=42)
    model.fit(scaled_data)

    predictions = model.predict(scaled_data)
    anomaly_scores = model.decision_function(scaled_data)
    anomaly_indices = np.where(predictions == -1)[0]

    # Compute normal means/stds for per-point explanations
    normal_indices = np.where(predictions == 1)[0]
    normal_rows = num_cols.iloc[normal_indices]
    col_means = normal_rows.mean().to_dict()
    col_stds = normal_rows.std().to_dict()

    # Build per-point explanations for the top 50 most anomalous points
    # sorted by most negative score (most anomalous first)
    sorted_anomaly_idx = sorted(
        anomaly_indices.tolist(),
        key=lambda i: anomaly_scores[i]
    )[:50]

    point_explanations = {}
    for i in sorted_anomaly_idx:
        row = num_cols.iloc[i]
        point_explanations[i] = _explain_point(row, col_means, col_stds)

    result = {
        "anomaly_indices": anomaly_indices[:50].tolist(),
        "anomaly_scores": anomaly_scores.tolist(),
        "total_events": len(num_cols),
        "total_anomalies": len(anomaly_indices),
        "anomaly_percentage": round((len(anomaly_indices) / len(num_cols)) * 100, 2),
        "most_anomalous_features": _find_anomaly_features(num_cols, anomaly_indices),
        "point_explanations": point_explanations,
    }
    return result
