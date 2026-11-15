from src.data.load import CANONICAL


def profile_dataset(df, mapping):
    """Summary of a loaded (not yet cleaned) dataset, for the data card and sanity checks."""
    import pandas as pd

    age = pd.to_numeric(df["age"], errors="coerce")
    prof = {
        "rows": int(len(df)),
        "column_mapping": {k: str(v) for k, v in mapping.items()},
        "missing_counts": {c: int(df[c].isna().sum()) for c in CANONICAL},
        "exact_duplicate_rows": int(df.duplicated(subset=["text", "label"]).sum()),
        "label_counts_raw": {str(k): int(v) for k, v in df["label"].fillna("<missing>").value_counts().items()},
        "age_available": bool(df["age"].notna().any() or df["age_band"].notna().any()),
        "age_numeric_count": int(age.notna().sum()),
        "age_min": None if age.dropna().empty else float(age.min()),
        "age_max": None if age.dropna().empty else float(age.max()),
        "language_counts_raw": {str(k): int(v) for k, v in df["language"].fillna("<missing>").value_counts().items()},
    }
    warnings = []
    if not prof["age_available"]:
        warnings.append("No age information: age analyses (O1, O2, O4) will be skipped.")
    if prof["missing_counts"]["language"] == len(df):
        warnings.append("No language column: language will be detected by rules (a hint only).")
    if prof["exact_duplicate_rows"] > 0:
        warnings.append("Duplicate rows found; they will be removed in cleaning.")
    prof["warnings"] = warnings
    return prof
