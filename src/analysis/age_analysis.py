import math
from collections import Counter

import numpy as np
import pandas as pd

from src.analysis.common import label_table, ordered_labels
from src.config import get_dir
from src.utils.plotting import save_heatmap, save_stacked_bar
from src.utils.stats import benjamini_hochberg, chi_square_test, kruskal_test
from src.utils.text import text_features, tokenize


def top_terms_by_group(df, group_col, k=10, min_count=5, alpha=0.5):
    """Terms over-represented in each group vs the rest (log-odds ratio, z-scored)."""
    counts = {g: Counter(t for txt in sub["text_clean"] for t in tokenize(txt)) for g, sub in df.groupby(group_col)}
    total = Counter()
    for c in counts.values():
        total.update(c)
    vocab = {t for t, c in total.items() if c >= min_count and len(t) > 1}
    V = len(vocab)
    rows = []
    for g, c in counts.items():
        rest = total - c
        ng = sum(c[t] for t in vocab)
        nr = sum(rest[t] for t in vocab)
        scored = []
        for t in vocab:
            fg, fr = c[t], rest[t]
            lg = math.log((fg + alpha) / (ng + alpha * V - fg - alpha))
            lr = math.log((fr + alpha) / (nr + alpha * V - fr - alpha))
            var = 1 / (fg + alpha) + 1 / (fr + alpha)
            scored.append((t, (lg - lr) / math.sqrt(var), fg))
        scored.sort(key=lambda x: -x[1])
        for t, z, fg in scored[:k]:
            rows.append({group_col: g, "term": t, "z_score": z, "count_in_group": fg})
    return pd.DataFrame(rows)


def run_age_analysis(df, cfg):
    """O1 (age-wise text patterns) and O2 (age-wise label/risk distribution)."""
    tables, figs = get_dir(cfg, "tables_dir"), get_dir(cfg, "figures_dir")
    min_n = cfg["analysis"]["min_group_n"]
    known = df[df["age_band"] != "unknown"].copy()
    summary = {"rows_total": int(len(df)), "rows_with_age": int(len(known))}
    if len(known) == 0:
        summary["status"] = "unavailable: no reliable age information in this dataset"
        return summary

    order = [b for b in cfg["age"]["bands"]["labels"] if b in set(known["age_band"])]
    labels = ordered_labels(known, cfg)
    known["age_band"] = pd.Categorical(known["age_band"], categories=order, ordered=True)

    lt = label_table(known, "age_band", labels, min_n)
    lt.to_csv(tables / "age_label_table.csv", index=False)
    counts = pd.crosstab(known["age_band"], known["label"]).reindex(columns=labels, fill_value=0)
    pct = counts.div(counts.sum(axis=1), axis=0) * 100
    save_stacked_bar(pct, "Label distribution by age band", figs / "age_label_distribution.png", "Age band")
    save_heatmap(pct, "Label % by age band", figs / "age_label_heatmap.png", fmt=".1f",
                 xlabel="Label", ylabel="Age band")

    pvals, names = [], []
    chi = chi_square_test(counts)
    summary["label_vs_age_chi_square"] = chi
    if chi:
        pvals.append(chi["p_value"]); names.append("label_vs_age")

    feats = pd.DataFrame([text_features(t) for t in known["text_clean"]], index=known.index)
    known = known.join(feats)
    kw = {}
    for col in ["word_count", "first_person_rate"]:
        groups = {b: known.loc[known["age_band"] == b, col].values for b in order}
        res = kruskal_test(groups, min_n)
        kw[col] = res
        if res:
            pvals.append(res["p_value"]); names.append(col)
    summary["kruskal_wallis"] = kw
    if pvals:
        adj = benjamini_hochberg(pvals)
        summary["fdr_adjusted_p"] = dict(zip(names, map(float, adj)))

    fsum = known.groupby("age_band", observed=True)[["word_count", "char_count", "first_person_rate"]].mean().round(3)
    fsum.insert(0, "n", known.groupby("age_band", observed=True).size())
    fsum.to_csv(tables / "age_text_features.csv")

    terms = top_terms_by_group(known, "age_band", cfg["analysis"]["top_terms"], cfg["analysis"]["min_term_count"])
    terms.to_csv(tables / "age_top_terms.csv", index=False, encoding="utf-8-sig")

    summary["group_sizes"] = {str(k): int(v) for k, v in known["age_band"].value_counts().items()}
    summary["small_groups_below_min_n"] = [str(k) for k, v in known["age_band"].value_counts().items() if v < min_n]
    summary["elevated_share_by_age_band_pct"] = {
        str(b): float(100 * sub["label"].isin(cfg["labels"]["elevated"]).mean())
        for b, sub in known.groupby("age_band", observed=True)
    }
    summary["status"] = "ok"
    return summary
