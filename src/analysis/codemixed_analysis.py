import pandas as pd

from src.analysis.common import ordered_labels
from src.config import get_dir
from src.data.language import CODE_MIXED_LANGS
from src.data.normalize import ROMAN_LANGS
from src.models.train import choose_splits, metrics, oof_predict
from src.utils.text import tokenize


def run_codemixed_analysis(df, cfg):
    """O3 (code-mixed part): how many rows are normalized, vocabulary effect, model effect."""
    tables = get_dir(cfg, "tables_dir")
    sub = df[df["language"].isin(ROMAN_LANGS)].copy()
    if sub.empty:
        return {"status": "skipped: no Romanized / code-mixed rows"}

    changed = sub["text_norm"] != sub["text_clean"]
    vocab_before = len({t for x in sub["text_clean"] for t in tokenize(x)})
    vocab_after = len({t for x in sub["text_norm"] for t in tokenize(x)})
    out = {
        "status": "ok",
        "romanized_rows": int(len(sub)),
        "share_of_dataset_pct": float(100 * len(sub) / len(df)),
        "rows_changed_by_normalization": int(changed.sum()),
        "vocab_before": vocab_before,
        "vocab_after": vocab_after,
        "code_mixed_languages": sorted(set(sub["language"]) & (CODE_MIXED_LANGS | ROMAN_LANGS)),
    }

    if cfg["codemixed"]["save_examples"] and changed.any():
        ex = sub[changed].head(cfg["codemixed"]["n_examples"])[["language", "text_clean", "text_norm"]]
        ex.to_csv(tables / "codemixed_examples.csv", index=False, encoding="utf-8-sig")

    n_splits = choose_splits(sub, cfg["models"]["n_splits"])
    if len(sub) >= 100 and sub["label"].nunique() >= 2 and n_splits >= 2:
        res = {}
        for col in ("text_clean", "text_norm"):
            f1s = [metrics(sub["label"], oof_predict(sub, "logreg", s, n_splits, col))["macro_f1"]
                   for s in cfg["models"]["seeds"]]
            res[col] = float(sum(f1s) / len(f1s))
        out["macro_f1_before_normalization"] = res["text_clean"]
        out["macro_f1_after_normalization"] = res["text_norm"]
    else:
        out["model_comparison"] = "skipped: too few Romanized rows"
    pd.DataFrame([out]).drop(columns=["code_mixed_languages"]).to_csv(
        tables / "codemixed_summary.csv", index=False)
    return out
