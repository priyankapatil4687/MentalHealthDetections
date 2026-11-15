import json

import numpy as np
import pandas as pd

from src.utils.stats import wilson_ci


def ordered_labels(df, cfg):
    present = list(df["label"].unique())
    first = [l for l in cfg["labels"]["order"] if l in present]
    return first + sorted(l for l in present if l not in first)


def label_table(df, group_col, labels, min_n):
    """Long table: group, label, count, n, pct, 95% Wilson CI, sufficient_n flag."""
    rows = []
    for g, sub in df.groupby(group_col, observed=True):
        n = len(sub)
        for lab in labels:
            k = int((sub["label"] == lab).sum())
            lo, hi = wilson_ci(k, n)
            rows.append({group_col: g, "label": lab, "count": k, "n": n,
                         "pct": 100 * k / n, "ci_low_pct": 100 * lo, "ci_high_pct": 100 * hi,
                         "sufficient_n": n >= min_n})
    return pd.DataFrame(rows)


def to_jsonable(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, float) and o != o:
        return None
    raise TypeError(f"Not JSON serializable: {type(o)}")


def save_json(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=to_jsonable)
