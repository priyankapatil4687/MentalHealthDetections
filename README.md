# Age and Language-Based Mental Health Text Analysis

A reproducible Python framework that analyses mental-health-related text across **age groups** and **languages** (English, Hindi, Marathi, Hinglish, Romanized Marathi), compares baseline classifiers **per group** with fairness gaps, and produces guard-railed generative-AI summaries and awareness content, all explored through a Streamlit dashboard.

> **Research and educational tool only. It is not a diagnostic system** and must not be used to assess individuals. Results from the bundled sample data are **synthetic** and only prove the software works.

## Why this project

Mental-health text classifiers are usually reported with one overall score, which can hide failures on specific age bands or languages. India adds code-mixing (Hinglish, Romanized Marathi) that standard English pipelines handle poorly. Public datasets that provide text, a mental-health label, age and language together are rare, so careful dataset handling is itself part of the contribution.

## Objectives

| ID | Objective |
|---|---|
| O1 | Age-wise text-pattern analysis |
| O2 | Age-based risk-category analysis (primary objective) |
| O3 | Multilingual and code-mixed analysis |
| O4 | Age x language combined analysis |
| O5 | Group-wise model performance and fairness comparison |
| O6 | Generative-AI age-wise insight generation |
| O7 | Generative-AI multilingual awareness content (human review required) |

## Features

- **Load and validate** CSV, TSV, JSON, JSONL and Excel files. Column names are matched automatically, and missing values, duplicates and labels are checked (`src/data/`).
- **Privacy-preserving cleaning.** Emails, phone numbers, URLs and @names are replaced by placeholders. Missing or impossible ages are never guessed; they become "unknown".
- **Language handling.** Rule-based detection and conservative code-mixed normalization that preserves the original text.
- **Age and language analysis** (`src/analysis/`). Label distributions, top terms and age x language cross-tabs. Groups below the minimum size are flagged rather than interpreted.
- **Model comparison** (`src/models/train.py`). Logistic Regression, Linear SVM and Complement Naive Bayes use author-grouped, stratified cross-validation, repeated seeds and bootstrap confidence intervals. Subgroup `n`, fairness gaps and top explanatory features are reported.
- **Generative AI** (`src/genai/`). Insights are built from **aggregated statistics only** (never raw posts). A number-verification guardrail checks the text and falls back to offline templates on failure. Works offline by default; online mode uses any OpenAI-compatible API. Awareness content is marked `PENDING_HUMAN_REVIEW`.
- **Streamlit dashboard** (`app.py`) covering all of the above.

## Architecture

```
Raw data -> Validation -> Privacy cleaning + unified schema -> Age/Language features
          -> O1/O2 age, O3 language, O4 age x language analysis
          -> O5 model training, group-wise evaluation, explainability
          -> Aggregated stats JSON -> GenAI insights (O6) and awareness content (O7)
          -> Streamlit dashboard
```

Only the aggregated statistics JSON ever reaches an LLM.

## Project structure

```
app.py              Streamlit dashboard
main.py             Command-line entry point
config/config.yaml  Seeds, paths, age bands, thresholds, model and GenAI settings
src/
  data/             load, validate, clean, normalize, language, synthetic, open_datasets
  analysis/         age, language, code-mixed and common helpers
  models/           training and group-wise evaluation
  genai/            client, guardrails, insights, awareness content
  utils/            plotting, stats, text helpers
tests/              pytest suite
scripts/            guide, report and screenshot builders
docs/               project documentation (see below)
data/sample/        synthetic sample datasets
outputs/            generated figures, tables and reports
```

## Getting started

Requires **Python 3.10+** (tested on 3.14). Commands are for Windows PowerShell.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py check
```

Quick start:

```powershell
python main.py generate-data
python main.py full --input data/sample/sample_clean.csv
python -m streamlit run app.py
```

The dashboard opens at http://localhost:8501. Run the tests with `python -m pytest -q`.

## Commands

| Command | What it does |
|---|---|
| `python main.py check` | Confirms Python and packages work |
| `python main.py generate-data` | Writes synthetic test files into `data/sample/` |
| `python main.py validate --input FILE` | Shows columns, missing values and warnings |
| `python main.py clean --input FILE` | Cleans data into `data/processed/clean.csv` |
| `python main.py analyze` | Age, language, code-mixed, age x language and model analysis |
| `python main.py run --input FILE` | validate + clean + analyze |
| `python main.py genai [--llm offline\|online]` | Creates AI-assisted insights and awareness content |
| `python main.py full --input FILE [--llm online]` | run + genai |
| `python main.py fetch-open --lang hin\|mar\|eng` | Downloads BRIGHTER emotion data to `data/raw/` |
| `python main.py prepare-reddit --files F1 F2 --positive depression` | Builds a dataset from Reddit Mental Health CSVs |

## Using your own data

Put CSV, TSV, JSON, JSONL or `.xlsx` files in `data/raw/` and run `python main.py full --input data/raw/yourfile.csv`.

| Meaning | Accepted column names | Required |
|---|---|---|
| Text | text, post, content, body, message, mood_text, comment, tweet | Yes |
| Label | label, category, diagnosis, class, target, risk, risk_label | Yes (or a PHQ-9 score) |
| PHQ-9 score | phq9_score, phq9 | Alternative to label (0-4 none, 5-9 mild, 10-19 moderate, 20-27 severe) |
| Age | age, years, age_years | Optional |
| Age band | age_band, age_group (13-17, 18-25, 26-35, 36-45, 46+) | Optional |
| Language | language, lang, preferred_language | Optional (detected if missing) |
| Author ID | source_id, user_id, author_id, response_id, id | Optional, recommended |

For real data, set `codemixed.save_examples: false` in `config/config.yaml`, because saved examples are raw text.

## Datasets

No widely available public dataset provides text, label, age and language together, so the project uses a tiered strategy and never pools datasets with different label types.

| Dataset | Role | Label | Age | Language |
|---|---|---|---|---|
| Reddit Mental Health Dataset (Zenodo) | Age patterns (O1, O2) | Subreddit proxy (`mh_forum` vs `control`) | Only explicit self-statements such as "24F"; validate manually | English |
| BRIGHTER (SemEval-2025 Task 11) | Language analysis (O3, O5) | `negative_affect` proxy from sadness or fear | None | Hindi, Marathi, English |
| Own consented survey (Track C) | Age x language (O4) | PHQ-9 screening bands | Self-reported band | English, Hindi, Marathi, Hinglish |
| Synthetic data | Code testing only | Generated | Generated | 5 language types |

Labels from the open datasets are **proxies, not diagnoses**. See [docs/02_Dataset_Research_and_Analysis.md](docs/02_Dataset_Research_and_Analysis.md) for the candidate dataset list and the dataset checklist.

## Generative AI options

- **Offline (default):** no setup or internet; uses templates and a prepared awareness-content bank.
- **Online (optional):** set `OPENAI_API_KEY` (optionally `OPENAI_BASE_URL` and `OPENAI_MODEL`) in the terminal, then add `--llm online`. Never store keys in files. Only aggregated statistics are sent.
- Awareness content needs review by a native speaker and a qualified reviewer, and the `[ADD VERIFIED LOCAL HELPLINE]` placeholder in `src/genai/awareness.py` must be replaced before public use.

## Configuration

Edit [config/config.yaml](config/config.yaml). Key settings:

| Setting | Meaning |
|---|---|
| `seed` | Randomness seed for repeatable results |
| `age.bands`, `age.min_valid`, `age.max_valid` | Age band edges and valid range |
| `labels.order`, `labels.elevated` | Label display order and which labels count as "elevated" |
| `analysis.min_group_n` | Minimum posts before a group is interpreted (30) |
| `models.*` | CV folds, seeds, minimum group size for metrics (100), bootstrap resamples |
| `codemixed.save_examples` | Save raw-text examples (turn off for real data) |
| `genai.online_model` | Model used in online mode |

## Documentation

| Document | Contents |
|---|---|
| [01 Requirements, Objectives, Outcomes](docs/01_Requirements_Objectives_Outcomes.md) | Stakeholders, functional and non-functional requirements, objectives O1-O7 |
| [02 Dataset Research and Analysis](docs/02_Dataset_Research_and_Analysis.md) | Candidate datasets, tiered strategy, harmonization rules |
| [03 Implementation and Action Plan](docs/03_Implementation_Plan_and_Action_Plan.md) | Architecture, folder structure, phase-wise plan |
| [04 Track C Survey and Consent](docs/04_TrackC_Survey_and_Consent.md) | Draft survey, consent and ethics pack |
| [05 IEEE Report Draft](docs/05_IEEE_Report_Draft.md) | Conference-style report draft |
| [06 User Manual](docs/06_User_Manual.md) | Detailed install, usage and configuration guide |

## Ethics and privacy

- Not a diagnostic tool; labels are proxies or screening scores.
- PII is scrubbed, age is never inferred from writing, and validation is author-grouped to prevent leakage.
- Every metric is reported with subgroup `n`, and under-powered groups are flagged.
- Survey data collection (Track C) requires supervisor and ethics approval, informed consent and a verified helpline before any data is collected.
- Do not commit real or sensitive data. `.gitignore` excludes `data/raw/`, survey responses, secrets and model files.

## Status

The pipeline and tests are implemented (31 tests pass, 8 are skipped). Real-data results in the IEEE draft are still `[TODO]` placeholders.
