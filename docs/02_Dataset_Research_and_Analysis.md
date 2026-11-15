# 02 – Dataset Research and Analysis

**Important:** Dataset descriptions below come from general knowledge of the literature and have **not** been re-verified against official pages in this session. Before use, each must be checked for current availability, license, columns and access conditions (checklist in Section 6). Treat all "Known" claims as "to verify".

---

## 1. Core Finding

The project needs four fields together: `text`, a mental-health `label`, `age`, and `language`. **To my knowledge, no widely available public dataset provides all four**, especially with Hindi/Marathi/Hinglish. This is the central risk of the project and also a defensible research-gap statement (pending a systematic literature search).

Per the blueprint, we must not infer age from writing and must not blindly concatenate datasets. The plan is therefore a **tiered, honest dataset strategy**.

## 2. Candidate Datasets

| ID | Dataset | Text | MH label | Age | Language | Access | Role |
|---|---|---|---|---|---|---|---|
| D1 | Blog Authorship Corpus (Schler et al., 2006) | Blogs | No (topic/sign only) | Yes (self-reported, bands ~13-17, 23-27, 33-47) | English | Public (Kaggle mirror) | Age-pattern analysis; needs a documented label strategy |
| D2 | Reddit Mental Health Dataset (Low et al., 2020, Zenodo) | Reddit posts | Subreddit-based (depression, anxiety, etc.) | No | English | Public | Label source for English text models |
| D3 | DepSign-LT-EDI 2022 | Reddit | Depression severity (not / moderate / severe) | No | English | Shared-task request | Severity categories ("depression categories") |
| D4 | Dreaddit (Turcan & McKeown, 2019) | Reddit | Stress yes/no | No | English | Public | Supplementary binary baseline |
| D5 | RSDD / SMHD (Yates et al.; Cohan et al.) | Reddit | Self-reported diagnosis | Not provided | English | Restricted, data-use agreement | Optional, access uncertain |
| D6 | BRIGHTER / SemEval-2025 Task 11 | Multilingual short texts | Emotion labels (e.g., sadness, fear) | No | ~28 languages incl. Hindi, Marathi (verify) | Public/shared-task | Language analysis using emotion proxy |
| D7 | SemEval-2020 Task 9 SentiMix (Hinglish) | Code-mixed tweets | Sentiment | No | Hindi-English | Shared-task | Code-mixed normalization experiments |
| D8 | L3Cube-MahaSent / MahaHate (Marathi) | Marathi tweets | Sentiment / hate | No | Marathi | Public | Marathi preprocessing and language-model checks |
| D9 | PAN author-profiling corpora | Tweets / blogs | No | Yes (age groups) | EN, ES, others | Shared-task | Age-profile reference; not MH |
| D10 | **Own consented survey (Track C)** | Free-text in EN/HI/MR | PHQ-9 or PHQ-2 band (self-reported) | Yes (band, self-reported) | Yes | Collected by team | Only route to true age + language + label |

Notes:
- D6-D8 give language diversity but **no age** and not depression labels. Emotion/sentiment is only a weak proxy for mental-health signal and must be labelled as such.
- D1 gives age but **no mental-health label**.
- D10 is the only source meeting all four fields, and requires institutional ethics approval, informed consent, anonymization and a medically safe design (no collection from at-risk users without a support path).

## 3. Recommended Strategy (Tiered)

### Track A – Primary (age-wise depression categories, English)
Goal: O1, O2, O5 (age part).
Options, in decreasing preference:
1. **A1 – Self-reported age in Reddit text.** Use D2/D3-type posts where authors explicitly state age (for example "I (24F)"). Extract only explicit disclosures with a documented regex, validated on a manual sample. This is *extraction of a stated fact*, not inference. Requires reading the dataset license and ethics note; may yield small subsets per band.
2. **A2 – D1 (Blog Authorship) with transparent weak labels.** Age is genuine; MH label would come from a validated lexicon/emotion model and be explicitly labelled "weak, proxy". Findings must be framed as text-pattern analysis, not risk prevalence.
3. **A3 – Track C survey data** (below), if approved and collected.

### Track B – Multilingual (O3, code-mixed part)
Use D6 (Hindi/Marathi/English), D7 (Hinglish), D8 (Marathi). Label = emotion/sentiment mapped to "negative-affect vs other" with a documented mapping. Age is not available, so Track B supports O3 and O5 (language part) only.

### Track C – Own survey (recommended if time and approval allow)
Small anonymous form (target 150-300 responses): age band, preferred language, a short free-text prompt about recent mood, and PHQ-2/PHQ-9 self-screening score. Needs supervisor and institutional ethics sign-off, consent, no identifiers, safe-messaging and helpline information shown to all participants. This is the only way to genuinely deliver O4 (age x language). If not possible, O4 becomes a **documented "insufficient data" analysis** using whatever overlap exists, or a synthetic-data code-test clearly labelled as non-evidence.

### Harmonization rules (no naive concatenation)
- Maintain a unified schema: `text, label_raw, label_unified, age_band, language, source, source_id, label_type {clinical-proxy, self-report, emotion-proxy, weak}`.
- Never pool datasets with different `label_type` into one metric without reporting per-source results.
- Always report per-source and per-group `n`.

## 4. Objective-to-Dataset Feasibility

| Objective | A1 | A2 | Track B | Track C | Feasibility |
|---|---|---|---|---|---|
| O1 Age text patterns | partial | yes | no | yes | High (A2) |
| O2 Age-based risk | partial | proxy only | no | yes | Medium; strongest with A1 or C |
| O3 Multilingual | no | no | yes | yes | High |
| O4 Age + language | no | no | no | yes | **Low unless Track C** |
| O5 Model comparison by group | age | age | language | both | Medium-High |
| O6 GenAI insights | uses aggregates from above | | | | High |
| O7 GenAI awareness content | no data needed | | | | High |

**Recommendation:** Proceed with A1+A2 for age, Track B for language, and decide on Track C at review. Be explicit that O4 depends on Track C.

## 5. Data Quality and Bias Risks
- Reddit population skews young, English-speaking, Western; limits generalization to India.
- Subreddit label != clinical diagnosis (label noise).
- Self-reported age can be false; self-diagnosis is unverified.
- Emotion-proxy labels are not depression labels.
- Imbalance across age bands and languages will cause unstable subgroup metrics.
- Duplicates / cross-posting can leak across train/test; use group-aware splitting by author where IDs exist, near-duplicate hashing otherwise.
- Romanized Marathi/Hindi has no standard spelling; normalization can change meaning.

## 6. Dataset Audit Checklist (fill one per dataset)
Name; official URL; access date; license; permitted use; language coverage; age field present and how obtained; label definition and annotators; rows and class distribution; missing and duplicate counts; privacy/consent notes; known biases. Store in `docs/data_card_<id>.md`.

## 7. Literature Gap Statement (to be validated)
Prior work commonly addresses English depression detection on Reddit/Twitter; fewer studies jointly examine **age-stratified** and **language-stratified** model behaviour with fairness reporting and explainability for Indian-language / code-mixed settings. This must be confirmed by a systematic search (IEEE Xplore, ACL Anthology, PubMed, Scopus) before it is claimed. Search strings are in the implementation plan.

## 8. Decisions Needed From You
1. Is Track C (own survey) allowed by your institution/supervisor?
2. Do you have access to RSDD/SMHD/DepSign, or should we use only open data?
3. Is a transformer baseline (XLM-R / MuRIL) acceptable, given CPU-only training time?
4. Which LLM provider is permitted for O6/O7 (Azure OpenAI, other API, or local model)?
