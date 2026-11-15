import re
import unicodedata

import pandas as pd

from src.data.language import detect_language, normalize_language_name
from src.data.normalize import normalize_for_nlp

_URL = re.compile(r"(https?://\S+|www\.\S+)", re.I)
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
_HANDLE = re.compile(r"(?<![\w])(@\w+|u/\w+)")
_PHONE = re.compile(r"(?<![\w])\+?\d[\d\s\-]{8,}\d(?![\w])")

LABEL_ALIASES = {
    "normal": "none", "no": "none", "minimal": "none", "not depressed": "none",
    "not_depressed": "none", "control": "none",
    "low": "mild", "medium": "moderate", "high": "severe", "moderately severe": "severe",
}


def scrub_pii(text):
    """Replace URLs, e-mails, handles and phone numbers with placeholder tokens."""
    t = _URL.sub("<URL>", text)
    t = _EMAIL.sub("<EMAIL>", t)
    t = _HANDLE.sub("<USER>", t)
    t = _PHONE.sub("<PHONE>", t)
    return t


def normalize_text(text):
    t = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", t).strip()


def _age_band(age, cfg):
    edges = cfg["age"]["bands"]["edges"]
    labels = cfg["age"]["bands"]["labels"]
    return pd.cut(age, bins=edges, labels=labels, right=False).astype("object")


def clean_dataframe(df, cfg):
    """Privacy-preserving cleaning. Never imputes age; unknowns stay 'unknown'."""
    rep = {"rows_input": int(len(df))}
    d = df.copy()

    d["text"] = d["text"].fillna("").astype(str)
    blank = d["text"].str.strip() == ""
    rep["dropped_missing_text"] = int(blank.sum())
    d = d[~blank]

    lab = d["label"].fillna("").astype(str).str.strip().str.lower()
    lab = lab.replace(LABEL_ALIASES)
    d = d.assign(label=lab)
    blank = d["label"] == ""
    rep["dropped_missing_label"] = int(blank.sum())
    d = d[~blank].copy()

    d["text_original"] = d["text"]
    scrubbed = d["text_original"].map(scrub_pii)
    rep["rows_with_pii_removed"] = int((scrubbed != d["text_original"]).sum())
    d["text_clean"] = scrubbed.map(normalize_text)
    short = d["text_clean"].str.len() < cfg["text"]["min_chars"]
    rep["dropped_too_short"] = int(short.sum())
    d = d[~short].copy()

    key = d["text_clean"].str.lower()
    dup = d.assign(_k=key).duplicated(subset=["_k", "label"], keep="first")
    rep["dropped_exact_duplicates"] = int(dup.sum())
    d = d[~dup.values].copy()

    key = d["text_clean"].str.lower()
    nlab = d.groupby(key.values)["label"].transform("nunique")
    conflict = (nlab > 1).values
    rep["dropped_conflicting_label_duplicates"] = int(conflict.sum())
    d = d[~conflict].copy()

    age = pd.to_numeric(d["age"], errors="coerce")
    rep["age_missing_or_non_numeric"] = int(age.isna().sum())
    lo, hi = cfg["age"]["min_valid"], cfg["age"]["max_valid"]
    out_of_range = age.notna() & ((age < lo) | (age > hi))
    rep["age_out_of_range_set_missing"] = int(out_of_range.sum())
    age = age.mask(out_of_range)
    d["age"] = age
    band = _age_band(age, cfg)
    valid_bands = set(cfg["age"]["bands"]["labels"])
    provided = d["age_band"].map(
        lambda x: str(x).strip() if pd.notna(x) and str(x).strip() in valid_bands else None
    )
    d["age_band"] = pd.Series(band, index=d.index).where(age.notna(), provided).fillna("unknown")

    prov = d["language"].map(normalize_language_name)
    det = d["text_clean"].map(detect_language)
    d["language_detected"] = det
    d["language_source"] = prov.map(lambda x: "provided" if isinstance(x, str) else "detected")
    d["language"] = prov.where(prov.notna(), det)
    both = prov.notna()
    rep["language_provided_rows"] = int(both.sum())
    rep["language_provided_vs_detected_agreement"] = (
        float((prov[both] == det[both]).mean()) if both.any() else None
    )

    d["text_norm"] = [normalize_for_nlp(t, l) for t, l in zip(d["text_clean"], d["language"])]

    sid = d["source_id"].astype("object")
    fallback = pd.Series([f"row_{i}" for i in range(len(d))], index=d.index)
    d["source_id"] = sid.where(sid.notna(), fallback).astype(str)

    cols = ["source_id", "text_original", "text_clean", "text_norm", "label", "age", "age_band",
            "language", "language_source", "language_detected", "source"]
    d = d[cols].reset_index(drop=True)
    rep["rows_output"] = int(len(d))
    rep["age_band_unknown"] = int((d["age_band"] == "unknown").sum())
    return d, rep
