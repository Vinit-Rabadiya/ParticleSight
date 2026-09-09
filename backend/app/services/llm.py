import os
import json
import re
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("CEREBRAS_API_KEY")
client = Cerebras(api_key=API_KEY) if API_KEY else None

# qwen-3.8-27b — fast, free tier, good quality
# gpt-oss-120b — larger fallback
PREFERRED_MODEL = os.getenv("CEREBRAS_MODEL", "qwen-3.8-27b")
MODEL_CANDIDATES = [PREFERRED_MODEL, "gpt-oss-120b"]

# Known physics column definitions used as fallback when the LLM is unavailable
KNOWN_COLUMNS = {
    "run":     ("Run number — identifies the LHC data-taking period", "https://opendata.cern.ch/docs/cms-guide-for-research"),
    "event":   ("Event number — unique identifier for each recorded collision", "https://opendata.cern.ch/docs/cms-guide-for-research"),
    "type":    ("Particle type label (e.g. muon pair or electron pair)", "https://opendata.cern.ch/docs/cms-guide-for-research"),
    "e":       ("Total energy of the particle in GeV", "https://pdg.lbl.gov/"),
    "e1":      ("Energy of the first particle in GeV", "https://pdg.lbl.gov/"),
    "e2":      ("Energy of the second particle in GeV", "https://pdg.lbl.gov/"),
    "px":      ("Momentum component along the x-axis in GeV/c", "https://pdg.lbl.gov/"),
    "py":      ("Momentum component along the y-axis in GeV/c", "https://pdg.lbl.gov/"),
    "pz":      ("Momentum component along the z-axis (beam direction) in GeV/c", "https://pdg.lbl.gov/"),
    "px1":     ("x-momentum of the first particle in GeV/c", "https://pdg.lbl.gov/"),
    "py1":     ("y-momentum of the first particle in GeV/c", "https://pdg.lbl.gov/"),
    "pz1":     ("z-momentum of the first particle in GeV/c", "https://pdg.lbl.gov/"),
    "px2":     ("x-momentum of the second particle in GeV/c", "https://pdg.lbl.gov/"),
    "py2":     ("y-momentum of the second particle in GeV/c", "https://pdg.lbl.gov/"),
    "pz2":     ("z-momentum of the second particle in GeV/c", "https://pdg.lbl.gov/"),
    "pt":      ("Transverse momentum — momentum perpendicular to the beam axis in GeV/c", "https://pdg.lbl.gov/"),
    "pt1":     ("Transverse momentum of the first particle in GeV/c", "https://pdg.lbl.gov/"),
    "pt2":     ("Transverse momentum of the second particle in GeV/c", "https://pdg.lbl.gov/"),
    "eta":     ("Pseudorapidity — describes the angle of the particle relative to the beam (0 = perpendicular, ±∞ = beam direction)", "https://pdg.lbl.gov/"),
    "eta1":    ("Pseudorapidity of the first particle", "https://pdg.lbl.gov/"),
    "eta2":    ("Pseudorapidity of the second particle", "https://pdg.lbl.gov/"),
    "phi":     ("Azimuthal angle of the particle around the beam axis in radians", "https://pdg.lbl.gov/"),
    "phi1":    ("Azimuthal angle of the first particle in radians", "https://pdg.lbl.gov/"),
    "phi2":    ("Azimuthal angle of the second particle in radians", "https://pdg.lbl.gov/"),
    "q":       ("Electric charge of the particle (+1 or −1)", "https://pdg.lbl.gov/"),
    "q1":      ("Electric charge of the first particle", "https://pdg.lbl.gov/"),
    "q2":      ("Electric charge of the second particle", "https://pdg.lbl.gov/"),
    "m":       ("Invariant mass of the particle or system in GeV/c²", "https://pdg.lbl.gov/"),
    "m1":      ("Invariant mass of the first particle in GeV/c²", "https://pdg.lbl.gov/"),
    "m2":      ("Invariant mass of the second particle in GeV/c²", "https://pdg.lbl.gov/"),
    "minv":    ("Invariant mass of the two-particle system in GeV/c² — used to identify resonances like Z or Higgs", "https://pdg.lbl.gov/"),
    "chisq":   ("Chi-squared fit quality of the track reconstruction — lower is better", "https://opendata.cern.ch/docs/cms-guide-for-research"),
    "chisq1":  ("Track fit chi-squared for the first particle", "https://opendata.cern.ch/docs/cms-guide-for-research"),
    "chisq2":  ("Track fit chi-squared for the second particle", "https://opendata.cern.ch/docs/cms-guide-for-research"),
    "dxy":     ("Transverse impact parameter — distance from the beam axis in cm; large values suggest secondary vertices", "https://opendata.cern.ch/docs/cms-guide-for-research"),
    "dxy1":    ("Transverse impact parameter of the first particle in cm", "https://opendata.cern.ch/docs/cms-guide-for-research"),
    "dxy2":    ("Transverse impact parameter of the second particle in cm", "https://opendata.cern.ch/docs/cms-guide-for-research"),
    "iso":     ("Isolation — how much energy surrounds the particle; low values mean the particle is well-isolated", "https://opendata.cern.ch/docs/cms-guide-for-research"),
    "iso1":    ("Isolation of the first particle", "https://opendata.cern.ch/docs/cms-guide-for-research"),
    "iso2":    ("Isolation of the second particle", "https://opendata.cern.ch/docs/cms-guide-for-research"),
    "met":     ("Missing transverse energy in GeV — energy imbalance suggesting invisible particles like neutrinos", "https://pdg.lbl.gov/"),
    "phimet":  ("Azimuthal angle of the missing transverse energy vector in radians", "https://pdg.lbl.gov/"),
    "x":       ("x position in the detector in cm", "https://opendata.cern.ch/docs/cms-guide-for-research"),
    "y":       ("y position in the detector in cm", "https://opendata.cern.ch/docs/cms-guide-for-research"),
    "z":       ("z position along the beam axis in cm", "https://opendata.cern.ch/docs/cms-guide-for-research"),
}


def _column_meaning_fallback(col: str) -> tuple[str, str]:
    """Return (meaning, url) for a column using the known definitions table."""
    key = col.lower().replace(" ", "").replace("_", "").replace("-", "")
    if key in KNOWN_COLUMNS:
        return KNOWN_COLUMNS[key]
    return (
        f"Numeric quantity recorded per event — check the dataset documentation for the exact definition of '{col}'",
        f"https://opendata.cern.ch/search?q={col}",
    )


def _build_column_meanings_fallback(columns: list) -> str:
    lines = []
    for col in columns[:20]:
        meaning, url = _column_meaning_fallback(col)
        lines.append(f"- {col}: {meaning}. Source: {url}")
    return "\n".join(lines)


def _local_fallback_insights(analysis_data: dict, dataset_name: str, reason: str) -> list:
    """Deterministic insights when the AI API is unavailable."""
    insights = []
    top_correlations = analysis_data.get("top_correlations", [])
    anomaly_summary = analysis_data.get("anomaly_summary", {})
    distributions = analysis_data.get("distributions", {})
    columns = list(distributions.keys())
    preview_columns = ", ".join(columns[:8]) if columns else "none detected"

    insights.append({
        "title": "Dataset At A Glance",
        "explanation": (
            f"{dataset_name} contains {anomaly_summary.get('total_events', 0):,} events "
            f"with {len(distributions)} numeric columns. "
            f"Columns present: {preview_columns}."
        ),
        "surprise_level": 2,
        "finding_type": "pattern",
    })

    if columns:
        insights.append({
            "title": "Column Meanings",
            "explanation": _build_column_meanings_fallback(columns),
            "surprise_level": 1,
            "finding_type": "pattern",
        })

    if top_correlations:
        strongest = top_correlations[0]
        r = strongest.get("correlation", 0)
        insights.append({
            "title": "Strongest Correlation",
            "explanation": (
                f"The strongest relationship is between {strongest.get('variable_1')} and "
                f"{strongest.get('variable_2')} (r = {r:.3f}, {strongest.get('direction')}). "
                f"This is a {strongest.get('strength')} correlation."
            ),
            "surprise_level": 6 if abs(r) >= 0.8 else 4,
            "finding_type": "correlation",
        })

    total = anomaly_summary.get("total_events", 0)
    pct = anomaly_summary.get("anomaly_percentage", 0)
    if total:
        insights.append({
            "title": "Anomaly Rate",
            "explanation": (
                f"{anomaly_summary.get('total_anomalies', 0):,} of {total:,} events ({pct}%) "
                f"were flagged as anomalous by Isolation Forest."
            ),
            "surprise_level": 7 if pct >= 5 else 3,
            "finding_type": "anomaly",
        })

    unusual = [c for c, s in distributions.items() if s.get("is_unusual")]
    if unusual:
        insights.append({
            "title": "Unusual Distributions",
            "explanation": (
                f"{len(unusual)} column(s) have highly skewed distributions: "
                f"{', '.join(unusual[:4])}. This is common in particle physics where most "
                f"events cluster near zero but rare high-energy events create long tails."
            ),
            "surprise_level": 5,
            "finding_type": "distribution",
        })

    return insights[:5]


def _build_column_summaries(distributions: dict, limit: int = 15) -> list:
    summaries = []
    for col, stats in list(distributions.items())[:limit]:
        summaries.append({
            "column": col,
            "mean": stats.get("mean"),
            "min": stats.get("min"),
            "max": stats.get("max"),
            "is_unusual": stats.get("is_unusual"),
        })
    return summaries


def _parse_model_json_array(content: str):
    text = (content or "").strip()
    if not text:
        raise json.JSONDecodeError("Empty model response", text, 0)
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]).strip()
    parsed = json.loads(text)
    if isinstance(parsed, list):
        return parsed
    raise json.JSONDecodeError("Expected a JSON array", text, 0)


def _parse_model_json_array_best_effort(content: str):
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
    return [l.strip() for l in (text or "").split("\n") if l.strip().startswith("-")]


def _call_llm(model_name: str, prompt: str, max_tokens: int) -> str:
    """Single LLM call — raises on failure."""
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def _generate_column_meanings(dataset_name: str, columns: list) -> str:
    """
    Dedicated LLM call just for column meanings.
    Runs separately from the main insights call so it has its own token budget.
    Falls back to the KNOWN_COLUMNS table if the LLM fails.
    """
    if not columns:
        return ""

    prompt = f"""You are a particle-physics expert writing for general users.

Dataset: {dataset_name}
Column names: {columns}

For each column write exactly one bullet line in this format:
- <column>: <plain-English physics meaning, include units if applicable>. Source: <authoritative URL>

Use these source URLs when relevant:
- PDG (particle properties): https://pdg.lbl.gov/
- CMS detector/reconstruction: https://opendata.cern.ch/docs/cms-guide-for-research
- CERN Open Data portal: https://opendata.cern.ch/

Rules:
- One line per column, no extra text
- No JSON, no markdown fences
- If unsure, say "likely" instead of stating as fact
"""

    last_err = None
    for model in MODEL_CANDIDATES:
        try:
            content = _call_llm(model, prompt, max_tokens=1500)
            lines = _extract_bullet_lines(content)
            if lines:
                return "\n".join(lines[:20])
        except Exception as e:
            last_err = e
            continue

    # LLM failed — use the known definitions table
    print(f"Column meanings LLM failed ({last_err}), using known definitions table.")
    return _build_column_meanings_fallback(columns)


def generate_insights(analysis_data: dict, dataset_name: str) -> list:
    distributions = analysis_data.get("distributions", {})
    top_correlations = analysis_data.get("top_correlations", [])
    anomaly_summary = analysis_data.get("anomaly_summary", {})
    columns = list(distributions.keys())

    if client is None:
        print("No Cerebras API key — using local fallback.")
        return _local_fallback_insights(analysis_data, dataset_name, "missing API key")

    unusual_columns = [c for c, s in distributions.items() if s.get("is_unusual")]
    column_summaries = json.dumps(_build_column_summaries(distributions), indent=2)

    # ── Step 1: Generate the 4 statistical insights (no Column Meanings here) ──
    insights_prompt = f"""You are a data analyst explaining particle-physics results to non-experts.

Dataset: {dataset_name}

COLUMN SUMMARIES:
{column_summaries}

TOP CORRELATIONS:
{json.dumps(top_correlations[:5], indent=2)}

ANOMALY DETECTION:
- Total events: {anomaly_summary.get("total_events", 0):,}
- Anomalies found: {anomaly_summary.get("total_anomalies", 0)} ({anomaly_summary.get("anomaly_percentage", 0)}%)
- Top anomalous features: {[f.get("feature") for f in anomaly_summary.get("most_anomalous_features", [])[:3]]}

UNUSUAL DISTRIBUTIONS: {unusual_columns}

Generate exactly 4 insights. Each must:
1. Be plain English for non-experts
2. Mention specific variable names and numbers
3. Have a surprise_level from 1 to 10
4. Include one insight titled "Dataset At A Glance" explaining what this dataset contains and what physics it studies

Return ONLY a valid JSON array, no extra text:
[
  {{
    "title": "...",
    "explanation": "...",
    "surprise_level": 5,
    "finding_type": "correlation"
  }}
]

finding_type must be one of: correlation, anomaly, distribution, pattern"""

    insights = None
    last_error = None
    for model in MODEL_CANDIDATES:
        try:
            content = _call_llm(model, insights_prompt, max_tokens=1200)
            insights = _parse_model_json_array_best_effort(content)
            if isinstance(insights, list) and len(insights) > 0:
                break
        except Exception as e:
            last_error = e
            continue

    if not insights:
        print(f"Insights LLM failed: {last_error} — using local fallback.")
        return _local_fallback_insights(analysis_data, dataset_name, str(last_error))

    # ── Step 2: Generate Column Meanings as a separate dedicated call ──
    column_meanings_text = _generate_column_meanings(dataset_name, columns)
    if column_meanings_text:
        insights.append({
            "title": "Column Meanings",
            "explanation": column_meanings_text,
            "surprise_level": 1,
            "finding_type": "pattern",
        })

    return insights[:5]
