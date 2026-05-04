import os
import json
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

# Load the Cerebras API key from .env
load_dotenv()

# Create the Cerebras client
# Uses llama3.1-8b — fast, free, good enough for plain-English insight generation
client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))

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

    try:
        response = client.chat.completions.create(
            model="llama3.1-8b",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
        )

        content = response.choices[0].message.content.strip()

        # Strip markdown code fences if the model adds them
        if content.startswith("```"):
            lines = content.split("\n")
            # Remove first line (```json or ```) and last line (```)
            content = "\n".join(lines[1:-1]).strip()

        return json.loads(content)

    except json.JSONDecodeError as e:
        print(f"Cerebras JSON parse error: {e}")
        print(f"Raw response: {content}")
        return [{
            "title": "AI Insights Unavailable",
            "explanation": "The AI returned an unexpected format. The statistical results above are still valid.",
            "surprise_level": 0,
            "finding_type": "error"
        }]
    except Exception as e:
        print(f"Cerebras API Error: {e}")
        return [{
            "title": "AI Insights Unavailable",
            "explanation": "The AI could not generate insights at this time. The statistical results above are still valid.",
            "surprise_level": 0,
            "finding_type": "error"
        }]
