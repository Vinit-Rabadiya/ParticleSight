import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.services.cern_client import CERNClient
from app.services.profiler import profile_distributions
from app.services.correlation import find_top_correlations
from app.services.anomaly import detect_anomalies
from app.services.llm import generate_insights

# Thread pool for running CPU-bound tasks in parallel
_executor = ThreadPoolExecutor(max_workers=3)

async def run_full_analysis(csv_url: str, dataset_name: str) -> dict:
    loop = asyncio.get_event_loop()

    # Step 1 — Download CSV (network-bound, must be first)
    print("Downloading dataset...")
    df = await loop.run_in_executor(_executor, CERNClient.get_data, csv_url)

    if df is None:
        raise ValueError(f"Could not load data from {csv_url}")

    # Step 2 — Clean column names
    df.columns = df.columns.str.strip()

    # Step 3 — Run all three analysis services IN PARALLEL
    # They are independent of each other so we run them concurrently
    print("Running profiling, correlation, and anomaly detection in parallel...")
    distributions, top_correlations, anomaly_summary = await asyncio.gather(
        loop.run_in_executor(_executor, profile_distributions, df),
        loop.run_in_executor(_executor, find_top_correlations, df),
        loop.run_in_executor(_executor, detect_anomalies, df),
    )

    # Step 4 — Build AI payload (strip anomaly_scores — too large for LLM)
    anomaly_summary_for_ai = {k: v for k, v in anomaly_summary.items() if k != "anomaly_scores"}
    analysis_data = {
        "distributions": distributions,
        "top_correlations": top_correlations,
        "anomaly_summary": anomaly_summary_for_ai,
    }

    # Step 5 — Generate AI insights
    print("Generating AI insights...")
    ai_insights = await loop.run_in_executor(
        _executor, generate_insights, analysis_data, dataset_name
    )

    print("Analysis complete.")
    return {
        "distributions": distributions,
        "top_correlations": top_correlations,
        "anomaly_summary": anomaly_summary,
        "ai_insights": ai_insights,
    }
