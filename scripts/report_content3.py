"""Report content: Chapters 6-7, references, appendices."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SYN = ROOT / "outputs"
REAL = ROOT / "outputs" / "real_brighter"


def f3(x):
    return "%.3f" % x


REFERENCES = [
    "World Health Organization, \"Depressive disorder (depression),\" Fact sheet, WHO, Geneva, 2023.",
    "G. Gururaj et al., \"National Mental Health Survey of India, 2015-16: Summary,\" NIMHANS, Bengaluru, Publication No. 128, 2016.",
    "D. E. Low et al., \"Natural language processing reveals vulnerable mental health support groups and heightened health anxiety on Reddit during COVID-19: Observational study,\" J. Med. Internet Res., vol. 22, no. 10, p. e22635, 2020.",
    "A. Yates, A. Cohan, and N. Goharian, \"Depression and self-harm risk assessment in online forums,\" in Proc. EMNLP, 2017, pp. 2968-2978.",
    "A. Cohan et al., \"SMHD: A large-scale resource for exploring online language usage for multiple mental health conditions,\" in Proc. COLING, 2018, pp. 1485-1497.",
    "S. M. Muhammad et al., \"BRIGHTER: BRIdging the Gap in Human-annotated Textual Emotion Recognition datasets for 28 languages,\" arXiv:2502.11926, 2025.",
    "S. M. Muhammad et al., \"SemEval-2025 Task 11: Bridging the gap in text-based emotion detection,\" arXiv:2503.07269, 2025.",
    "J. Schler, M. Koppel, S. Argamon, and J. Pennebaker, \"Effects of age and gender on blogging,\" in Proc. AAAI Spring Symp. Computational Approaches to Analyzing Weblogs, 2006, pp. 199-205.",
    "K. Kroenke, R. L. Spitzer, and J. B. W. Williams, \"The PHQ-9: Validity of a brief depression severity measure,\" J. Gen. Intern. Med., vol. 16, no. 9, pp. 606-613, 2001.",
    "E. Turcan and K. McKeown, \"Dreaddit: A Reddit dataset for stress analysis in social media,\" in Proc. 10th Int. Workshop Health Text Mining and Information Analysis (LOUHI), 2019, pp. 97-107.",
    "M. De Choudhury, M. Gamon, S. Counts, and E. Horvitz, \"Predicting depression via social media,\" in Proc. ICWSM, 2013, pp. 128-137.",
    "G. Coppersmith, M. Dredze, and C. Harman, \"Quantifying mental health signals in Twitter,\" in Proc. Workshop Computational Linguistics and Clinical Psychology (CLPsych), 2014, pp. 51-60.",
    "S. C. Guntuku, D. B. Yaden, M. L. Kern, L. H. Ungar, and J. C. Eichstaedt, \"Detecting depression and mental illness on social media: An integrative review,\" Curr. Opin. Behav. Sci., vol. 18, pp. 43-49, 2017.",
    "K. Harrigian, C. Aguirre, and M. Dredze, \"On the state of social media data for mental health research,\" in Proc. CLPsych, 2021, pp. 15-24.",
    "C. Aguirre, K. Harrigian, and M. Dredze, \"Gender and racial fairness in depression research using social media,\" in Proc. EACL, 2021, pp. 2932-2949.",
    "A. Conneau et al., \"Unsupervised cross-lingual representation learning at scale,\" in Proc. ACL, 2020, pp. 8440-8451.",
    "S. Khanuja et al., \"MuRIL: Multilingual representations for Indian languages,\" arXiv:2103.10730, 2021.",
    "P. Patwa et al., \"SemEval-2020 Task 9: Overview of sentiment analysis of code-mixed tweets,\" in Proc. SemEval, 2020, pp. 774-790.",
    "S. Ji et al., \"MentalBERT: Publicly available pretrained language models for mental healthcare,\" in Proc. LREC, 2022, pp. 7184-7190.",
    "X. Xu et al., \"Mental-LLM: Leveraging large language models for mental health prediction via online text data,\" Proc. ACM Interact. Mob. Wearable Ubiquitous Technol., vol. 8, no. 1, 2024.",
    "K. Yang et al., \"MentaLLaMA: Interpretable mental health analysis on social media with large language models,\" arXiv:2309.13567, 2023.",
    "S. L. Blodgett, S. Barocas, H. Daume III, and H. Wallach, \"Language (technology) is power: A critical survey of 'bias' in NLP,\" in Proc. ACL, 2020, pp. 5454-5476.",
    "E. B. Wilson, \"Probable inference, the law of succession, and statistical inference,\" J. Amer. Statist. Assoc., vol. 22, no. 158, pp. 209-212, 1927.",
    "Y. Benjamini and Y. Hochberg, \"Controlling the false discovery rate: A practical and powerful approach to multiple testing,\" J. R. Stat. Soc. Ser. B, vol. 57, no. 1, pp. 289-300, 1995.",
    "B. L. Monroe, M. P. Colaresi, and K. M. Quinn, \"Fightin' words: Lexical feature selection and evaluation for identifying the content of political conflict,\" Political Analysis, vol. 16, no. 4, pp. 372-403, 2008.",
    "F. Pedregosa et al., \"Scikit-learn: Machine learning in Python,\" J. Mach. Learn. Res., vol. 12, pp. 2825-2830, 2011.",
    "Streamlit Inc., \"Streamlit documentation,\" [Online]. Available: https://docs.streamlit.io",
    "D. Chicco and G. Jurman, \"The advantages of the Matthews correlation coefficient (MCC) over F1 score and accuracy in binary classification evaluation,\" BMC Genomics, vol. 21, art. 6, 2020.",
    "M. Mitchell et al., \"Model cards for model reporting,\" in Proc. FAT*, 2019, pp. 220-229.",
    "A. Benton, G. Coppersmith, and M. Dredze, \"Ethical research protocols for social media health research,\" in Proc. Workshop Ethics in NLP (EthNLP), 2017, pp. 94-102.",
]


def chapter6(r, F, UI):
    syn = json.loads((SYN / "reports" / "analysis_summary.json").read_text(encoding="utf-8"))
    r.chapter(6, "Results and Discussion")
    r.h2("6.1 Experimental Set-up")
    r.p("Two runs of the same pipeline are reported. **Run A** uses the synthetic dataset shipped with the project (1,200 invented "
        "posts with age, language and four severity labels). Its purpose is to verify that every module behaves correctly; "
        "its numbers are **not evidence about real people**. **Run B** uses real open data: 2,500 English, 2,500 Hindi and "
        "2,500 Marathi texts from the BRIGHTER emotion corpus (7,500 rows, 6,662 after cleaning). BRIGHTER texts have no age "
        "field, so age analysis is correctly reported as unavailable for Run B, and the language-based analyses (O3, O5) are exercised "
        "on real text. For Run B the label is a proxy: __negative_affect__ if the annotators marked sadness or fear, otherwise "
        "__neutral_or_other__. It is an emotion proxy, not a clinical label.")
    r.tbl("Datasets used in the experiments", ["Run", "Data", "Rows (clean)", "Languages", "Age", "Label"], [
        ["A", "Synthetic (sample_clean.csv)", "1,200", "en, hi, mr, hinglish, roman_mr", "Yes (5 bands)", "none/mild/moderate/severe (invented)"],
        ["B", "BRIGHTER (open)", "6,662", "en 2,259; hi 2,205; mr 2,198", "No", "negative_affect vs neutral_or_other (proxy)"],
    ], widths=[0.4, 1.5, 0.8, 1.6, 0.8, 1.4], fs=9, align=["c", "l", "c", "l", "c", "l"])
    r.tbl("Cleaning audit for Run B (BRIGHTER)", ["Step", "Rows"], [
        ["Input rows (3 languages x 2,500)", "7,500"],
        ["Exact duplicates removed", "836"],
        ["Conflicting-label duplicates removed", "2"],
        ["Rows with PII scrubbed (URL/e-mail/handle/phone)", "2"],
        ["Rows after cleaning", "6,662"],
        ["Provided vs detected language agreement", "93.3%"],
        ["Age missing (so age analysis unavailable)", "6,662"],
    ], widths=[4.5, 2.0], fs=10, align=["l", "r"])

    r.h2("6.2 Run A: Age-wise Analysis (synthetic data)")
    r.p("Table 13 gives the share of records with an elevated label (moderate or severe) in each age band with Wilson intervals. "
        "In the synthetic data the share falls from 43.3% (18-25) to 16.5% (46+), and the chi-square test of label against age gives "
        "chi2 = 63.66, p = 4.8e-9, Cramer's V = 0.133 (a small-to-moderate effect). Label against language is not significant "
        "(p = 0.84, V = 0.045). These patterns were built into the generator, so finding them confirms that the code recovers a "
        "known effect; it says nothing about real populations.")
    at = pd.read_csv(SYN / "tables" / "age_label_table.csv")
    rows = []
    for band, g in at.groupby("age_band", sort=False):
        e = g[g["label"].isin(["moderate", "severe"])]
        k, n = int(e["count"].sum()), int(g["n"].iloc[0])
        p = 100 * k / n
        # Wilson interval
        z = 1.96
        den = 1 + z * z / n
        c = (p / 100 + z * z / (2 * n)) / den
        h = z * ((p / 100) * (1 - p / 100) / n + z * z / (4 * n * n)) ** 0.5 / den
        rows.append([band, n, k, "%.1f" % p, "%.1f - %.1f" % (100 * (c - h), 100 * (c + h))])
    r.tbl("Run A: elevated-label share by age band (synthetic)", ["Age band", "n", "Elevated", "Share %", "95% Wilson CI %"],
          rows, widths=[1.2, 0.9, 1.0, 1.1, 1.6], fs=10, align=["c", "c", "c", "c", "c"])
    r.fig(F / "chart_syn_age_elevated.png", "Run A: elevated-label share by age band (synthetic data)", 4.8)
    r.fig(SYN / "figures" / "age_label_heatmap.png", "Run A: label distribution by age band (heat-map)", 4.6)

    r.h2("6.3 Run A: Language and Code-mixed Analysis (synthetic data)")
    r.p("The synthetic corpus contains 487 English, 183 Hindi, 167 Marathi, 209 Hinglish and 154 Roman-Marathi records; 363 records "
        "(30.25%) are Romanized or code-mixed. The rule-based detector agrees with the provided language for 99.5% of records. "
        "Conservative normalisation changed only 9 records and left macro-F1 essentially unchanged (0.8238 before, 0.8233 after), which "
        "is the intended behaviour: normalisation should not alter content it does not need to.")

    r.h2("6.4 Run A: Model Comparison and Fairness (synthetic data)")
    mo = pd.read_csv(SYN / "tables" / "model_comparison_overall.csv")
    names = {"complement_nb": "Complement NB", "logreg": "Logistic Regression", "linear_svm": "Linear SVM"}
    rows = [[names[m.model], f3(m.accuracy_mean), f3(m.macro_f1_mean), f3(m.macro_precision_mean),
             f3(m.macro_recall_mean), f3(m.mcc_mean)] for m in mo.itertuples()]
    r.tbl("Run A: overall performance (5-fold grouped CV x 3 seeds)", ["Model", "Accuracy", "Macro-F1", "Macro-P", "Macro-R", "MCC"],
          rows, widths=[1.8, 0.9, 0.9, 0.9, 0.9, 0.9], fs=10, align=["l", "c", "c", "c", "c", "c"])
    fg = pd.read_csv(SYN / "tables" / "model_fairness_gaps.csv")
    rows = [[names[m.model], m.group_type, m.groups_compared, f3(m.macro_f1_gap), m.worst_group] for m in fg.itertuples()]
    r.tbl("Run A: macro-F1 fairness gaps", ["Model", "Group type", "Groups", "Gap", "Worst group"], rows,
          widths=[1.7, 1.5, 0.8, 0.8, 1.5], fs=9.5, align=["l", "l", "c", "c", "c"])
    r.fig(F / "chart_model_comparison.png", "Run A: model comparison", 4.8)
    r.fig(F / "chart_fairness_gaps.png", "Run A: fairness gaps by group type", 4.8)
    r.p("All three models reach macro-F1 between 0.82 and 0.84, which is expected because the synthetic text was written from "
        "label-specific phrase banks. Complement NB scores highest overall, but its gap by age band (0.089, worst group 36-45) "
        "is larger than Linear SVM's (0.062). This shows why a single overall number is insufficient: the best overall model "
        "is not the fairest across age bands. The age x language analysis keeps only cells with at least 100 records, so only two "
        "cells are comparable; the rest are suppressed, which the dashboard shows explicitly.")

    r.h2("6.5 Run B: Real Multilingual Data (BRIGHTER)")
    r.p("The proxy label differs strongly by language (Figure 16 and Table 16): 64.1% of English texts are negative-affect versus 30.9% "
        "of Hindi and 33.2% of Marathi texts (chi2 = 626.7, p ~ 8e-137, Cramer's V = 0.307, a moderate effect). Part of this difference "
        "reflects different annotation and sampling choices per language rather than any difference in the speakers, so it must not be "
        "read as a statement about English versus Hindi speakers.")
    lt = pd.read_csv(REAL / "tables" / "language_label_table.csv")
    rows = []
    for lang, nm in [("en", "English"), ("hi", "Hindi"), ("mr", "Marathi")]:
        g = lt[(lt.language == lang) & (lt.label == "negative_affect")].iloc[0]
        rows.append([nm, int(g.n), int(g["count"]), "%.1f" % g.pct, "%.1f - %.1f" % (g.ci_low_pct, g.ci_high_pct)])
    r.tbl("Run B: negative-affect share by language", ["Language", "n", "Negative affect", "Share %", "95% Wilson CI %"], rows,
          widths=[1.3, 0.9, 1.3, 1.0, 1.6], fs=10, align=["l", "c", "c", "c", "c"])
    r.fig(F / "chart_real_language_share.png", "Run B: negative-affect share by language", 4.3)
    r.fig(REAL / "figures" / "language_label_heatmap.png", "Run B: label distribution by language (heat-map)", 4.4)

    mo = pd.read_csv(REAL / "tables" / "model_comparison_overall.csv")
    rows = [[names[m.model], f3(m.accuracy_mean), f3(m.macro_f1_mean) + " +/- " + f3(m.macro_f1_std), f3(m.macro_precision_mean),
             f3(m.macro_recall_mean), f3(m.mcc_mean)] for m in mo.itertuples()]
    r.tbl("Run B: overall performance on real data", ["Model", "Accuracy", "Macro-F1", "Macro-P", "Macro-R", "MCC"],
          rows, widths=[1.8, 0.9, 1.4, 0.8, 0.8, 0.8], fs=10, align=["l", "c", "c", "c", "c", "c"])
    gm = pd.read_csv(REAL / "tables" / "model_group_metrics.csv")
    rows = []
    for m in ["linear_svm", "logreg", "complement_nb"]:
        row = [names[m]]
        for lang in ["en", "hi", "mr"]:
            g = gm[(gm.model == m) & (gm.group == lang)].iloc[0]
            row.append("%.3f (%.3f-%.3f)" % (g.macro_f1_mean, g.macro_f1_ci_low, g.macro_f1_ci_high))
        fgr = pd.read_csv(REAL / "tables" / "model_fairness_gaps.csv")
        row.append(f3(fgr[fgr.model == m].macro_f1_gap.iloc[0]))
        rows.append(row)
    r.tbl("Run B: macro-F1 by language with 95% bootstrap CI, and language gap", ["Model", "English", "Hindi", "Marathi", "Gap"],
          rows, widths=[1.5, 1.4, 1.4, 1.4, 0.7], fs=9.5, align=["l", "c", "c", "c", "c"])
    r.fig(F / "chart_real_language_f1.png", "Run B: macro-F1 by language", 4.8)
    r.fig(REAL / "figures" / "confusion_matrix_best_model.png", "Run B: confusion matrix of the best model (Linear SVM)", 3.9)
    r.p("Linear SVM is the best model overall (macro-F1 0.816, accuracy 0.819, MCC 0.632), followed by Logistic Regression (0.804). "
        "Complement NB is much weaker (0.660). The headline number hides a large language gap: Linear SVM reaches 0.841 on Hindi and "
        "0.887 on Marathi but only 0.626 on English, a gap of 0.261 with the worst group always English. The bootstrap intervals "
        "are narrow (about +/- 0.01-0.02) so the gap is not a sampling effect. Three explanations are plausible and are "
        "not separable with this data: (i) the English subset has a different, more balanced label mix, which lowers macro-F1 "
        "for any classifier; (ii) English emotion texts are more varied or less lexically explicit than the Indian-language texts; "
        "(iii) the proxy mapping is a different construct in each language. For Complement NB the English macro-recall is exactly "
        "0.5, i.e. it predicts the majority class, which explains its poor score there. This is exactly the kind of finding that "
        "an overall score would never show.")

    r.h2("6.6 Explainability")
    r.p("For Logistic Regression the largest positive coefficients for the negative-affect class on Run B are Marathi and Hindi fear "
        "and sadness words (for example the Marathi word for 'fear', the Hindi word for 'fear', words for 'sadness', 'worry' and "
        "'sad'), which confirms that the model relies on sensible lexical cues. The Streamlit Explainability page shows these "
        "tables together with group-distinctive terms ranked by log-odds z-score. On Run A the top terms per class are the "
        "synthetic phrase-bank words, as expected.")

    r.h2("6.7 Generative AI Components (O6 and O7)")
    r.p("The offline generator produced an age-wise insight paragraph for Run A containing 24 numbers; all 24 matched the facts "
        "and the safety check passed (guardrail JSON stored with the report). The paragraph opens with an explicit note that the "
        "data are synthetic, reports the range 16.5% (46+) to 43.3% (18-25), the chi-square result, language counts and the model "
        "gaps, and ends with the sentence that results are associations, not causes, not a diagnosis, and must not be used for "
        "decisions about individuals. For Run B the facts record that labels are proxies and that no age is available.")
    r.p("Twelve awareness drafts were produced (English, Hindi, Marathi x teen, young adult, adult, older). They come from a "
        "curated offline bank, each carries the disclaimer and the helpline placeholder, and each is marked PENDING_HUMAN_REVIEW. "
        "An example is given in Appendix B. In the online mode the same facts and checks would be applied to an OpenAI-compatible "
        "model; this mode was implemented and unit-tested with a stub but not evaluated with a live model.")

    r.h2("6.8 Dashboard")
    r.p("The Streamlit dashboard has eight pages: Overview, Age analysis, Language analysis, Age x Language, Model comparison, "
        "Explainability, Generative AI and Limitations. Figures 20 to 23 show four of them rendered from the synthetic run; the "
        "others are in Appendix C.")
    r.fig(UI / "ui_age.png", "Dashboard: age analysis page", 5.8)
    r.fig(UI / "ui_language.png", "Dashboard: language analysis page", 5.8)
    r.fig(UI / "ui_models.png", "Dashboard: model comparison page", 5.8)
    r.fig(UI / "ui_genai.png", "Dashboard: generative AI page", 5.8)

    r.h2("6.9 Testing")
    r.p("The project has 39 automated tests (pytest), all passing. Table 19 groups them by feature; the Streamlit page test "
        "starts the app and checks that a page renders.")
    r.tbl("Test cases", ["ID", "Feature", "Test (file)", "Expected result", "Status"], [
        ["T1", "PII scrubbing", "test_scrub_pii", "URL, e-mail, @handle and phone replaced by tokens", "Pass"],
        ["T2", "Language detection", "test_detect_language (parametrised)", "en, hi, mr, Hinglish and Roman-Marathi samples identified", "Pass"],
        ["T3", "Detector accuracy", "test_language_detector_accuracy_on_synthetic", "Agreement with provided language above threshold", "Pass"],
        ["T4", "PHQ-9 mapping", "test_phq9_bands", "0-4 none, 5-9 mild, 10-19 moderate, 20-27 severe", "Pass"],
        ["T5", "Statistics helpers", "test_stats_helpers", "Wilson, chi-square, Kruskal, BH produce known values", "Pass"],
        ["T6", "Cleaning", "test_clean_messy_data", "Missing, duplicate, invalid-age rows handled; age never imputed", "Pass"],
        ["T7", "File formats", "test_all_sample_formats_load", "CSV, TSV, JSON, JSONL, XLSX all load", "Pass"],
        ["T8", "Schema errors", "test_missing_columns_give_clear_error", "Clear error message for missing columns", "Pass"],
        ["T9", "Roman normalisation", "test_normalize_roman, test_noisy_codemixed_file_is_normalized", "Variants unified, clean text untouched", "Pass"],
        ["T10", "Models and groups", "test_models_and_groups, test_models_skip_tiny_data", "Metrics produced; tiny data skipped safely", "Pass"],
        ["T11", "Guardrails", "test_guardrails, test_offline_summary_passes_own_guardrails", "Wrong numbers and banned phrases rejected; offline text passes", "Pass"],
        ["T12", "Awareness bank", "test_awareness_bank_complete", "12 items, disclaimer, placeholder and review status present", "Pass"],
        ["T13", "Open datasets", "test_prepare_brighter_proxy_labels, test_prepare_reddit_hashes_authors_and_labels, test_extract_stated_age", "Proxy labels, hashed authors, stated-age extraction", "Pass"],
        ["T14", "Dashboard", "test_dashboard_page_renders", "Streamlit page renders without error", "Pass"],
    ], widths=[0.4, 1.1, 2.1, 2.2, 0.5], fs=8.5, align=["c", "l", "l", "l", "c"])

    r.h2("6.10 Discussion")
    r.bl(["**Why group-wise reporting matters.** On real data the best overall model had a 0.261 macro-F1 gap between languages; on "
          "synthetic data the model with the best overall score was not the one with the smallest age gap.",
          "**Privacy is structural.** The GenAI layer never receives text; all 24 checked numbers matched the statistics.",
          "**Honest negative result for age.** Open multilingual data contain no age field, so O1/O2/O4 can be demonstrated "
          "only on synthetic data until the consented survey (Track C) is collected. The system detects this and says so.",
          "**Reproducibility.** Seeds, configuration and a single 'full' command regenerate every table and figure.",
          "**Comparison with prior work.** Earlier studies [3]-[5] report single overall scores on English Reddit; this work "
          "adds group-wise gaps and Indian languages but uses a smaller, proxy-labelled dataset, so its absolute scores are "
          "not comparable with those papers."])
    r.h2("6.11 Limitations")
    r.bl(["Run A is synthetic; Run B uses emotion proxy labels and no age.",
          "Only three linear models were evaluated; transformer models (MuRIL, XLM-R) are not included.",
          "Language identification is rule-based and Romanized Marathi/Hindi detection is approximate.",
          "Awareness drafts come from an offline bank and are unreviewed; online GenAI was not evaluated with a live model.",
          "The literature search was not systematic, so the research gap claim is provisional."])


def chapter7(r):
    r.chapter(7, "Conclusion and Future Scope")
    r.h2("7.1 Conclusion")
    r.p("The project delivers a reproducible framework that treats age and language as first-class dimensions of mental-health "
        "text analysis. It cleans and anonymises data, analyses label and text patterns by age band and language, compares three "
        "classifiers with author-grouped validation and bootstrap intervals, explains their decisions, and uses Generative AI only on "
        "aggregated, number-verified statistics. All seven objectives (O1-O7) are implemented and covered by 39 passing tests.")
    r.p("On real BRIGHTER data (6,662 English, Hindi and Marathi texts) the best model reaches macro-F1 0.816 overall but only 0.626 on "
        "English versus 0.841 on Hindi and 0.887 on Marathi, showing that an overall score can conceal a large language gap. On synthetic "
        "data the pipeline recovers the built-in age pattern and shows that the best overall model is not necessarily the fairest "
        "across age bands. The outputs are research and awareness aids; they are not diagnostic, and the labels are proxies.")
    r.h2("7.2 Future Scope")
    r.bl(["Collect the consented survey (Track C) with age and PHQ-9 to run O1, O2 and O4 on real data after ethics approval.",
          "Add transformer encoders (MuRIL, XLM-R) and compare them with the linear baselines under the same fairness protocol.",
          "Improve language identification and transliteration handling for Hinglish and Roman Marathi.",
          "Add more Indian languages (Tamil, Bengali, Telugu) using the BRIGHTER data.",
          "Evaluate online GenAI with a live model, with native-speaker review of every draft and a verified helpline directory.",
          "Add calibration and uncertainty reporting, and intersectional analysis with larger samples.",
          "Systematic literature review to confirm the research gap and publish the framework as an open toolkit."])


def references(r):
    r.plain_title("REFERENCES")
    for i, ref in enumerate(REFERENCES, 1):
        par = r.doc.add_paragraph()
        pf = par.paragraph_format
        pf.left_indent = __import__("docx").shared.Inches(0.5)
        pf.first_line_indent = __import__("docx").shared.Inches(-0.5)
        pf.space_after = __import__("docx").shared.Pt(4)
        pf.line_spacing = 1.15
        pf.alignment = 3
        r._runs(par, "[%d]\t%s" % (i, ref), 11)


def appendices(r, F, UI):
    r.plain_title("APPENDIX A: REPRODUCING THE RESULTS")
    r.p("All commands are run from the project root in an activated virtual environment (Windows PowerShell shown).", line=1.3)
    r.code("""
python -m venv .venv
.\\.venv\\Scripts\\activate
pip install -r requirements.txt

python -m pytest -q                       # 39 tests
python main.py generate-data              # synthetic data (code validation only)
python main.py full                       # validate, clean, analyze, models, GenAI
streamlit run app.py                      # dashboard on http://localhost:8501

python main.py fetch-open --lang hin --max-rows 2500   # repeat for eng and mar
""")
    r.p("Configuration (seeds, age bands, minimum group sizes, bootstrap count) is in config/config.yaml. Outputs are written to "
        "outputs/tables, outputs/figures and outputs/reports. The real-data results in this report are stored in outputs/real_brighter.",
        line=1.3)
    r.plain_title("APPENDIX B: SAMPLE GENERATED TEXT", page_break=True)
    r.h3("B.1 Age-wise insight (offline template, synthetic data)")
    txt = (SYN / "reports" / "genai_age_insights.md").read_text(encoding="utf-8").split("\n")
    body = [t for t in txt if t.strip() and not t.startswith("#") and not t.startswith("_")]
    r.p(body[0].replace("NOTE: ", "") + " " + (body[1] if len(body) > 1 else ""), size=11, line=1.3)
    r.h3("B.2 Awareness draft (English, teen; offline bank; PENDING_HUMAN_REVIEW)")
    r.p("School and exam pressure can feel heavy. Feeling stressed or low sometimes is common, and you do not have to handle it "
        "alone. Talk to a parent, teacher or friend you trust, and look after sleep, breaks and time outdoors. If the feeling "
        "lasts for weeks, a counsellor or doctor can help. This is general information, not medical advice or a diagnosis. "
        "If you are in crisis or in danger, contact local emergency services or a helpline: [ADD VERIFIED LOCAL HELPLINE].",
        size=11, line=1.3)
    r.plain_title("APPENDIX C: ADDITIONAL DASHBOARD PAGES", page_break=True)
    r.fig(UI / "ui_overview.png", "Dashboard: overview page", 5.8)
    r.fig(UI / "ui_age_language.png", "Dashboard: age x language page", 5.8)
    r.fig(UI / "ui_explain.png", "Dashboard: explainability page", 5.8)
    r.fig(UI / "ui_limits.png", "Dashboard: limitations page", 5.8)
    r.plain_title("APPENDIX D: ETHICS AND SURVEY PROTOCOL (SUMMARY)", page_break=True)
    r.bl(["Track C collects short free-text responses, an explicit age, language and PHQ-9 items from adult (18+) volunteers; under-18s are excluded unless the ethics committee and a guardian-consent procedure allow it.",
          "Participation is voluntary with informed consent, the right to withdraw and no collection of names or contact details.",
          "PHQ-9 bands: 0-4 none, 5-9 mild, 10-19 moderate, 20-27 severe [9]; scores are used for research labels only and never reported "
          "to individuals as a diagnosis.",
          "A wellbeing message with a verified helpline is shown to every participant after submission, and the form states that it is not monitored in real time.",
          "Supervisor approval and, where one exists, ethics-committee approval are required before any survey data are collected; the full consent pack is in docs/04."])
