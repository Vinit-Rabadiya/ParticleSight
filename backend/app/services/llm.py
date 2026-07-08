import os
import json
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

load_dotenv()

# Create the Cerebras client
# Uses llama3.1-8b — fast, free, good enough for plain-English insight generation
API_KEY = os.getenv("CEREBRAS_API_KEY")
client = Cerebras(api_key=API_KEY) if API_KEY else None
PREFERRED_MODEL = os.getenv("CEREBRAS_MODEL", "llama3.1-8b")
MODEL_CANDIDATES = [
    PREFERRED_MODEL,
    "llama-3.3-70b",
    "llama3.1-70b",
    "llama3.1-8b",
]


def _local_fallback_insights(analysis_data: dict, dataset_name: str, reason: str) -> list:
    """Generate useful deterministic insights when remote AI is unavailable."""
    insights = []

    top_correlations = analysis_data.get("top_correlations", [])
    anomaly_summary = analysis_data.get("anomaly_summary", {})
    distributions = analysis_data.get("distributions", {})

    insights.append(
        {
            "title": "Dataset At A Glance",
            "explanation": (
                f"{dataset_name} contains {anomaly_summary.get('total_events', 0)} events with "
                f"{len(distributions)} numeric features profiled for patterns, anomalies, and correlations."
            ),
            "surprise_level": 2,
            "finding_type": "pattern",
        }
    )

    if top_correlations:
        strongest = top_correlations[0]
        corr_value = strongest.get("correlation", 0)
        direction = strongest.get("direction", "unknown")
        insights.append(
            {
                "title": "Strongest Relationship Found",
                "explanation": (
                    f"In {dataset_name}, the strongest relationship is between "
                    f"{strongest.get('variable_1', 'N/A')} and {strongest.get('variable_2', 'N/A')} "
                    f"with correlation {corr_value:.2f} ({direction})."
                ),
                "surprise_level": 6 if abs(corr_value) >= 0.8 else 4,
                "finding_type": "correlation",
            }
        )

    total_events = anomaly_summary.get("total_events", 0)
    anomaly_pct = anomaly_summary.get("anomaly_percentage", 0)
    if total_events:
        insights.append(
            {
                "title": "Anomaly Rate Overview",
                "explanation": (
                    f"The anomaly detector flagged {anomaly_summary.get('total_anomalies', 0)} out of "
                    f"{total_events} events ({anomaly_pct}%)."
                ),
                "surprise_level": 7 if anomaly_pct >= 5 else 3,
                "finding_type": "anomaly",
            }
        )

    unusual_columns = [col for col, stats in distributions.items() if stats.get("is_unusual")]
    if unusual_columns:
        sample = ", ".join(unusual_columns[:3])
        insights.append(
            {
                "title": "Skewed Distributions Detected",
                "explanation": (
                    f"The data shows unusually skewed distributions in {len(unusual_columns)} columns"
                    f" (for example: {sample})."
                ),
                "surprise_level": 5,
                "finding_type": "distribution",
            }
        )

    top_features = anomaly_summary.get("most_anomalous_features", [])
    if top_features:
        first = top_features[0]
        insights.append(
            {
                "title": "Top Driver Behind Anomalies",
                "explanation": (
                    f"The feature {first.get('feature', 'N/A')} shows the largest mean shift between "
                    f"normal and anomalous events (difference {first.get('difference', 'N/A')})."
                ),
                "surprise_level": 6,
                "finding_type": "pattern",
            }
        )

    return insights[:5]

def generate_insights(analysis_data: dict, dataset_name: str) -> list:
    """
    Sends CERN analysis results to Cerebras (Llama 3.1) and returns
    5 plain-English insights as a list of dicts.
    analysis_data must have keys: distributions, top_correlations, anomaly_summary
    """
    # Pull out the parts we need for the prompt
    top_correlations = json.dumps(analysis_data.get("top_correlations", []), indent=2)
    anomaly_summary = analysis_data.get("anomaly_summary", {})
    distributions = analysis_data.get("distributions", {})

    # Find which columns were flagged as unusual (skewness > 2.0)
    unusual_columns = [col for col, stats in distributions.items() if stats.get("is_unusual")]

    # Build the prompt
    prompt = f"""You are explaining particle physics data findings to a non-expert audience for the ParticleSight platform.

Dataset: {dataset_name}

Here are the automated statistical findings:

TOP CORRELATIONS:
{top_correlations}

ANOMALY DETECTION:
- Total events: {anomaly_summary.get("total_events", 0)}
- Anomalies found: {anomaly_summary.get("total_anomalies", 0)} ({anomaly_summary.get("anomaly_percentage", 0)}%)
- Features most different in anomalies: {anomaly_summary.get("most_anomalous_features", [])}

UNUSUAL DISTRIBUTIONS (highly skewed columns):
{unusual_columns}

Generate exactly 5 insights from this data. Each insight must:
1. Be written in plain English — no physics jargon
2. Explain what was found and why it is interesting
3. Be specific — mention actual variable names and numbers
4. Have a surprise_level from 1 (expected) to 10 (very surprising)

Return ONLY a valid JSON array. No extra text, no markdown, no code fences.
[
  {{
    "title": "Short title here",
    "explanation": "Full plain-English explanation here",
    "surprise_level": 7,
    "finding_type": "correlation"
  }}
]

finding_type must be one of: correlation, anomaly, distribution, pattern"""

    if client is None:
        print("Cerebras API key not set; using local fallback insights.")
        return _local_fallback_insights(analysis_data, dataset_name, "missing CEREBRAS_API_KEY")

    last_error = None
    for model_name in MODEL_CANDIDATES:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )

            content = response.choices[0].message.content.strip()

            # Strip markdown code fences if the model adds them
            if content.startswith("```"):
                lines = content.split("\n")
                # Remove first line (```json or ```) and last line (```)
                content = "\n".join(lines[1:-1]).strip()

            try:
                return json.loads(content)
            except json.JSONDecodeError as parse_error:
                last_error = parse_error
                continue
        except Exception as exc:
            last_error = exc
            continue

    print(f"Cerebras API Error: {last_error}")
    return _local_fallback_insights(
        analysis_data,
        dataset_name,
        f"AI API request failed: {last_error}",
    )
