import pandas as pd

from src.analysis.age_analysis import top_terms_by_group
from src.analysis.common import label_table, ordered_labels
from src.config import get_dir
from src.data.language import CODE_MIXED_LANGS
from src.utils.plotting import save_heatmap, save_stacked_bar
from src.utils.stats import chi_square_test


def run_language_analysis(df, cfg):
    """O3: language distribution, label balance per language, code-mixed share."""
    tables, figs = get_dir(cfg, "tables_dir"), get_dir(cfg, "figures_dir")
    min_n = cfg["analysis"]["min_group_n"]
    labels = ordered_labels(df, cfg)

    dist = df["language"].value_counts().rename_axis("language").reset_index(name="count")
    dist["pct"] = 100 * dist["count"] / len(df)
    dist.to_csv(tables / "language_distribution.csv", index=False)

    lt = label_table(df, "language", labels, min_n)
    lt.to_csv(tables / "language_label_table.csv", index=False)
    counts = pd.crosstab(df["language"], df["label"]).reindex(columns=labels, fill_value=0)
    pct = counts.div(counts.sum(axis=1), axis=0) * 100
    save_stacked_bar(pct, "Label distribution by language", figs / "language_label_distribution.png", "Language")
    save_heatmap(pct, "Label % by language", figs / "language_label_heatmap.png", fmt=".1f",
                 xlabel="Label", ylabel="Language")

    terms = top_terms_by_group(df, "language", cfg["analysis"]["top_terms"], cfg["analysis"]["min_term_count"])
    terms.to_csv(tables / "language_top_terms.csv", index=False, encoding="utf-8-sig")

    code_mixed = df["language"].isin(CODE_MIXED_LANGS)
    prov = df[df["language_source"] == "provided"]
    return {
        "status": "ok",
        "language_counts": {str(k): int(v) for k, v in df["language"].value_counts().items()},
        "languages_below_min_n": [str(k) for k, v in df["language"].value_counts().items() if v < min_n],
        "label_vs_language_chi_square": chi_square_test(counts),
        "code_mixed_share_pct": float(100 * code_mixed.mean()),
        "language_source_counts": {str(k): int(v) for k, v in df["language_source"].value_counts().items()},
        "detector_agreement_on_provided_pct": (
            float(100 * (prov["language"] == prov["language_detected"]).mean()) if len(prov) else None
        ),
        "note": "Language detection is a rule-based hint, not ground truth.",
    }


def run_combined_analysis(df, cfg):
    """O4: age band x language counts and elevated-label share, small cells flagged."""
    tables, figs = get_dir(cfg, "tables_dir"), get_dir(cfg, "figures_dir")
    min_n = cfg["analysis"]["min_group_n"]
    known = df[df["age_band"] != "unknown"]
    if known.empty:
        return {"status": "unavailable: no reliable age information in this dataset"}
    order = [b for b in cfg["age"]["bands"]["labels"] if b in set(known["age_band"])]
    counts = pd.crosstab(known["age_band"], known["language"]).reindex(order)
    counts.to_csv(tables / "age_language_counts.csv")
    save_heatmap(counts, "Posts per age band x language", figs / "age_language_counts.png", fmt="d",
                 cmap="Blues", xlabel="Language", ylabel="Age band")

    k = known.assign(elevated=known["label"].isin(cfg["labels"]["elevated"]))
    share = k.pivot_table(index="age_band", columns="language", values="elevated", aggfunc="mean").reindex(order) * 100
    reliable = share.where(counts >= min_n)
    reliable.round(1).to_csv(tables / "age_language_elevated_pct_reliable_cells.csv")
    annot = reliable.round(0).map(lambda v: "n<min" if pd.isna(v) else f"{v:.0f}")
    save_heatmap(reliable.fillna(0), f"Elevated-label % (cells with n<{min_n} hidden)",
                 figs / "age_language_elevated_pct.png", fmt="", xlabel="Language", ylabel="Age band", annot=annot)

    cells = int(counts.size)
    sparse = int((counts < min_n).sum().sum())
    return {
        "status": "ok",
        "cells_total": cells,
        "cells_below_min_n": sparse,
        "share_cells_sufficient_pct": float(100 * (cells - sparse) / cells),
        "elevated_labels": cfg["labels"]["elevated"],
    }
