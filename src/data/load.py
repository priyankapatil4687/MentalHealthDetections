import json
from pathlib import Path

import pandas as pd

ALIASES = {
    "text": ["text", "post", "content", "body", "message", "mood_text", "comment", "tweet"],
    "label": ["label", "category", "diagnosis", "class", "target", "risk", "risk_label"],
    "age": ["age", "years", "age_years"],
    "age_band": ["age_band", "age_group", "agegroup"],
    "language": ["language", "lang", "preferred_language"],
    "source_id": ["source_id", "user_id", "author_id", "response_id", "id"],
    "phq9": ["phq9_score", "phq9"],
}

CANONICAL = ["text", "label", "age", "age_band", "language", "source_id"]


def phq9_to_label(score):
    try:
        s = float(score)
    except (TypeError, ValueError):
        return None
    if s != s or s < 0 or s > 27:
        return None
    if s <= 4:
        return "none"
    if s <= 9:
        return "mild"
    if s <= 19:
        return "moderate"
    return "severe"


def read_any(path):
    """Read CSV, TSV, JSON, JSONL or XLSX into a DataFrame of strings."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    ext = path.suffix.lower()
    if ext in (".csv", ".txt"):
        return pd.read_csv(path, dtype=str, encoding="utf-8-sig")
    if ext == ".tsv":
        return pd.read_csv(path, dtype=str, sep="\t", encoding="utf-8-sig")
    if ext == ".jsonl":
        return pd.read_json(path, lines=True, dtype=False, encoding="utf-8")
    if ext == ".json":
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        if isinstance(data, dict):
            for key in ("records", "data", "rows", "items"):
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
        return pd.DataFrame(data)
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(path, dtype=str)
    raise ValueError(f"Unsupported file type '{ext}'. Use csv, tsv, json, jsonl or xlsx.")


def load_dataset(path):
    """Load a file and map its columns to the canonical schema.

    Returns (DataFrame, mapping) where mapping shows which source column was used.
    """
    raw = read_any(path)
    lookup = {str(c).strip().lower(): c for c in raw.columns}
    mapping = {}
    for canon, names in ALIASES.items():
        for n in names:
            if n in lookup:
                mapping[canon] = lookup[n]
                break

    if "text" not in mapping:
        raise ValueError(
            f"No text column found. Columns present: {list(raw.columns)}. "
            f"Accepted names: {ALIASES['text']}"
        )
    if "label" not in mapping and "phq9" not in mapping:
        cols = [str(c) for c in raw.columns]
        if {"subreddit", "author", "post"} <= set(cols):
            raise ValueError(
                "This looks like a raw Reddit Mental Health file (no label column). Prepare it first: "
                "python main.py prepare-reddit --files <file1.csv> <file2.csv> --positive depression "
                "(use at least one mental-health subreddit file and one control file), then run on "
                "data/raw/reddit_mh_proxy.csv.")
        shown = ", ".join(cols[:12]) + (f" ... (+{len(cols) - 12} more)" if len(cols) > 12 else "")
        raise ValueError(
            f"No label column found. Columns present: {shown}. "
            f"Accepted names: {ALIASES['label'] + ALIASES['phq9']}"
        )

    df = pd.DataFrame(index=raw.index)
    for canon in CANONICAL:
        df[canon] = raw[mapping[canon]] if canon in mapping else pd.NA
    if "label" not in mapping:
        df["label"] = raw[mapping["phq9"]].map(phq9_to_label)
        mapping["label"] = f"derived from {mapping['phq9']} (PHQ-9 bands)"
    df["source"] = Path(path).name
    return df.reset_index(drop=True), mapping
