# 01 – Requirements, Objectives, Outcomes and Parameters

**Project:** Age and Language-Based Mental Health Risk Analysis Using AI
**Status:** Draft for review. Nothing here has been implemented or validated yet.
**Nature:** Research and educational analysis only. Not a diagnostic tool.

---

## 1. Stakeholders and User Requirements

| Stakeholder | Need | Requirement |
|---|---|---|
| Student team / evaluator | IEEE-style, reproducible mini project | Clear problem, method, metrics, reproducible code, report |
| Supervisor / reviewer | Defensible scope and ethics | Documented dataset provenance, limitations, ethics statement |
| Researcher / analyst (end user of dashboard) | See how mental-health text patterns differ by age and language | Interactive dashboard with age, language, combined views |
| Awareness / outreach reader | General, safe multilingual content | Reviewed, non-clinical generated text |

### Functional requirements (FR)
- FR1: Load, validate and profile a dataset (schema, missing values, duplicates, label, age and language checks).
- FR2: Privacy-preserving preprocessing (remove usernames, URLs, phone numbers, e-mails; keep original text).
- FR3: Age-band analysis of labels and text patterns.
- FR4: Language analysis, including detection of Hindi / Marathi / English / Hinglish / Romanized Marathi.
- FR5: Age x language cross-analysis with minimum-sample-size guards.
- FR6: Train and compare at least 3 baseline models, overall and per group.
- FR7: Explainability (coefficients and SHAP/LIME) for selected predictions.
- FR8: Generative-AI insight summaries from aggregated statistics only.
- FR9: Generative-AI multilingual awareness content with human review.
- FR10: Streamlit dashboard exposing all of the above.

### Non-functional requirements (NFR)
- NFR1 Reproducibility: fixed seeds, pinned `requirements.txt`, config file, saved splits.
- NFR2 Privacy: no raw posts or identifiers sent to any external service.
- NFR3 Fairness reporting: every metric reported with subgroup `n`; sparse groups flagged.
- NFR4 Runs on a laptop CPU (no GPU required for the core pipeline).
- NFR5 IEEE-style documentation: abstract, related work, method, experiments, threats to validity.

---

## 2. Final Objective Set (7 objectives)

Mapped to your list. O1-O5 are core analytics, O6-O7 are Generative AI.

| ID | Objective | Type | Priority |
|---|---|---|---|
| **O1** | **Age-wise mental-health text-pattern analysis** | Core | Must |
| **O2** | **Age-based risk analysis (age-wise depression/risk categories)** | Core | **Must – primary** |
| **O3** | Multilingual mental-health analysis | Core | Must |
| **O4** | Age + language combined analysis | Core | Should |
| **O5** | Age + language model performance comparison (group-wise fairness) | Core | Must |
| **O6** | Age-wise insight generation using Generative AI | GenAI | Should |
| **O7** | Multilingual awareness-content generation using Generative AI | GenAI | Should |

Supporting cross-cutting component: explainability (blueprint Objective 4) is delivered inside O2 and O5 rather than as a separate objective. Code-mixed normalization (blueprint Objective 3) is delivered inside O3.

### Recommended primary objective
**O2 – Age-based risk analysis.** Reasons:
1. Directly matches your stated interest (age-wise depression categories).
2. It is the most defensible with a labelled dataset and clear metrics.
3. O1, O4, O5 and O6 reuse its outputs, so it is the project spine.

### Objective definitions

**O1 Age-wise text patterns.** Compare vocabulary (TF-IDF top terms, log-odds), sentiment/emotion lexicon rates, first-person pronoun rate, post length, across age bands.
*Output:* age-band summary table, top-term charts, statistical test (chi-square for label vs age; Kruskal-Wallis for numeric text features) with effect sizes.

**O2 Age-based risk analysis.** Distribution of dataset-defined categories (for example none / mild / moderate / severe, or depressed / not) per age band, plus per-age-band classifier performance.
*Output:* category x age heatmap with confidence intervals, odds ratios, per-band macro-F1.

**O3 Multilingual analysis.** Language distribution, label balance per language, language-specific preprocessing, code-mixed detection and conservative normalization (original text preserved).
*Output:* language x label table, code-mixed examples table, before/after normalization metrics.

**O4 Age + language.** Age-band x language cross-tab, label rates per cell, with cells below the minimum `n` marked "insufficient evidence".
*Output:* heatmap and grouped bars.

**O5 Model comparison.** Logistic Regression + TF-IDF, Linear SVM, Multinomial/Complement NB, optionally a multilingual transformer (XLM-R / MuRIL) as a stretch baseline. Overall and per-group metrics, plus fairness gaps (max-min macro-F1, recall gap).
*Output:* model x group metrics table, confusion matrices, gap analysis.

**O6 GenAI age-wise insights.** An LLM turns the aggregated statistics table (JSON) into a short narrative. A guardrail checker verifies that every number in the narrative exists in the input.
*Output:* generated summary, number-verification report, limitations paragraph.

**O7 GenAI multilingual awareness content.** Generate general wellbeing / help-seeking awareness text in English, Hindi, Marathi using age-appropriate tone. No diagnosis, no treatment advice, helpline placeholders only. Mandatory human review.
*Output:* reviewed content bank with review status and reviewer notes.

---

## 3. Expected Outcomes

| # | Outcome | Evidence |
|---|---|---|
| 1 | Validated dataset and data card | `docs/data_card.md` |
| 2 | Quantified age-wise label and text differences | Tables, charts, test statistics |
| 3 | Multilingual / code-mixed findings with stated limits | Language report |
| 4 | Subgroup fairness evaluation of >= 3 models | Metrics table, gap plot |
| 5 | Explanations for model behaviour | SHAP/LIME plots |
| 6 | Verified GenAI summary and awareness content | Guardrail report, review log |
| 7 | Working Streamlit dashboard | Runnable `app.py` |
| 8 | IEEE-format report and slides | `report/` |

## 4. Project Parameters

### Experimental parameters
| Parameter | Proposed value (to confirm after data audit) |
|---|---|
| Age bands | 13-17, 18-25, 26-35, 36-45, 46+ (merge if `n` too small) |
| Languages | English (required); Hindi, Marathi, Hinglish if data supports |
| Min cell size for reporting | n >= 30 per group; n >= 100 for model metrics |
| Split | Stratified 80/20, group-aware if author IDs exist |
| Cross-validation | 5-fold stratified |
| Seeds | 3 fixed seeds, report mean +/- std |
| Primary metric | Macro-F1 |
| Secondary | Precision, recall (per class), accuracy, confusion matrix, MCC, AUROC when binary |
| Fairness | Macro-F1 gap, recall gap, bootstrap 95% CI |
| Significance | Chi-square / Kruskal-Wallis, Bonferroni or FDR correction |

### System parameters
Python 3.10+, scikit-learn, pandas, NumPy, matplotlib/seaborn, langdetect or fastText `lid.176`, SHAP/LIME, Streamlit, optional `transformers`.

## 5. Scope Boundaries
**In scope:** research-grade analysis, group-wise evaluation, dashboards, safe GenAI summaries.
**Out of scope:** diagnosis, individual risk scoring for real users, inferring age from writing, clinical claims, sending raw posts to external LLMs.

## 6. Success Criteria
- All 7 objectives have runnable code, outputs and a documented result or a documented "insufficient data" finding.
- Every reported number is reproducible from one command.
- Each subgroup result includes `n` and confidence interval.
- GenAI guardrail: 100% of numbers in generated insights match the source statistics.
