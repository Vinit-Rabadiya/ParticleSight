import os
import json
import re
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

load_dotenv()

# Create the Cerebras client
# Uses llama3.1-8b — fast, free, good enough for plain-English insight generation
API_KEY = os.getenv("CEREBRAS_API_KEY")
client = Cerebras(api_key=API_KEY) if API_KEY else None
PREFERRED_MODEL = os.getenv("CEREBRAS_MODEL", "gpt-oss-120b")
MODEL_CANDIDATES = [
    PREFERRED_MODEL,
    "gpt-oss-120b",
    "gemma-4-31b",
    "zai-glm-4.7",
]


def _local_fallback_insights(analysis_data: dict, dataset_name: str, reason: str) -> list:
    """Generate useful deterministic insights when remote AI is unavailable."""
    insights = []

    top_correlations = analysis_data.get("top_correlations", [])
    anomaly_summary = analysis_data.get("anomaly_summary", {})
    distributions = analysis_data.get("distributions", {})
    columns = list(distributions.keys())

    preview_columns = ", ".join(columns[:8]) if columns else "no numeric columns detected"

    insights.append(
        {
            "title": "Dataset At A Glance",
            "explanation": (
                f"{dataset_name} contains {anomaly_summary.get('total_events', 0)} events with "
                f"{len(distributions)} numeric features profiled for patterns, anomalies, and correlations. "
                f"Examples of columns: {preview_columns}."
            ),
            "surprise_level": 2,
            "finding_type": "pattern",
        }
    )

    if columns:
        column_meaning_lines = []
        for column_name in columns[:20]:
            ref_url = f"https://opendata.cern.ch/search?q={column_name}"
            column_meaning_lines.append(
                f"- {column_name}: Physics meaning unavailable in local fallback mode. Source: {ref_url}"
            )

        insights.append(
            {
                "title": "Column Meanings",
                "explanation": "\n".join(column_meaning_lines),
                "surprise_level": 1,
                "finding_type": "pattern",
            }
        )

        insights.append(
            {
                "title": "Column Guide",
                "explanation": (
                    "Column names are interpreted from the data itself. "
                    f"Start with these fields: {preview_columns}. "
                    "Use min/mean/max patterns and correlations to understand each column's role."
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


def _build_column_summaries(distributions: dict, limit: int = 25) -> list:
    summaries = []
    for column_name, stats in list(distributions.items())[:limit]:
        summaries.append(
            {
                "column": column_name,
                "mean": stats.get("mean"),
                "median": stats.get("median"),
                "min": stats.get("min"),
                "max": stats.get("max"),
                "std_dev": stats.get("std_dev"),
                "missing_values": stats.get("missing_values"),
                "is_unusual": stats.get("is_unusual"),
            }
        )
    return summaries


def _parse_model_json_array(content: str):
    """Best-effort parse for model output that should contain a JSON array."""
    text = (content or "").strip()
    if not text:
        raise json.JSONDecodeError("Empty model response", text, 0)

    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]).strip()

    # First try direct parse
    parsed = json.loads(text)
    if isinstance(parsed, list):
        return parsed
    raise json.JSONDecodeError("Expected a JSON array", text, 0)


def _parse_model_json_array_best_effort(content: str):
    """Parse JSON array even when the model adds extra prefix/suffix text."""
    try:
        return _parse_model_json_array(content)
    except json.JSONDecodeError:
        pass

    text = (content or "").strip()
    match = re.search(r"\[\s*\{[\s\S]*\}\s*\]", text)
    if match:
        return _parse_model_json_array(match.group(0))

    raise json.JSONDecodeError("No JSON array found in model response", text, 0)


def _extract_bullet_lines(text: str) -> list:
    lines = []
    for line in (text or "").split("\n"):
        cleaned = line.strip()
        if cleaned.startswith("-"):
            lines.append(cleaned)
    return lines


def _find_column_meanings_insight(insights: list):
    for insight in insights:
        title = str(insight.get("title", "")).lower()
        if "column meanings" in title:
            return insight

    for insight in insights:
        explanation = str(insight.get("explanation", ""))
        bullets = _extract_bullet_lines(explanation)
        if bullets and any("source:" in b.lower() for b in bullets):
            return insight

    return None


def _generate_column_meanings_text(model_name: str, dataset_name: str, distributions: dict):
    columns = list(distributions.keys())[:20]
    if not columns:
        return ""

    prompt = f"""You are a particle-physics explainer.

Dataset: {dataset_name}
Columns: {columns}

Return ONLY bullet lines, one per column, in this exact format:
- <column>: <physics meaning>. Source: <url>

Rules:
1) Explain likely physics meaning in plain English.
2) Include likely units when appropriate.
3) Each line must include one source URL.
4) No JSON, no markdown fences, no extra text.
"""

    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200,
    )
    content = response.choices[0].message.content.strip()
    bullet_lines = _extract_bullet_lines(content)
    if not bullet_lines:
        return ""
    return "\n".join(bullet_lines[:20])


def _ensure_column_meanings_insight(
    insights: list,
    model_name: str,
    dataset_name: str,
    distributions: dict,
) -> list:
    if not isinstance(insights, list):
        return insights

    existing = _find_column_meanings_insight(insights)
    if existing:
        existing["title"] = "Column Meanings"
        return insights

    try:
        explanation = _generate_column_meanings_text(model_name, dataset_name, distributions)
    except Exception:
        return insights

    if not explanation:
        return insights

    new_item = {
        "title": "Column Meanings",
        "explanation": explanation,
        "surprise_level": 4,
        "finding_type": "pattern",
    }

    if len(insights) >= 5:
        replace_index = None
        for idx, item in enumerate(insights):
            if "column guide" in str(item.get("title", "")).lower():
                replace_index = idx
                break
        if replace_index is None:
            replace_index = len(insights) - 1
        insights[replace_index] = new_item
        return insights

    insights.append(new_item)
    return insights

def generate_insights(analysis_data: dict, dataset_name: str) -> list:
    """
    Sends analysis results to Cerebras and returns
    5 plain-English insights as a list of dicts.
    analysis_data must have keys: distributions, top_correlations, anomaly_summary
    """
    # Pull out the parts we need for the prompt
    top_correlations = json.dumps(analysis_data.get("top_correlations", []), indent=2)
    anomaly_summary = analysis_data.get("anomaly_summary", {})
    distributions = analysis_data.get("distributions", {})
    column_summaries = json.dumps(_build_column_summaries(distributions), indent=2)

    # Find which columns were flagged as unusual (skewness > 2.0)
    unusual_columns = [col for col, stats in distributions.items() if stats.get("is_unusual")]

    # Build the prompt
    prompt = f"""You are a data analyst explaining results to non-experts.

Dataset: {dataset_name}

Here are the automated statistical findings:

COLUMN SUMMARIES (name + descriptive stats):
{column_summaries}

TOP CORRELATIONS:
{top_correlations}

ANOMALY DETECTION:
- Total events: {anomaly_summary.get("total_events", 0)}
- Anomalies found: {anomaly_summary.get("total_anomalies", 0)} ({anomaly_summary.get("anomaly_percentage", 0)}%)
- Features most different in anomalies: {anomaly_summary.get("most_anomalous_features", [])}

UNUSUAL DISTRIBUTIONS (highly skewed columns):
{unusual_columns}

Generate exactly 5 insights from this data. Each insight must:
1. Be written in plain English for general users
2. Explain what was found and why it is interesting
3. Be specific — mention actual variable names and numbers
4. Have a surprise_level from 1 (expected) to 10 (very surprising)
5. Include at least one dataset-overview insight that explains what the dataset appears to contain
6. Include at least one column-guide insight that explains what important columns likely represent
7. Include one insight with title exactly "Column Meanings" and explanation formatted as bullet points, one line per column in this exact format: "- <column>: <physics meaning>. Source: <url>"
8. For "Column Meanings", explain each variable in particle-physics terms (kinematics, detector, or reconstruction context), and include likely units only when appropriate (for example GeV, radians)
9. For each column bullet, include one authoritative reference URL for the exact definition (prefer CERN Open Data docs, experiment docs, PDG, or other trusted HEP references)
10. If uncertain, use language like "likely" or "probably" instead of presenting guesses as facts

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

            try:
                parsed = _parse_model_json_array_best_effort(content)
                parsed = _ensure_column_meanings_insight(
                    parsed,
                    model_name,
                    dataset_name,
                    distributions,
                )
                return parsed
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
