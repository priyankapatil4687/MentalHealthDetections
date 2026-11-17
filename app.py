# """Streamlit dashboard. Run with: streamlit run app.py"""
# import json
# import os
# import subprocess
# import sys
# from pathlib import Path

# import pandas as pd
# import streamlit as st

# from src.config import ROOT, load_config

# CFG = load_config()
# OUT = ROOT / "outputs"
# TABLES, FIGS, REPORTS = OUT / "tables", OUT / "figures", OUT / "reports"

# st.set_page_config(page_title="Age & Language Mental-Health Text Analysis", layout="wide")


# def read_csv(name):
#     p = TABLES / name
#     if not p.exists():
#         return None
#     try:
#         return pd.read_csv(p, encoding="utf-8-sig")
#     except pd.errors.EmptyDataError:
#         return None


# def show_fig(name, caption=None):
#     p = FIGS / name
#     if p.exists():
#         st.image(str(p), caption=caption)


# def load_summary():
#     p = REPORTS / "analysis_summary.json"
#     return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


# def input_files():
#     files = []
#     for d in ("data/sample", "data/raw"):
#         folder = ROOT / d
#         if folder.exists():
#             files += sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in folder.iterdir()
#                             if p.suffix.lower() in (".csv", ".tsv", ".json", ".jsonl", ".xlsx"))
#     return files


# def run_pipeline(rel_path):
#     env = dict(os.environ, PYTHONIOENCODING="utf-8")
#     return subprocess.run([sys.executable, "main.py", "full", "--input", rel_path], cwd=ROOT, env=env,
#                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)


# st.sidebar.title("Navigation")
# page = st.sidebar.radio("Page", ["Overview", "Age analysis", "Language analysis", "Age x Language",
#                                  "Model comparison", "Explainability", "Generative AI", "Limitations"])
# st.sidebar.divider()
# st.sidebar.subheader("Run on a dataset")
# uploaded = st.sidebar.file_uploader("Upload your own file (csv, tsv, json, jsonl, xlsx)",
#                                     type=["csv", "tsv", "json", "jsonl", "xlsx"])
# uploaded_rel = None
# if uploaded is not None:
#     safe_name = Path(uploaded.name).name
#     dest = ROOT / "data" / "raw" / safe_name
#     dest.parent.mkdir(parents=True, exist_ok=True)
#     dest.write_bytes(uploaded.getbuffer())
#     uploaded_rel = f"data/raw/{safe_name}"
#     st.sidebar.success(f"Saved {safe_name}. Press Run pipeline.")
# files = input_files()
# default_idx = files.index(uploaded_rel) if uploaded_rel in files else 0
# if uploaded_rel is None:
#     last = load_summary()
#     last_sources = (last or {}).get("sources", [])
#     for i, f in enumerate(files):
#         if Path(f).name in last_sources:
#             default_idx = i
#             break
# choice = st.sidebar.selectbox("Input file", files, index=default_idx) if files else None
# if st.sidebar.button("Run pipeline", disabled=not choice):
#     with st.spinner("Running (1-3 minutes)..."):
#         res = run_pipeline(choice)
#     if res.returncode == 0:
#         st.sidebar.success("Done.")
#     else:
#         st.sidebar.error("Pipeline failed.")
#         errs = [l for l in (res.stdout or "").splitlines() + (res.stderr or "").splitlines() if l.startswith("ERROR")]
#         if errs:
#             st.sidebar.warning(errs[0][:600])
#     with st.sidebar.expander("Log"):
#         st.code((res.stdout or "")[-3000:] + (res.stderr or "")[-2000:])
# st.sidebar.caption("Research tool. Not a diagnostic or screening tool.")

# summary = load_summary()
# st.title("Age and Language-Based Mental Health Text Analysis")

# if summary is None and page != "Limitations":
#     st.info("No results yet. Pick a file in the sidebar and press 'Run pipeline'.")
#     st.stop()

# if summary and any(str(s).startswith("sample") for s in summary.get("sources", [])):
#     st.warning("These results come from SYNTHETIC test data. They are not evidence about real people.")
# if summary and any("proxy" in str(s) for s in summary.get("sources", [])):
#     st.warning("Labels in this dataset are PROXIES (emotion tags or forum membership), not clinical status.")

# if page == "Overview":
#     st.subheader("Dataset overview")
#     c = st.columns(3)
#     c[0].metric("Posts after cleaning", summary["rows"])
#     age = summary["age_analysis_O1_O2"]
#     c[1].metric("Posts with reliable age", age.get("rows_with_age", 0))
#     lang = summary["language_analysis_O3"]
#     c[2].metric("Code-mixed / Romanized %", f"{lang['code_mixed_share_pct']:.1f}")
#     st.write("Source file(s):", ", ".join(summary.get("sources", [])))
#     rep = REPORTS / "cleaning_report.json"
#     if rep.exists():
#         st.subheader("Cleaning report")
#         st.json(json.loads(rep.read_text(encoding="utf-8")))
#     val = REPORTS / "data_validation.json"
#     if val.exists():
#         with st.expander("Validation profile"):
#             st.json(json.loads(val.read_text(encoding="utf-8")))

# elif page == "Age analysis":
#     st.subheader("Age-wise text patterns and label distribution (O1, O2)")
#     a = summary["age_analysis_O1_O2"]
#     if a.get("status") != "ok":
#         st.info(a.get("status", "Not available"))
#     else:
#         chi = a.get("label_vs_age_chi_square")
#         if chi:
#             st.write(f"Label vs age band: chi-square = {chi['chi2']:.2f}, p = {chi['p_value']:.4g}, "
#                      f"Cramer's V = {chi['cramers_v']:.3f}. Small groups are flagged below.")
#         if a.get("small_groups_below_min_n"):
#             st.warning(f"Age bands with fewer than {CFG['analysis']['min_group_n']} posts: "
#                        f"{', '.join(a['small_groups_below_min_n'])}")
#         c1, c2 = st.columns(2)
#         with c1:
#             show_fig("age_label_distribution.png")
#         with c2:
#             show_fig("age_label_heatmap.png")
#         t = read_csv("age_label_table.csv")
#         if t is not None:
#             st.caption("Label shares with 95% Wilson confidence intervals")
#             st.dataframe(t.round(2))
#         f = read_csv("age_text_features.csv")
#         if f is not None:
#             st.caption("Text features by age band (means)")
#             st.dataframe(f)
#         terms = read_csv("age_top_terms.csv")
#         if terms is not None:
#             st.caption("Terms over-represented in each age band (log-odds z-score)")
#             st.dataframe(terms.round(2))

# elif page == "Language analysis":
#     st.subheader("Multilingual and code-mixed analysis (O3)")
#     lang = summary["language_analysis_O3"]
#     st.write("Language detection is a rule-based hint, not ground truth.")
#     d = read_csv("language_distribution.csv")
#     c1, c2 = st.columns(2)
#     with c1:
#         show_fig("language_label_distribution.png")
#     with c2:
#         show_fig("language_label_heatmap.png")
#     if d is not None:
#         st.dataframe(d.round(2))
#     if lang.get("languages_below_min_n"):
#         st.warning(f"Languages with too few posts: {', '.join(lang['languages_below_min_n'])}")
#     cm = summary.get("codemixed_O3", {})
#     st.subheader("Code-mixed normalization")
#     if cm.get("status") == "ok":
#         c = st.columns(3)
#         c[0].metric("Romanized rows", cm["romanized_rows"])
#         c[1].metric("Rows changed", cm["rows_changed_by_normalization"])
#         c[2].metric("Vocabulary", f"{cm['vocab_before']} -> {cm['vocab_after']}")
#         if "macro_f1_before_normalization" in cm:
#             st.write(f"Macro-F1 before: {cm['macro_f1_before_normalization']:.3f} | "
#                      f"after: {cm['macro_f1_after_normalization']:.3f}")
#         ex = read_csv("codemixed_examples.csv")
#         if ex is not None:
#             st.caption("Examples (raw text; disable with codemixed.save_examples=false for real data)")
#             st.dataframe(ex)
#     else:
#         st.info(cm.get("status", "Not available"))

# elif page == "Age x Language":
#     st.subheader("Combined age-and-language analysis (O4)")
#     comb = summary["age_language_O4"]
#     if comb.get("status") != "ok":
#         st.info(comb.get("status"))
#     else:
#         st.write(f"{comb['cells_below_min_n']} of {comb['cells_total']} cells have fewer than "
#                  f"{CFG['analysis']['min_group_n']} posts and are hidden as 'insufficient evidence'.")
#         c1, c2 = st.columns(2)
#         with c1:
#             show_fig("age_language_counts.png")
#         with c2:
#             show_fig("age_language_elevated_pct.png")

# elif page == "Model comparison":
#     st.subheader("Models overall and per group (O5)")
#     m = summary["models_O5"]
#     if m.get("status") != "ok":
#         st.info(m.get("status"))
#     else:
#         st.write(f"Validation: {m['cv']}. Best model: **{m['best_model']}**.")
#         ov = read_csv("model_comparison_overall.csv")
#         if ov is not None:
#             st.dataframe(ov.round(3))
#         c1, c2 = st.columns(2)
#         with c1:
#             show_fig("confusion_matrix_best_model.png")
#         with c2:
#             show_fig("model_macro_f1_age_language.png")
#         g = read_csv("model_group_metrics.csv")
#         if g is not None:
#             gt = st.selectbox("Group type", sorted(g["group_type"].unique()))
#             show = g[g["group_type"] == gt]
#             only_ok = st.checkbox("Only groups with enough data", value=True)
#             if only_ok:
#                 show = show[show["sufficient_n"]]
#             st.dataframe(show.round(3))
#         gaps = read_csv("model_fairness_gaps.csv")
#         if gaps is not None and not gaps.empty:
#             st.caption("Fairness gaps: largest macro-F1 / recall difference between groups with enough data")
#             st.dataframe(gaps.round(3))
#         else:
#             st.info("No fairness gaps to show: fewer than two groups have enough data for comparison.")

# elif page == "Explainability":
#     st.subheader("Which words push the model toward each label")
#     st.write("This shows model behaviour only, not the cause of anyone's mental state. "
#              "Single words are not evidence of a condition.")
#     e = read_csv("explain_top_features.csv")
#     if e is None:
#         st.info("Run the pipeline first.")
#     else:
#         lab = st.selectbox("Label", list(e["label"].unique()))
#         st.dataframe(e[e["label"] == lab].round(3))

# elif page == "Generative AI":
#     st.subheader("Age-wise insights (O6)")
#     p = REPORTS / "genai_age_insights.md"
#     if p.exists():
#         st.markdown(p.read_text(encoding="utf-8"))
#         g = REPORTS / "genai_age_insights_guardrail.json"
#         if g.exists():
#             guard = json.loads(g.read_text(encoding="utf-8"))["guardrail"]
#             st.caption(f"Source: {guard['source']} | numbers verified: {guard['numbers']['ok']} | "
#                        f"safety check: {guard['safety']['ok']}")
#     else:
#         st.info("Run `python main.py genai` to create it.")
#     st.subheader("Multilingual awareness content (O7)")
#     aw = REPORTS / "awareness_content.json"
#     if aw.exists():
#         items = json.loads(aw.read_text(encoding="utf-8"))["items"]
#         st.error("Not reviewed. Do not publish until a native speaker and a qualified reviewer approve it "
#                  "and the helpline placeholder is replaced.")
#         lang = st.selectbox("Language", sorted({i["language"] for i in items}))
#         for it in [i for i in items if i["language"] == lang]:
#             with st.expander(f"{it['audience'].replace('_', ' ')} ({it['review_status']})"):
#                 st.write(it["text"])
#                 st.caption(it["disclaimer"])

# else:
#     st.subheader("Limitations and responsible use")
#     st.markdown("""
# - This is a **research and educational tool**. It is not a diagnostic or screening tool and must not be used for decisions about individuals.
# - Labels may be **proxies** (emotion tags, forum membership, survey screening bands) and do not equal clinical diagnoses.
# - Age is only used when it is explicitly provided or stated by the author. It is never inferred from writing.
# - Language detection is a rule-based hint and can be wrong, especially for Romanized and code-mixed text.
# - Groups with few posts are flagged; do not over-interpret them. Results can reflect sampling bias (for example Reddit users).
# - Generative AI text is produced from aggregated statistics only, checked for unsupported numbers, and needs human review.
# - If you or someone you know is in distress, contact a qualified professional or a local emergency/helpline service.
# """)



"""Streamlit dashboard. Run with: streamlit run app.py"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import ROOT, load_config

# Ollama is optional for the other dashboard pages.
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    ollama = None
    OLLAMA_AVAILABLE = False


CFG = load_config()
OUT = ROOT / "outputs"
TABLES = OUT / "tables"
FIGS = OUT / "figures"
REPORTS = OUT / "reports"

LLM_MODEL = "llama3.2"

st.set_page_config(
    page_title="Age & Language Mental-Health Text Analysis",
    layout="wide"
)


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def read_csv(name):
    path = TABLES / name

    if not path.exists():
        return None

    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        return None


def show_fig(name, caption=None):
    path = FIGS / name

    if path.exists():
        st.image(str(path), caption=caption)


def load_summary():
    path = REPORTS / "analysis_summary.json"

    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        st.error(f"Could not read analysis summary: {exc}")
        return None


def input_files():
    files = []

    for folder_name in ("data/sample", "data/raw"):
        folder = ROOT / folder_name

        if folder.exists():
            files += sorted(
                str(p.relative_to(ROOT)).replace("\\", "/")
                for p in folder.iterdir()
                if p.suffix.lower() in (
                    ".csv", ".tsv", ".json", ".jsonl", ".xlsx"
                )
            )

    return files


def run_pipeline(rel_path):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")

    return subprocess.run(
        [
            sys.executable,
            "main.py",
            "full",
            "--input",
            rel_path
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=900
    )


# ---------------------------------------------------------
# GENERATIVE AI + LLM FUNCTION
# ---------------------------------------------------------

def generate_genai_insights(analysis_summary):

    if not OLLAMA_AVAILABLE:
        raise RuntimeError(
            "Ollama package is missing. "
            "Install it using: python -m pip install ollama"
        )

    # Only aggregate ML results are passed to the LLM.
    ml_results = {
        "age_analysis": analysis_summary.get(
            "age_analysis_O1_O2", {}
        ),
        "language_analysis": analysis_summary.get(
            "language_analysis_O3", {}
        ),
        "age_language_analysis": analysis_summary.get(
            "age_language_O4", {}
        ),
        "model_comparison": analysis_summary.get(
            "models_O5", {}
        ),
        "code_mixed_analysis": analysis_summary.get(
            "codemixed_O3", {}
        )
    }

    results_json = json.dumps(
        ml_results,
        indent=2,
        ensure_ascii=False,
        default=str
    )

    prompt = f"""
You are an academic research assistant.

Project:
Age and Language-Based Mental Health Text Analysis
using Machine Learning and Generative AI.

Analyze these aggregate machine-learning results:

{results_json}

Generate a report using these headings:

1. Age-wise observations
2. Language-wise observations
3. Combined age and language observations
4. Machine-learning model comparison
5. Code-mixed language observations
6. Research limitations
7. Overall conclusion

IMPORTANT RULES:

- Use only the information provided above.
- Never invent statistics or percentages.
- If information is unavailable, mention that clearly.
- Do not diagnose any person.
- Do not provide medical advice.
- Do not claim that age or language causes a condition.
- Explain that dataset labels may be proxies, not clinical diagnoses.
- Use simple English suitable for a student project presentation.
"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful academic research assistant. "
                    "Follow the provided data and safety instructions."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Page",
    [
        "Overview",
        "Age analysis",
        "Language analysis",
        "Age x Language",
        "Model comparison",
        "Explainability",
        "Generative AI",
        "Limitations"
    ]
)

st.sidebar.divider()
st.sidebar.subheader("Run on a dataset")

uploaded = st.sidebar.file_uploader(
    "Upload your own file",
    type=["csv", "tsv", "json", "jsonl", "xlsx"]
)

uploaded_rel = None

if uploaded is not None:
    safe_name = Path(uploaded.name).name
    destination = ROOT / "data" / "raw" / safe_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(uploaded.getbuffer())

    uploaded_rel = f"data/raw/{safe_name}"
    st.sidebar.success(
        f"Saved {safe_name}. Press Run pipeline."
    )

files = input_files()
default_idx = files.index(uploaded_rel) if uploaded_rel in files else 0

if uploaded_rel is None:
    last_summary = load_summary()
    last_sources = (last_summary or {}).get("sources", [])

    for i, file_name in enumerate(files):
        if Path(file_name).name in last_sources:
            default_idx = i
            break

choice = (
    st.sidebar.selectbox("Input file", files, index=default_idx)
    if files else None
)

if st.sidebar.button("Run pipeline", disabled=not choice):

    try:
        with st.spinner("Running analysis..."):
            result = run_pipeline(choice)

        if result.returncode == 0:
            st.sidebar.success("Pipeline completed.")
            st.rerun()
        else:
            st.sidebar.error("Pipeline failed.")

            errors = [
                line
                for line in (
                    (result.stdout or "").splitlines()
                    + (result.stderr or "").splitlines()
                )
                if line.startswith("ERROR")
            ]

            if errors:
                st.sidebar.warning(errors[0][:600])

        with st.sidebar.expander("Pipeline log"):
            st.code(
                (result.stdout or "")[-3000:]
                + (result.stderr or "")[-2000:]
            )

    except subprocess.TimeoutExpired:
        st.sidebar.error("Pipeline timed out.")
    except Exception as exc:
        st.sidebar.error(f"Pipeline error: {exc}")

st.sidebar.caption(
    "Research tool. Not a diagnostic or screening tool."
)


# ---------------------------------------------------------
# LOAD ANALYSIS RESULTS
# ---------------------------------------------------------

summary = load_summary()

st.title("Age and Language-Based Mental Health Text Analysis")

if summary is None and page != "Limitations":
    st.info(
        "No results yet. Select a dataset and press "
        "'Run pipeline' in the sidebar."
    )
    st.stop()

if summary and any(
    str(s).startswith("sample")
    for s in summary.get("sources", [])
):
    st.warning(
        "These results come from SYNTHETIC test data. "
        "They are not evidence about real people."
        
    )

if summary and any(
    "proxy" in str(s).lower()
    for s in summary.get("sources", [])
):
    st.warning(
        "Dataset labels may be proxies, not clinical status."
    )


# ---------------------------------------------------------
# 1. OVERVIEW
# ---------------------------------------------------------

if page == "Overview":

    st.subheader("Dataset overview")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Posts after cleaning",
        summary.get("rows", 0)
    )

    age = summary.get("age_analysis_O1_O2", {})

    c2.metric(
        "Posts with reliable age",
        age.get("rows_with_age", 0)
    )

    lang = summary.get("language_analysis_O3", {})
    code_mixed_share = lang.get("code_mixed_share_pct")

    c3.metric(
        "Code-mixed / Romanized %",
        (
            f"{code_mixed_share:.1f}"
            if isinstance(code_mixed_share, (int, float))
            else "Not available"
        )
    )

    st.write(
        "Source file(s):",
        ", ".join(summary.get("sources", []))
    )

    report = REPORTS / "cleaning_report.json"

    if report.exists():
        st.subheader("Cleaning report")
        st.json(
            json.loads(report.read_text(encoding="utf-8"))
        )

    validation = REPORTS / "data_validation.json"

    if validation.exists():
        with st.expander("Validation profile"):
            st.json(
                json.loads(validation.read_text(encoding="utf-8"))
            )


# ---------------------------------------------------------
# 2. AGE ANALYSIS
# ---------------------------------------------------------

elif page == "Age analysis":

    st.subheader(
        "Age-wise text patterns and label distribution (O1, O2)"
    )

    a = summary["age_analysis_O1_O2"]

    if a.get("status") != "ok":
        st.info(a.get("status", "Not available"))

    else:
        chi = a.get("label_vs_age_chi_square")

        if chi:
            st.write(
                f"Label vs age band: chi-square = {chi['chi2']:.2f}, "
                f"p = {chi['p_value']:.4g}, "
                f"Cramer's V = {chi['cramers_v']:.3f}."
            )

        if a.get("small_groups_below_min_n"):
            st.warning(
                "Age bands with fewer than "
                f"{CFG['analysis']['min_group_n']} posts: "
                + ", ".join(a["small_groups_below_min_n"])
            )

        c1, c2 = st.columns(2)

        with c1:
            show_fig("age_label_distribution.png")

        with c2:
            show_fig("age_label_heatmap.png")

        table = read_csv("age_label_table.csv")

        if table is not None:
            st.caption(
                "Label shares with 95% Wilson confidence intervals"
            )
            st.dataframe(table.round(2))

        features = read_csv("age_text_features.csv")

        if features is not None:
            st.caption("Text features by age band")
            st.dataframe(features)

        terms = read_csv("age_top_terms.csv")

        if terms is not None:
            st.caption("Terms over-represented in each age band")
            st.dataframe(terms.round(2))


# ---------------------------------------------------------
# 3. LANGUAGE ANALYSIS
# ---------------------------------------------------------

elif page == "Language analysis":

    st.subheader("Multilingual and code-mixed analysis (O3)")

    st.write(
        "Language detection is a rule-based hint, not ground truth."
    )

    d = read_csv("language_distribution.csv")

    c1, c2 = st.columns(2)

    with c1:
        show_fig("language_label_distribution.png")

    with c2:
        show_fig("language_label_heatmap.png")

    if d is not None:
        st.dataframe(d.round(2))

    lang = summary["language_analysis_O3"]

    if lang.get("languages_below_min_n"):
        st.warning(
            "Languages with too few posts: "
            + ", ".join(lang["languages_below_min_n"])
        )

    cm = summary.get("codemixed_O3", {})

    st.subheader("Code-mixed normalization")

    if cm.get("status") == "ok":

        c1, c2, c3 = st.columns(3)

        c1.metric("Romanized rows", cm["romanized_rows"])
        c2.metric(
            "Rows changed",
            cm["rows_changed_by_normalization"]
        )
        c3.metric(
            "Vocabulary",
            f"{cm['vocab_before']} -> {cm['vocab_after']}"
        )

        if "macro_f1_before_normalization" in cm:
            st.write(
                f"Macro-F1 before: "
                f"{cm['macro_f1_before_normalization']:.3f} | "
                f"after: {cm['macro_f1_after_normalization']:.3f}"
            )

        examples = read_csv("codemixed_examples.csv")

        if examples is not None:
            st.caption("Code-mixed examples")
            st.dataframe(examples)

    else:
        st.info(cm.get("status", "Not available"))


# ---------------------------------------------------------
# 4. AGE + LANGUAGE ANALYSIS
# ---------------------------------------------------------

elif page == "Age x Language":

    st.subheader("Combined age-and-language analysis (O4)")

    comb = summary["age_language_O4"]

    if comb.get("status") != "ok":
        st.info(comb.get("status", "Not available"))

    else:
        st.write(
            f"{comb['cells_below_min_n']} of "
            f"{comb['cells_total']} cells have fewer than "
            f"{CFG['analysis']['min_group_n']} posts."
        )

        c1, c2 = st.columns(2)

        with c1:
            show_fig("age_language_counts.png")

        with c2:
            show_fig("age_language_elevated_pct.png")


# ---------------------------------------------------------
# 5. MODEL COMPARISON
# ---------------------------------------------------------

elif page == "Model comparison":

    st.subheader("Models overall and per group (O5)")

    m = summary["models_O5"]

    if m.get("status") != "ok":
        st.info(m.get("status", "Not available"))

    else:
        st.write(
            f"Validation: {m['cv']}. "
            f"Best model: **{m['best_model']}**."
        )

        overall = read_csv("model_comparison_overall.csv")

        if overall is not None:
            st.dataframe(overall.round(3))

        c1, c2 = st.columns(2)

        with c1:
            show_fig("confusion_matrix_best_model.png")

        with c2:
            show_fig("model_macro_f1_age_language.png")

        groups = read_csv("model_group_metrics.csv")

        if groups is not None:
            gt = st.selectbox(
                "Group type",
                sorted(groups["group_type"].unique())
            )

            show = groups[groups["group_type"] == gt]

            only_ok = st.checkbox(
                "Only groups with enough data",
                value=True
            )

            if only_ok:
                show = show[show["sufficient_n"]]

            st.dataframe(show.round(3))

        gaps = read_csv("model_fairness_gaps.csv")

        if gaps is not None and not gaps.empty:
            st.caption(
                "Fairness gaps: largest macro-F1 / recall difference "
                "between groups with enough data"
            )
            st.dataframe(gaps.round(3))
        else:
            st.info(
                "No fairness gaps to show: insufficient group data."
            )


# ---------------------------------------------------------
# 6. EXPLAINABILITY
# ---------------------------------------------------------

elif page == "Explainability":

    st.subheader(
        "Which words push the model toward each label"
    )

    st.write(
        "This shows model behaviour only, not the cause of "
        "anyone's mental state. Single words are not evidence "
        "of a condition."
    )

    e = read_csv("explain_top_features.csv")

    if e is None:
        st.info("Run the pipeline first.")

    else:
        lab = st.selectbox(
            "Label",
            list(e["label"].unique())
        )

        st.dataframe(
            e[e["label"] == lab].round(3)
        )


# ---------------------------------------------------------
# 7. GENERATIVE AI + LLM
# ---------------------------------------------------------

elif page == "Generative AI":

    st.subheader("Generative AI Insights using Llama 3.2")

    st.write(
        "The Large Language Model explains the aggregate results "
        "generated by your machine-learning pipeline."
    )

    st.info(
        "Only aggregate analysis results are passed to the local LLM. "
        "Raw social-media posts and usernames are not sent."
    )

    if not OLLAMA_AVAILABLE:

        st.warning(
            "Ollama Python package is not installed. "
            "Run: python -m pip install ollama"
        )

    else:

        if st.button(
            "Generate AI Insights",
            type="primary"
        ):

            try:
                with st.spinner(
                    "Llama 3.2 is generating your report..."
                ):

                    result = generate_genai_insights(summary)

                REPORTS.mkdir(
                    parents=True,
                    exist_ok=True
                )

                report_path = REPORTS / "genai_age_insights.md"

                report_path.write_text(
                    result,
                    encoding="utf-8"
                )

                st.success(
                    "AI insights generated successfully!"
                )

                st.rerun()

            except Exception as exc:

                st.error(
                    f"Error generating AI insights: {exc}"
                )

                st.write(
                    "Check that Ollama is installed, running, "
                    "and that the Llama 3.2 model is downloaded."
                )

    st.divider()

    st.subheader("AI Generated Research Report")

    report_path = REPORTS / "genai_age_insights.md"

    if report_path.exists():

        report = report_path.read_text(
            encoding="utf-8"
        )

        st.markdown(report)

        st.download_button(
            "Download AI Report",
            data=report,
            file_name="genai_age_insights.md",
            mime="text/markdown"
        )

    else:

        st.info(
            "Click Generate AI Insights to create the report."
        )

    st.warning(
        "This is an educational research output, not a medical "
        "diagnosis. Human review is required."
    )

    st.divider()

    st.subheader("Multilingual Awareness Content (O7)")

    awareness_file = REPORTS / "awareness_content.json"

    if awareness_file.exists():

        try:
            items = json.loads(
                awareness_file.read_text(
                    encoding="utf-8"
                )
            ).get("items", [])

            if items:

                st.error(
                    "Not reviewed. Do not publish until a native "
                    "speaker and qualified reviewer approve it."
                )

                languages = sorted({
                    item["language"]
                    for item in items
                })

                selected_language = st.selectbox(
                    "Language",
                    languages
                )

                for item in items:

                    if item["language"] == selected_language:

                        with st.expander(
                            item["audience"].replace("_", " ")
                            + " ("
                            + item["review_status"]
                            + ")"
                        ):

                            st.write(item["text"])
                            st.caption(item["disclaimer"])

            else:
                st.info("No awareness content items found.")

        except (json.JSONDecodeError, OSError) as exc:
            st.error(
                f"Could not read awareness content: {exc}"
            )

    else:

        st.info(
            "No multilingual awareness content file is available. "
            "This section displays existing content; it does not "
            "generate new awareness content."
        )


# ---------------------------------------------------------
# 8. LIMITATIONS
# ---------------------------------------------------------

elif page == "Limitations":

    st.subheader("Limitations and Responsible Use")

    st.markdown("""
- This is a **research and educational tool**. It is not a diagnostic
  or screening tool.
- Labels may be **proxies** (emotion tags, forum membership, survey
  screening bands) and do not equal clinical diagnoses.
- Age is only used when it is explicitly provided. It is never inferred
  from writing.
- Language detection is a rule-based hint and can be wrong, especially
  for Romanized and code-mixed text.
- Groups with few posts are flagged. Do not over-interpret them.
- Results can reflect sampling bias.
- Generative AI text is produced from aggregate statistics only.
  It can still contain errors and needs human review.
- If someone is in distress, contact a qualified professional or a
  local emergency/helpline service.
""")

elif page == "Limitations":

    st.subheader("Limitations and Responsible Use")

    # Read current dataset summary
    sources = summary.get("sources", []) if summary else []
    total_rows = summary.get("rows", 0) if summary else 0

    age = summary.get("age_analysis_O1_O2", {}) if summary else {}
    lang = summary.get("language_analysis_O3", {}) if summary else {}
    combined = summary.get("age_language_O4", {}) if summary else {}
    models = summary.get("models_O5", {}) if summary else {}
    cm = summary.get("codemixed_O3", {}) if summary else {}

    # Detect sample or synthetic data from source filename
    source_names = [Path(str(s)).name.lower() for s in sources]
    is_synthetic = any(
        "synthetic" in name or name.startswith("sample")
        for name in source_names
    )

    st.subheader("Dataset-specific limitations")

    if is_synthetic:
        st.warning(
            "Sample/Synthetic dataset detected. "
            "Results are for testing and are not evidence about real people."
        )
    else:
        st.info(
            "Dataset is not identified as synthetic by its filename. "
            "Verify its origin and authenticity before drawing conclusions."
        )

    st.write(f"**Dataset sources:** {', '.join(map(str, sources)) or 'Not available'}")
    st.write(f"**Total posts:** {total_rows}")

    if total_rows < 100:
        st.warning("Small dataset: results may be unstable.")

    # Age limitations
    st.subheader("Age analysis limitations")

    age_rows = age.get("rows_with_age", 0)
    st.write(f"Posts with age information: {age_rows} / {total_rows}")

    if age.get("status") != "ok":
        st.warning("Age analysis is unavailable.")
    elif age_rows < total_rows:
        st.warning("Some posts do not have age information.")
    else:
        st.success("Age information is available for all posts.")

    small_age = age.get("small_groups_below_min_n", [])
    if small_age:
        st.warning(
            "Age groups with insufficient data: "
            + ", ".join(map(str, small_age))
        )

    # Statistical interpretation
    age_test = age.get("label_vs_age_chi_square", {})
    adjusted_p = age.get("fdr_adjusted_p", {}).get("label_vs_age")

    if age_test.get("p_value") is not None:
        st.write(
            f"Age-label association p-value: "
            f"{age_test['p_value']:.4f}"
        )

    if adjusted_p is not None:
        st.write(f"FDR-adjusted p-value: {adjusted_p:.4f}")
        if adjusted_p >= 0.05:
            st.warning(
                "After multiple-testing correction, the age-label "
                "association is not statistically significant at 0.05."
            )

    # Language limitations
    st.subheader("Language analysis limitations")

    if lang.get("status") != "ok":
        st.warning("Language analysis is unavailable.")

    small_languages = lang.get("languages_below_min_n", [])
    if small_languages:
        st.warning(
            "Languages with insufficient data: "
            + ", ".join(map(str, small_languages))
        )

    code_mixed_pct = lang.get("code_mixed_share_pct")

    if isinstance(code_mixed_pct, (int, float)):
        st.write(f"Code-mixed / Romanized text: {code_mixed_pct:.1f}%")

        if code_mixed_pct > 0:
            st.warning(
                "Code-mixed and Romanized text may reduce "
                "language detection accuracy."
            )

    st.info(
        "Language detection is a rule-based hint, not ground truth."
    )

    # Combined age-language limitations
    st.subheader("Age and Language combined analysis")

    cells_total = combined.get("cells_total", 0)
    cells_below = combined.get("cells_below_min_n", 0)

    if combined.get("status") != "ok":
        st.warning("Combined age-language analysis is unavailable.")
    else:
        st.write(
            f"Groups with insufficient data: "
            f"{cells_below} / {cells_total}"
        )

        if cells_below > 0:
            st.warning(
                "Many age-language combinations have insufficient data. "
                "Avoid strong conclusions about these groups."
            )

    # Model limitations
    st.subheader("Machine Learning model limitations")

    if models.get("status") != "ok":
        st.warning("Model comparison is unavailable.")
    else:
        st.write(f"Best model: {models.get('best_model', 'Not available')}")

        overall = models.get("overall", [])
        best_name = models.get("best_model")

        best_result = next(
            (m for m in overall if m.get("model") == best_name),
            None
        )

        if best_result:
            st.write(
                f"Accuracy: "
                f"{best_result.get('accuracy_mean', 0) * 100:.2f}%"
            )
            st.write(
                f"Macro F1-score: "
                f"{best_result.get('macro_f1_mean', 0) * 100:.2f}%"
            )

        insufficient = models.get("groups_insufficient_n", [])
        if insufficient:
            st.warning(
                f"{len(insufficient)} groups have insufficient samples "
                "for reliable group-level model evaluation."
            )

    # Code-mixed normalization
    if cm.get("status") == "ok":
        changed = cm.get("rows_changed_by_normalization", 0)
        st.write(
            f"Rows changed by text normalization: {changed}"
        )

        before = cm.get("macro_f1_before_normalization")
        after = cm.get("macro_f1_after_normalization")

        if before is not None and after is not None:
            st.write(
                f"Macro F1 before normalization: {before:.4f}"
            )
            st.write(
                f"Macro F1 after normalization: {after:.4f}"
            )

    # General limitations
    st.divider()
    st.subheader("General limitations and responsible use")

    st.markdown("""
    - This is a research and educational tool, not a medical diagnostic
      or screening system.
    - Dataset labels may be proxy labels and are not necessarily
      clinical diagnoses.
    - Age is used only when explicitly provided. It is never inferred
      from writing.
    - Language detection may be incorrect, especially for Romanized
      and code-mixed text.
    - Small groups should not be over-interpreted.
    - Results may reflect dataset sampling bias.
    - Generative AI summaries may contain errors and require human review.
    - If someone is in distress, contact a qualified professional
      or a local emergency or helpline service.
    """)