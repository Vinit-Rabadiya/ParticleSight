from app.services.cern_client import CERNClient
from app.services.profiler import profile_distributions
from app.services.correlation import find_top_corellations
from app.services.anomaly import detect_anomalies
from app.services.llm import generate_insights

#async func so that if network is slow downloading will also be slow, and FastAPI can handle other requests in the meantime

async def run_full_analysis(csv_url, dataset_name):
    df = await CERNClient.get_data(csv_url)  #to get dataframe
    df.columns = df.columns.str.strip()  # Remove leading/trailing whitespace from column names
    distributions = profile_distributions(df)
    top_corellations = find_top_corellations(df)
    anomaly_summary = detect_anomalies(df)
    analysis_data = {distributions, top_corellations, anomaly_summary}
    ai_insights = generate_insights(analysis_data)
    return {
        "distributions": distributions,
        "top_corellations": top_corellations,
        "anomaly_summary": anomaly_summary,
        "ai_insights": ai_insights
    }