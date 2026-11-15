import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score, matthews_corrcoef,
                             precision_score, recall_score)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

from src.analysis.common import ordered_labels
from src.config import get_dir
from src.utils.plotting import save_heatmap
from src.utils.text import tokenize

MODELS = {
    "logreg": lambda seed: LogisticRegression(max_iter=2000, class_weight="balanced", random_state=seed),
    "linear_svm": lambda seed: LinearSVC(class_weight="balanced", random_state=seed),
    "complement_nb": lambda seed: ComplementNB(),
}


def build_pipeline(kind, seed=42):
    """TF-IDF (word + char n-grams) and a classifier. Vectorizer is fit inside each training fold."""
    feats = FeatureUnion([
        ("word", TfidfVectorizer(tokenizer=tokenize, token_pattern=None, lowercase=False,
                                 ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1, sublinear_tf=True)),
    ])
    return Pipeline([("features", feats), ("clf", MODELS[kind](seed))])


def choose_splits(df, max_splits):
    min_class = int(df["label"].value_counts().min())
    return min(max_splits, min_class, df["source_id"].nunique())


def oof_predict(df, kind, seed, n_splits, text_col="text_norm"):
    """Out-of-fold predictions; all posts of one author stay in the same fold."""
    y = df["label"].values
    X = df[text_col].values
    groups = df["source_id"].values
    pred = np.empty(len(df), dtype=object)
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    for tr, te in cv.split(X, y, groups):
        if len(set(y[tr])) < 2:
            raise ValueError("A training fold has fewer than 2 classes.")
        pipe = clone(build_pipeline(kind, seed))
        pipe.fit(X[tr], y[tr])
        pred[te] = pipe.predict(X[te])
    return pred


def metrics(y, p):
    y, p = np.asarray(y), np.asarray(p)
    present = sorted(set(y))
    return {
        "n": int(len(y)),
        "accuracy": float(accuracy_score(y, p)),
        "macro_f1": float(f1_score(y, p, average="macro", labels=present, zero_division=0)),
        "macro_precision": float(precision_score(y, p, average="macro", labels=present, zero_division=0)),
        "macro_recall": float(recall_score(y, p, average="macro", labels=present, zero_division=0)),
        "mcc": float(matthews_corrcoef(y, p)) if len(present) > 1 else float("nan"),
    }


def bootstrap_ci(y, p, n_boot, seed):
    rng = np.random.default_rng(seed)
    y, p = np.asarray(y), np.asarray(p)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(y), len(y))
        vals.append(f1_score(y[idx], p[idx], average="macro", labels=sorted(set(y[idx])), zero_division=0))
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def group_definitions(df):
    known = df["age_band"] != "unknown"
    defs = {"language": df["language"]}
    if known.any():
        defs["age_band"] = df["age_band"].where(known)
        defs["age_band x language"] = (df["age_band"] + " | " + df["language"]).where(known)
    return defs


def top_features(pipe, k=10):
    """Largest logistic-regression word coefficients per class (model behaviour, not causes)."""
    names = np.array(pipe.named_steps["features"].get_feature_names_out())
    is_word = np.array([n.startswith("word__") for n in names])
    clf = pipe.named_steps["clf"]
    coef, classes = clf.coef_, list(clf.classes_)
    rows = []
    if coef.shape[0] == 1:
        coef = np.vstack([-coef[0], coef[0]])
    for i, c in enumerate(classes):
        w = np.where(is_word, coef[i], -np.inf)
        for j in np.argsort(-w)[:k]:
            rows.append({"label": c, "term": names[j].replace("word__", "", 1), "coefficient": float(coef[i][j])})
    return pd.DataFrame(rows)


def run_model_analysis(df, cfg):
    """O5: compare models overall and per age band / language, with fairness gaps."""
    tables, figs, models_dir = get_dir(cfg, "tables_dir"), get_dir(cfg, "figures_dir"), get_dir(cfg, "models_dir")
    mc = cfg["models"]
    n_splits = choose_splits(df, mc["n_splits"])
    if len(df) < 40 or df["label"].nunique() < 2 or n_splits < 2:
        return {"status": f"skipped: not enough data (rows={len(df)}, classes={df['label'].nunique()}, usable folds={n_splits})"}

    labels = ordered_labels(df, cfg)
    groups = group_definitions(df)
    overall, grp_rows, preds0 = [], [], {}
    for kind in MODELS:
        per_seed = []
        for seed in mc["seeds"]:
            p = oof_predict(df, kind, seed, n_splits)
            if seed == mc["seeds"][0]:
                preds0[kind] = p
            m = metrics(df["label"], p)
            per_seed.append(m)
            for gtype, gcol in groups.items():
                for g in sorted(gcol.dropna().unique()):
                    idx = (gcol == g).values
                    gm = metrics(df["label"].values[idx], p[idx])
                    grp_rows.append({"model": kind, "group_type": gtype, "group": g, "seed": seed, **gm})
        row = {"model": kind, "n_splits": n_splits, "seeds": len(mc["seeds"])}
        for k in ("accuracy", "macro_f1", "macro_precision", "macro_recall", "mcc"):
            vals = [m[k] for m in per_seed]
            row[f"{k}_mean"], row[f"{k}_std"] = float(np.nanmean(vals)), float(np.nanstd(vals))
        overall.append(row)
    overall_df = pd.DataFrame(overall).sort_values("macro_f1_mean", ascending=False)
    overall_df.to_csv(tables / "model_comparison_overall.csv", index=False)
    best = overall_df.iloc[0]["model"]

    g = pd.DataFrame(grp_rows)
    agg = g.groupby(["model", "group_type", "group"]).agg(
        n=("n", "first"), macro_f1_mean=("macro_f1", "mean"), macro_f1_std=("macro_f1", "std"),
        accuracy_mean=("accuracy", "mean"), macro_recall_mean=("macro_recall", "mean")).reset_index()
    agg["sufficient_n"] = agg["n"] >= mc["min_group_n"]
    ci_lo, ci_hi = [], []
    for _, r in agg.iterrows():
        if r["sufficient_n"]:
            idx = (groups[r["group_type"]] == r["group"]).values
            lo, hi = bootstrap_ci(df["label"].values[idx], preds0[r["model"]][idx], mc["bootstrap"], mc["seeds"][0])
        else:
            lo = hi = float("nan")
        ci_lo.append(lo); ci_hi.append(hi)
    agg["macro_f1_ci_low"], agg["macro_f1_ci_high"] = ci_lo, ci_hi
    agg.to_csv(tables / "model_group_metrics.csv", index=False)

    gaps = []
    for (model, gtype), sub in agg[agg["sufficient_n"]].groupby(["model", "group_type"]):
        if len(sub) < 2:
            continue
        gaps.append({"model": model, "group_type": gtype, "groups_compared": len(sub),
                     "macro_f1_gap": float(sub["macro_f1_mean"].max() - sub["macro_f1_mean"].min()),
                     "worst_group": sub.loc[sub["macro_f1_mean"].idxmin(), "group"],
                     "recall_gap": float(sub["macro_recall_mean"].max() - sub["macro_recall_mean"].min())})
    gaps_df = pd.DataFrame(gaps, columns=["model", "group_type", "groups_compared", "macro_f1_gap",
                                          "worst_group", "recall_gap"])
    gaps_df.to_csv(tables / "model_fairness_gaps.csv", index=False)

    cm = confusion_matrix(df["label"], preds0[best], labels=labels, normalize="true") * 100
    save_heatmap(pd.DataFrame(cm, index=labels, columns=labels), f"Confusion matrix % ({best})",
                 figs / "confusion_matrix_best_model.png", fmt=".0f", cmap="Blues",
                 xlabel="Predicted", ylabel="True")
    cells = agg[(agg["model"] == best) & (agg["group_type"] == "age_band x language") & agg["sufficient_n"]]
    if not cells.empty:
        piv = cells.assign(age=cells["group"].str.split(" \\| ").str[0], lang=cells["group"].str.split(" \\| ").str[1]) \
            .pivot(index="age", columns="lang", values="macro_f1_mean")
        save_heatmap(piv, f"Macro-F1 by age band x language ({best}; cells with n<{mc['min_group_n']} hidden)",
                     figs / "model_macro_f1_age_language.png", fmt=".2f", cmap="YlGn",
                     xlabel="Language", ylabel="Age band")

    final = build_pipeline(best, mc["seeds"][0]).fit(df["text_norm"].values, df["label"].values)
    joblib.dump(final, models_dir / "best_model.joblib")
    if best == "logreg":
        top_features(final, cfg["analysis"]["top_terms"]).to_csv(
            tables / "explain_top_features.csv", index=False, encoding="utf-8-sig")
    else:
        lr = build_pipeline("logreg").fit(df["text_norm"].values, df["label"].values)
        top_features(lr, cfg["analysis"]["top_terms"]).to_csv(
            tables / "explain_top_features.csv", index=False, encoding="utf-8-sig")

    return {
        "status": "ok",
        "n_rows": int(len(df)),
        "cv": f"{n_splits}-fold author-grouped stratified CV x {len(mc['seeds'])} seeds",
        "best_model": best,
        "overall": overall_df.round(4).to_dict("records"),
        "fairness_gaps": gaps_df.round(4).to_dict("records"),
        "min_group_n_for_model_metrics": mc["min_group_n"],
        "groups_insufficient_n": agg[(~agg["sufficient_n"]) & (agg["model"] == best)]["group"].tolist(),
    }
