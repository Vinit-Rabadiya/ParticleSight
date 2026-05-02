import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

#Configuration
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def generate_insights(analysis_data: dict, dataset_name: str):
    """
    Sends CERN analysis results to Gemini and returns 5 plain-English insights.
    """
    #creating model instance with JSON response configuration
    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        generation_config={"response_mime_type": "application/json"}
    )

    #extracting data for the prompt
    correlations_json = json.dumps(analysis_data.get("correlations", []))
    anomaly_summary = analysis_data.get("anomalies", {"count": 0, "percentage": 0, "top_features": []})
    unusual_columns = analysis_data.get("unusual_columns", [])

    #prompt
    prompt = f"""
    Act as an expert Particle Physics Communicator for the ParticleSight platform.
    Explain these CERN data findings to a non-expert audience in plain English.

    DATASET: {dataset_name}
    TOP CORRELATIONS: {correlations_json}
    ANOMALIES: {anomaly_summary['count']} events ({anomaly_summary['percentage']}%) involving {anomaly_summary['top_features']}
    UNUSUAL DISTRIBUTIONS: {unusual_columns}

    TASK:
    Generate 5 distinct insights. For each insight, provide:
    - title: A short, catchy name.
    - explanation: A jargon-free explanation of the finding.
    - surprise_level: A scale of 1-10.
    - finding_type: (e.g., "Correlation", "Anomaly", or "Distribution")

    OUTPUT FORMAT:
    Return ONLY a JSON array of 5 objects. No extra text or markdown.
    Example: 
    [
      {{"title": "Energy Link", "explanation": "...", "surprise_level": 5, "finding_type": "Correlation"}},
      ...
    ]
    """

    try:
        #call the API
        response = model.generate_content(prompt)
        content = response.text

        #clean and parse
        # Some models wrap JSON in markdown blocks (```json ... ```), though mime_type helps prevent it.
        if content.startswith("```"):
            content = content.strip("`").replace("json", "", 1).strip()

        return json.loads(content)

    except Exception as e:
        #error handling
        print(f"Gemini API Error: {e}")
        return [{
            "title": "AI Insight Unavailable",
            "explanation": "The AI is currently catching its breath. Please try again in a moment.",
            "surprise_level": 0,
            "finding_type": "Error"
        }]
