"""Streamlit dashboard. Run with: streamlit run app.py"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import ROOT, load_config

CFG = load_config()
OUT = ROOT / "outputs"
TABLES, FIGS, REPORTS = OUT / "tables", OUT / "figures", OUT / "reports"

st.set_page_config(page_title="Age & Language Mental-Health Text Analysis", layout="wide")


def read_csv(name):
    p = TABLES / name
    if not p.exists():
        return None
    try:
        return pd.read_csv(p, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        return None


def show_fig(name, caption=None):
    p = FIGS / name
    if p.exists():
        st.image(str(p), caption=caption)


def load_summary():
    p = REPORTS / "analysis_summary.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def input_files():
    files = []
    for d in ("data/sample", "data/raw"):
        folder = ROOT / d
        if folder.exists():
            files += sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in folder.iterdir()
                            if p.suffix.lower() in (".csv", ".tsv", ".json", ".jsonl", ".xlsx"))
    return files


def run_pipeline(rel_path):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "main.py", "full", "--input", rel_path], cwd=ROOT, env=env,
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)


st.sidebar.title("Navigation")
page = st.sidebar.radio("Page", ["Overview", "Age analysis", "Language analysis", "Age x Language",
                                 "Model comparison", "Explainability", "Generative AI", "Limitations"])
st.sidebar.divider()
st.sidebar.subheader("Run on a dataset")
uploaded = st.sidebar.file_uploader("Upload your own file (csv, tsv, json, jsonl, xlsx)",
                                    type=["csv", "tsv", "json", "jsonl", "xlsx"])
uploaded_rel = None
if uploaded is not None:
    safe_name = Path(uploaded.name).name
    dest = ROOT / "data" / "raw" / safe_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(uploaded.getbuffer())
    uploaded_rel = f"data/raw/{safe_name}"
    st.sidebar.success(f"Saved {safe_name}. Press Run pipeline.")
files = input_files()
default_idx = files.index(uploaded_rel) if uploaded_rel in files else 0
if uploaded_rel is None:
    last = load_summary()
    last_sources = (last or {}).get("sources", [])
    for i, f in enumerate(files):
        if Path(f).name in last_sources:
            default_idx = i
            break
choice = st.sidebar.selectbox("Input file", files, index=default_idx) if files else None
if st.sidebar.button("Run pipeline", disabled=not choice):
    with st.spinner("Running (1-3 minutes)..."):
        res = run_pipeline(choice)
    if res.returncode == 0:
        st.sidebar.success("Done.")
    else:
        st.sidebar.error("Pipeline failed.")
        errs = [l for l in (res.stdout or "").splitlines() + (res.stderr or "").splitlines() if l.startswith("ERROR")]
        if errs:
            st.sidebar.warning(errs[0][:600])
    with st.sidebar.expander("Log"):
        st.code((res.stdout or "")[-3000:] + (res.stderr or "")[-2000:])
st.sidebar.caption("Research tool. Not a diagnostic or screening tool.")

summary = load_summary()
st.title("Age and Language-Based Mental Health Text Analysis")

if summary is None and page != "Limitations":
    st.info("No results yet. Pick a file in the sidebar and press 'Run pipeline'.")
    st.stop()

if summary and any(str(s).startswith("sample") for s in summary.get("sources", [])):
    st.warning("These results come from SYNTHETIC test data. They are not evidence about real people.")
if summary and any("proxy" in str(s) for s in summary.get("sources", [])):
    st.warning("Labels in this dataset are PROXIES (emotion tags or forum membership), not clinical status.")

if page == "Overview":
    st.subheader("Dataset overview")
    c = st.columns(3)
    c[0].metric("Posts after cleaning", summary["rows"])
    age = summary["age_analysis_O1_O2"]
    c[1].metric("Posts with reliable age", age.get("rows_with_age", 0))
    lang = summary["language_analysis_O3"]
    c[2].metric("Code-mixed / Romanized %", f"{lang['code_mixed_share_pct']:.1f}")
    st.write("Source file(s):", ", ".join(summary.get("sources", [])))
    rep = REPORTS / "cleaning_report.json"
    if rep.exists():
        st.subheader("Cleaning report")
        st.json(json.loads(rep.read_text(encoding="utf-8")))
    val = REPORTS / "data_validation.json"
    if val.exists():
        with st.expander("Validation profile"):
            st.json(json.loads(val.read_text(encoding="utf-8")))

elif page == "Age analysis":
    st.subheader("Age-wise text patterns and label distribution (O1, O2)")
    a = summary["age_analysis_O1_O2"]
    if a.get("status") != "ok":
        st.info(a.get("status", "Not available"))
    else:
        chi = a.get("label_vs_age_chi_square")
        if chi:
            st.write(f"Label vs age band: chi-square = {chi['chi2']:.2f}, p = {chi['p_value']:.4g}, "
                     f"Cramer's V = {chi['cramers_v']:.3f}. Small groups are flagged below.")
        if a.get("small_groups_below_min_n"):
            st.warning(f"Age bands with fewer than {CFG['analysis']['min_group_n']} posts: "
                       f"{', '.join(a['small_groups_below_min_n'])}")
        c1, c2 = st.columns(2)
        with c1:
            show_fig("age_label_distribution.png")
        with c2:
            show_fig("age_label_heatmap.png")
        t = read_csv("age_label_table.csv")
        if t is not None:
            st.caption("Label shares with 95% Wilson confidence intervals")
            st.dataframe(t.round(2))
        f = read_csv("age_text_features.csv")
        if f is not None:
            st.caption("Text features by age band (means)")
            st.dataframe(f)
        terms = read_csv("age_top_terms.csv")
        if terms is not None:
            st.caption("Terms over-represented in each age band (log-odds z-score)")
            st.dataframe(terms.round(2))

elif page == "Language analysis":
    st.subheader("Multilingual and code-mixed analysis (O3)")
    lang = summary["language_analysis_O3"]
    st.write("Language detection is a rule-based hint, not ground truth.")
    d = read_csv("language_distribution.csv")
    c1, c2 = st.columns(2)
    with c1:
        show_fig("language_label_distribution.png")
    with c2:
        show_fig("language_label_heatmap.png")
    if d is not None:
        st.dataframe(d.round(2))
    if lang.get("languages_below_min_n"):
        st.warning(f"Languages with too few posts: {', '.join(lang['languages_below_min_n'])}")
    cm = summary.get("codemixed_O3", {})
    st.subheader("Code-mixed normalization")
    if cm.get("status") == "ok":
        c = st.columns(3)
        c[0].metric("Romanized rows", cm["romanized_rows"])
        c[1].metric("Rows changed", cm["rows_changed_by_normalization"])
        c[2].metric("Vocabulary", f"{cm['vocab_before']} -> {cm['vocab_after']}")
        if "macro_f1_before_normalization" in cm:
            st.write(f"Macro-F1 before: {cm['macro_f1_before_normalization']:.3f} | "
                     f"after: {cm['macro_f1_after_normalization']:.3f}")
        ex = read_csv("codemixed_examples.csv")
        if ex is not None:
            st.caption("Examples (raw text; disable with codemixed.save_examples=false for real data)")
            st.dataframe(ex)
    else:
        st.info(cm.get("status", "Not available"))

elif page == "Age x Language":
    st.subheader("Combined age-and-language analysis (O4)")
    comb = summary["age_language_O4"]
    if comb.get("status") != "ok":
        st.info(comb.get("status"))
    else:
        st.write(f"{comb['cells_below_min_n']} of {comb['cells_total']} cells have fewer than "
                 f"{CFG['analysis']['min_group_n']} posts and are hidden as 'insufficient evidence'.")
        c1, c2 = st.columns(2)
        with c1:
            show_fig("age_language_counts.png")
        with c2:
            show_fig("age_language_elevated_pct.png")

elif page == "Model comparison":
    st.subheader("Models overall and per group (O5)")
    m = summary["models_O5"]
    if m.get("status") != "ok":
        st.info(m.get("status"))
    else:
        st.write(f"Validation: {m['cv']}. Best model: **{m['best_model']}**.")
        ov = read_csv("model_comparison_overall.csv")
        if ov is not None:
            st.dataframe(ov.round(3))
        c1, c2 = st.columns(2)
        with c1:
            show_fig("confusion_matrix_best_model.png")
        with c2:
            show_fig("model_macro_f1_age_language.png")
        g = read_csv("model_group_metrics.csv")
        if g is not None:
            gt = st.selectbox("Group type", sorted(g["group_type"].unique()))
            show = g[g["group_type"] == gt]
            only_ok = st.checkbox("Only groups with enough data", value=True)
            if only_ok:
                show = show[show["sufficient_n"]]
            st.dataframe(show.round(3))
        gaps = read_csv("model_fairness_gaps.csv")
        if gaps is not None and not gaps.empty:
            st.caption("Fairness gaps: largest macro-F1 / recall difference between groups with enough data")
            st.dataframe(gaps.round(3))
        else:
            st.info("No fairness gaps to show: fewer than two groups have enough data for comparison.")

elif page == "Explainability":
    st.subheader("Which words push the model toward each label")
    st.write("This shows model behaviour only, not the cause of anyone's mental state. "
             "Single words are not evidence of a condition.")
    e = read_csv("explain_top_features.csv")
    if e is None:
        st.info("Run the pipeline first.")
    else:
        lab = st.selectbox("Label", list(e["label"].unique()))
        st.dataframe(e[e["label"] == lab].round(3))

elif page == "Generative AI":
    st.subheader("Age-wise insights (O6)")
    p = REPORTS / "genai_age_insights.md"
    if p.exists():
        st.markdown(p.read_text(encoding="utf-8"))
        g = REPORTS / "genai_age_insights_guardrail.json"
        if g.exists():
            guard = json.loads(g.read_text(encoding="utf-8"))["guardrail"]
            st.caption(f"Source: {guard['source']} | numbers verified: {guard['numbers']['ok']} | "
                       f"safety check: {guard['safety']['ok']}")
    else:
        st.info("Run `python main.py genai` to create it.")
    st.subheader("Multilingual awareness content (O7)")
    aw = REPORTS / "awareness_content.json"
    if aw.exists():
        items = json.loads(aw.read_text(encoding="utf-8"))["items"]
        st.error("Not reviewed. Do not publish until a native speaker and a qualified reviewer approve it "
                 "and the helpline placeholder is replaced.")
        lang = st.selectbox("Language", sorted({i["language"] for i in items}))
        for it in [i for i in items if i["language"] == lang]:
            with st.expander(f"{it['audience'].replace('_', ' ')} ({it['review_status']})"):
                st.write(it["text"])
                st.caption(it["disclaimer"])

else:
    st.subheader("Limitations and responsible use")
    st.markdown("""
- This is a **research and educational tool**. It is not a diagnostic or screening tool and must not be used for decisions about individuals.
- Labels may be **proxies** (emotion tags, forum membership, survey screening bands) and do not equal clinical diagnoses.
- Age is only used when it is explicitly provided or stated by the author. It is never inferred from writing.
- Language detection is a rule-based hint and can be wrong, especially for Romanized and code-mixed text.
- Groups with few posts are flagged; do not over-interpret them. Results can reflect sampling bias (for example Reddit users).
- Generative AI text is produced from aggregated statistics only, checked for unsupported numbers, and needs human review.
- If you or someone you know is in distress, contact a qualified professional or a local emergency/helpline service.
""")
