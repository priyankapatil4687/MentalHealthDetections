"""Loaders that turn open datasets into the project's canonical CSV layout.

Labels from these sources are PROXIES (emotion tags, subreddit membership), not clinical
status. Output file names contain "proxy" so the reports can flag it.
"""
import hashlib
import re
from pathlib import Path

import pandas as pd
import requests

HF_ROWS = "https://datasets-server.huggingface.co/rows"
BRIGHTER = "brighter-dataset/BRIGHTER-emotion-categories"  # CC-BY-4.0, no age field
BRIGHTER_LANG = {"eng": "en", "hin": "hi", "mar": "mr"}
NEGATIVE_EMOTIONS = ("sadness", "fear")


def _fetch_via_parquet(lang, splits, timeout):
    """Fallback: the auto-converted parquet files on the Hugging Face hub."""
    import io
    frames = []
    for split in splits:
        url = f"https://huggingface.co/datasets/{BRIGHTER}/resolve/refs%2Fconvert%2Fparquet/{lang}/{split}/0000.parquet"
        r = requests.get(url, timeout=timeout)
        if r.status_code == 404:
            continue
        r.raise_for_status()
        frames.append(pd.read_parquet(io.BytesIO(r.content)).assign(split=split))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def fetch_brighter(lang="hin", splits=("train", "dev", "test"), max_rows=None, timeout=60):
    """Download one BRIGHTER language (rows API first, parquet files as fallback)."""
    if lang not in BRIGHTER_LANG:
        raise ValueError(f"lang must be one of {sorted(BRIGHTER_LANG)}")
    try:
        df = _fetch_via_rows_api(lang, splits, max_rows, timeout)
    except requests.RequestException:
        df = _fetch_via_parquet(lang, splits, timeout)
    if df.empty:
        raise ValueError("No rows downloaded. Check your internet connection and the language code.")
    return df.head(max_rows) if max_rows else df


def _fetch_via_rows_api(lang, splits, max_rows, timeout):
    rows = []
    for split in splits:
        offset = 0
        while True:
            r = requests.get(HF_ROWS, params={"dataset": BRIGHTER, "config": lang, "split": split,
                                              "offset": offset, "length": 100}, timeout=timeout)
            if r.status_code == 404:
                break
            r.raise_for_status()
            batch = r.json().get("rows", [])
            if not batch:
                break
            rows += [dict(b["row"], split=split) for b in batch]
            offset += len(batch)
            if max_rows and len(rows) >= max_rows:
                break
        if max_rows and len(rows) >= max_rows:
            break
    return pd.DataFrame(rows)


def prepare_brighter(df, lang):
    """Proxy label: negative_affect if sadness or fear is annotated, else neutral_or_other."""
    neg = df[[c for c in NEGATIVE_EMOTIONS if c in df.columns]].apply(pd.to_numeric, errors="coerce").fillna(0).max(axis=1) > 0
    return pd.DataFrame({
        "source_id": [f"{lang}_{i}" for i in df["id"].astype(str)],
        "text": df["text"],
        "label": neg.map({True: "negative_affect", False: "neutral_or_other"}),
        "age": pd.NA,
        "language": BRIGHTER_LANG[lang],
    })


_AGE_PATTERNS = [
    re.compile(r"\bI\s*(?:am|'m|’m)\s+(\d{2})\b(?!\s*(?:%|percent|months|weeks|days|pounds|lbs|kg|mg))", re.I),
    re.compile(r"[\(\[]\s*(\d{2})\s*[mMfF]\s*[\)\]]"),
    re.compile(r"\b(\d{2})\s?[mMfF]\b(?!\w)"),
    re.compile(r"\b(\d{2})\s*(?:years?|yrs?)[ -]old\b", re.I),
]


def extract_stated_age(text, lo=13, hi=80):
    """Return an age the author explicitly states about themselves, else None. Never infers age."""
    t = str(text)
    for pat in _AGE_PATTERNS:
        m = pat.search(t)
        if m:
            age = int(m.group(1))
            if lo <= age <= hi:
                return age
    return None


def _hash_author(a, salt):
    return "u_" + hashlib.sha256((salt + str(a)).encode()).hexdigest()[:10]


def prepare_reddit_mh(files, positive=("depression",), min_chars=30, salt="mini-project"):
    """Reddit Mental Health Dataset (Low et al. 2020, Zenodo 3941387, PDDL).

    files: CSVs such as depression_pre_features_tfidf_256.csv; needs columns subreddit, author, post.
    Subreddits in `positive` get label mh_forum, all others control. Age comes only from explicit
    self-statements such as "(24F)" or "I am 24".
    """
    parts = []
    for f in files:
        d = pd.read_csv(f, usecols=lambda c: c in ("subreddit", "author", "post"), dtype=str)
        missing = {"subreddit", "author", "post"} - set(d.columns)
        if missing:
            raise ValueError(f"{Path(f).name}: missing columns {sorted(missing)}")
        parts.append(d)
    d = pd.concat(parts, ignore_index=True).dropna(subset=["post"])
    d = d[d["post"].str.len() >= min_chars]
    out = pd.DataFrame({
        "source_id": d["author"].map(lambda a: _hash_author(a, salt)),
        "text": d["post"],
        "label": d["subreddit"].str.lower().isin({p.lower() for p in positive}).map(
            {True: "mh_forum", False: "control"}),
        "age": d["post"].map(extract_stated_age),
        "language": "en",
    })
    return out.reset_index(drop=True)


def age_validation_sample(df, n=100, seed=42, context=60):
    """Rows with an extracted age plus the matching snippet, for manual verification."""
    sub = df[df["age"].notna()].sample(min(n, int(df["age"].notna().sum())), random_state=seed)
    snippets = []
    for t, a in zip(sub["text"], sub["age"]):
        m = re.search(rf"\b{int(a)}\b", t)
        s = max(0, (m.start() if m else 0) - context)
        snippets.append(t[s:s + 2 * context].replace("\n", " "))
    return pd.DataFrame({"source_id": sub["source_id"].values, "extracted_age": sub["age"].astype(int).values,
                         "snippet": snippets, "correct_yes_no": ""})
