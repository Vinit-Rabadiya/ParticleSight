from app.services.cern_client import CERNClient
from app.services.profiler import profile_distributions
from app.services.correlation import find_top_correlations
from app.services.anomaly import detect_anomalies
from app.services.llm import generate_insights

# This is the master pipeline — it calls all four services in order
# and combines their results into one dict.
# It is called by the analysis router when a user triggers an analysis.

async def run_full_analysis(csv_url: str, dataset_name: str) -> dict:
    # Step 1 — Download the CSV from CERN (or load from local cache)
    # get_data() is a regular function, not async, so no await needed
    df = CERNClient.get_data(csv_url)

    if df is None:
        raise ValueError(f"Could not load data from {csv_url}")

    # Step 2 — Clean column names (fixes trailing spaces like "px1 ")
    df.columns = df.columns.str.strip()

    # Step 3 — Run all three analysis services on the DataFrame
    print("Profiling distributions...")
    distributions = profile_distributions(df)

    print("Finding correlations...")
    top_correlations = find_top_correlations(df)

    print("Detecting anomalies...")
    anomaly_summary = detect_anomalies(df)

    # Step 4 — Combine results into one dict to send to Gemini
    # Strip anomaly_scores from the Gemini payload — it's 100k numbers
    # and would exceed the token limit. The frontend gets it from the full result.
    anomaly_summary_for_ai = {k: v for k, v in anomaly_summary.items() if k != "anomaly_scores"}

    analysis_data = {
        "distributions": distributions,
        "top_correlations": top_correlations,
        "anomaly_summary": anomaly_summary_for_ai
    }

    # Step 5 — Generate plain-English insights using Gemini API
    print("Generating AI insights...")
    ai_insights = generate_insights(analysis_data, dataset_name)

    # Step 6 — Return everything combined
    return {
        "distributions": distributions,
        "top_correlations": top_correlations,
        "anomaly_summary": anomaly_summary,
        "ai_insights": ai_insights
    }
