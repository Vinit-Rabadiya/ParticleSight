from app.services.cern_client import CERNClient
from app.services.profiler import profile_distributions
from app.services.correlation import find_top_correlations

df = CERNClient.get_data()
df.columns = df.columns.str.strip()
profile_results = profile_distributions(df)
print("Columns profiled:", len(profile_results))
print("Unusual columns:", [col for col in profile_results if profile_results[col]["is_unusual"]])
correlation_results = find_top_correlations(df)
print("\nTop correlations found:", len(correlation_results))
for c in correlation_results:
    print(c["variable_1"], "vs", c["variable_2"], "| r =", c["correlation"], "| strength:", c["strength"])


from app.services.anomaly import detect_anomalies

anomaly_results = detect_anomalies(df)
print("\nAnomaly Detection Results:")
print("Total events:", anomaly_results["total_events"])
print("Anomalies found:", anomaly_results["total_anomalies"])
print("Anomaly percentage:", anomaly_results["anomaly_percentage"], "%")
print("Top anomalous features:")
for f in anomaly_results["most_anomalous_features"]:
    print(" ", f["feature"], "| anomaly mean:", f["anomaly_mean"], "| normal mean:", f["normal_mean"])
