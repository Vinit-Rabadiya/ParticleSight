import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load the Gemini API key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Create the Gemini client using the new google-genai SDK
client = genai.Client(api_key=api_key)

def generate_insights(analysis_data: dict, dataset_name: str) -> list:
    """
    Sends CERN analysis results to Gemini and returns 5 plain-English insights.
    analysis_data must have keys: distributions, top_correlations, anomaly_summary
    """
    # Pull out the parts we need for the prompt
    # These key names must match exactly what analyser.py puts in analysis_data
    top_correlations = json.dumps(analysis_data.get("top_correlations", []), indent=2)
    anomaly_summary = analysis_data.get("anomaly_summary", {})
    distributions = analysis_data.get("distributions", {})

    # Find which columns were flagged as unusual (skewness > 2.0)
    unusual_columns = [col for col, stats in distributions.items() if stats.get("is_unusual")]

    # Build the prompt — tell Gemini exactly what we want back
    prompt = f"""
You are explaining particle physics data findings to a non-expert audience for the ParticleSight platform.

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

Return ONLY a valid JSON array. No extra text, no markdown.
[
  {{
    "title": "Short title here",
    "explanation": "Full plain-English explanation here",
    "surprise_level": 7,
    "finding_type": "correlation"
  }}
]

finding_type must be one of: correlation, anomaly, distribution, pattern
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        content = response.text

        # Strip markdown code fences if Gemini adds them
        if content.startswith("```"):
            content = content.strip("`").replace("json", "", 1).strip()

        return json.loads(content)

    except Exception as e:
        print(f"Gemini API Error: {e}")
        # Return a fallback so the rest of the analysis still works
        return [{
            "title": "AI Insights Unavailable",
            "explanation": "The AI could not generate insights at this time. The statistical results above are still valid.",
            "surprise_level": 0,
            "finding_type": "error"
        }]
