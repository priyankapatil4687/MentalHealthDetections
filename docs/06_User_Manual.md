# User Manual: Install, Configure and Run

For beginners. Commands are for **Windows PowerShell** inside the project folder (`Mini Project`). Replace paths if yours differs.

---

## 1. What this app does
It reads text data (posts or survey answers) with a label, and optionally age and language. It cleans the data, analyses patterns by age and language, trains and compares three simple models, explains them, writes AI-assisted summaries, and shows everything in a dashboard. It is a **research tool, not a diagnosis tool**.

## 2. One-time setup
1. Install **Python 3.10 or newer** from python.org (tick "Add Python to PATH"). Check: `python --version`.
2. Install **Visual Studio Code** and its Python extension.
3. Open the project folder in VS Code, then **Terminal > New Terminal**.
4. Create the environment (once):
   ```powershell
   python -m venv .venv
   ```
5. Activate it (every new terminal):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks it: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`, then activate again. You can also skip activation and always write `.\.venv\Scripts\python.exe` instead of `python`.
6. Install packages (once):
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
7. Check: `python main.py check`. Expected: "Project environment is ready."

## 3. Quick start (5 minutes)
```powershell
python main.py generate-data
python main.py full --input data/sample/sample_clean.csv
python -m streamlit run app.py
```
1. `generate-data` creates invented test files in `data/sample/`.
2. `full` cleans the file, runs all analyses (about 1-2 minutes, models train silently), and creates AI-assisted text.
3. `streamlit run` opens the dashboard in your browser (http://localhost:8501). Stop it with Ctrl+C.

Results from sample files are **synthetic**: they only prove the software works.

## 4. All commands
| Command | What it does |
|---|---|
| `python main.py check` | Confirms Python and packages work |
| `python main.py generate-data` | Writes synthetic test files into `data/sample/` |
| `python main.py validate --input FILE` | Shows columns, missing values and warnings |
| `python main.py clean --input FILE` | Cleans data into `data/processed/clean.csv` |
| `python main.py analyze` | Age, language, code-mixed, age x language and model analysis on the cleaned data |
| `python main.py run --input FILE` | validate + clean + analyze |
| `python main.py genai [--llm offline\|online]` | Creates the AI-assisted insights and awareness content |
| `python main.py full --input FILE [--llm online]` | run + genai |
| `python main.py fetch-open --lang hin\|mar\|eng` | Downloads BRIGHTER emotion data to `data/raw/` |
| `python main.py prepare-reddit --files F1 F2 --positive depression` | Builds a dataset from Reddit Mental Health CSVs |
| `python -m pytest -q` | Runs automated tests (all should pass) |
| `python -m streamlit run app.py` | Starts the dashboard |

`FILE` is a path such as `data/sample/sample_messy.csv`.

## 5. Using your own data
### Accepted files
CSV, TSV, JSON, JSONL or Excel (`.xlsx`). Put them in `data/raw/`.

### Columns (names are matched automatically)
| Meaning | Accepted names | Required |
|---|---|---|
| Text | text, post, content, body, message, mood_text, comment, tweet | Yes |
| Label | label, category, diagnosis, class, target, risk, risk_label | Yes (or a PHQ-9 score) |
| PHQ-9 score | phq9_score, phq9 | Alternative to label (0-4 none, 5-9 mild, 10-19 moderate, 20-27 severe) |
| Age (number) | age, years, age_years | Optional |
| Age band | age_band, age_group (must be 13-17, 18-25, 26-35, 36-45 or 46+) | Optional |
| Language | language, lang, preferred_language (English, Hindi, Marathi, Hinglish, Romanized Marathi) | Optional; detected by rules if missing |
| Author/respondent ID | source_id, user_id, author_id, response_id, id | Optional but recommended: keeps one author's posts together during testing |

Then run: `python main.py full --input data/raw/yourfile.csv`.

### Rules the app follows
- Missing or impossible ages are **not guessed**; they become "unknown" and are skipped by age analysis.
- No age column? Age pages say "unavailable"; language analysis still works.
- Emails, phone numbers, URLs and @names are replaced by placeholders.
- Groups with fewer than 30 posts (analysis) or 100 posts (model metrics) are flagged and not interpreted.

## 6. Real open datasets
- **BRIGHTER (Hindi/Marathi/English emotions)**: `python main.py fetch-open --lang hin`, then `python main.py full --input data/raw/brighter_hin_proxy.csv`. Needs internet. No age field.
- **Reddit Mental Health Dataset**: download CSVs (for example `depression_pre_features_tfidf_256.csv` and a few control subreddits such as `fitness`) from https://zenodo.org/records/3941387 into `data/raw/`. Then:
  ```powershell
  python main.py prepare-reddit --files data/raw/depression_pre_features_tfidf_256.csv data/raw/fitness_pre_features_tfidf_256.csv --positive depression --max-per-class 5000
  python main.py full --input data/raw/reddit_mh_proxy.csv
  ```
  Ages come only from explicit self-statements. Open `data/raw/age_extraction_check.csv`, fill `correct_yes_no` for each row and compute the share correct before trusting age results. Files are large; start with small ones.
- Labels from both are **proxies**, not diagnoses.

## 7. Survey data (Track C)
Follow `docs/04_TrackC_Survey_and_Consent.md` (get approval first). Export the responses as CSV with columns `response_id, age_band, preferred_language, mood_text, phq9_score`, put the file in `data/raw/`, and run `full` on it. For real data, **set `codemixed.save_examples: false`** in `config/config.yaml`.

## 8. Configuration (`config/config.yaml`)
| Setting | Meaning |
|---|---|
| `seed` | Randomness seed (keep for repeatable results) |
| `age.bands` | Age band edges and names |
| `age.min_valid` / `max_valid` | Ages outside this range become unknown |
| `labels.order` | Display order of labels |
| `labels.elevated` | Labels counted as "elevated" in age and language summaries (add your own label names here if different) |
| `analysis.min_group_n` | Minimum posts before a group is interpreted (default 30) |
| `models.n_splits`, `seeds`, `min_group_n`, `bootstrap` | Cross-validation folds, repeat seeds, minimum posts per group for model metrics (100), bootstrap resamples |
| `codemixed.save_examples` | Save raw text examples of normalization (turn off for real data) |
| `genai.online_model` | Model name used in online mode |

Edit with VS Code, save, and rerun the command.

## 9. Generative AI options
- **Offline (default):** no setup, no internet. Uses templates and a prepared awareness-content bank.
- **Online (optional):** uses any OpenAI-compatible service. In the same terminal, before running:
  ```powershell
  $env:OPENAI_API_KEY = "your-key"
  # optional: $env:OPENAI_BASE_URL = "https://api.openai.com/v1"; $env:OPENAI_MODEL = "gpt-4o-mini"
  python main.py full --input data/sample/sample_clean.csv --llm online
  ```
  Never put keys in files or share them. Only aggregated statistics are sent, never posts. If the key is missing, the call fails, or the text breaks a safety/number check, the app falls back to the offline text and says so.
- Awareness content is marked `PENDING_HUMAN_REVIEW`. A native speaker and a qualified reviewer must approve it, and `[ADD VERIFIED LOCAL HELPLINE]` must be replaced before public use (edit `src/genai/awareness.py`).

## 10. Where results appear
| Folder | Contents |
|---|---|
| `outputs/tables/` | CSV tables (age, language, models, fairness gaps, top words) |
| `outputs/figures/` | PNG charts |
| `outputs/reports/` | `analysis_summary.json`, cleaning and validation reports, GenAI text and its safety check, awareness content |
| `outputs/models/` | Saved best model |
| `data/processed/clean.csv` | Cleaned data |

Each run overwrites these. Copy the `outputs` folder elsewhere to keep a run.

## 11. Dashboard
Start `python -m streamlit run app.py`. Use the left menu for pages. Use "Run on a dataset" in the sidebar to choose a file from `data/sample` or `data/raw` and press **Run pipeline**. Yellow banners warn when data is synthetic or labels are proxies.

## 12. Troubleshooting
| Problem | Fix |
|---|---|
| `python` not recognized | Reinstall Python with "Add to PATH", or use `py` |
| Activation blocked | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` |
| `ModuleNotFoundError` | Activate the environment and run `python -m pip install -r requirements.txt` |
| "No cleaned data found" | Run `main.py run` or `full` with `--input` first |
| "No text column found" | Rename your columns using the table in section 5 |
| Analysis seems stuck | Model training takes 1-2 minutes (more for big files); wait for the result lines |
| Garbled Hindi/Marathi in Excel | Open CSV via Data > From Text/CSV with UTF-8, or view it in VS Code |
| Dashboard shows "No results yet" | Press **Run pipeline** or run `main.py full` first |
| Fetch-open fails with a network error | Check internet; retry later (the server can be busy) |
| Port already in use | `python -m streamlit run app.py --server.port 8600` |
| Very large Reddit files are slow | Use `--max-per-class` and fewer files |
| Age analysis says unavailable | Your data has no reliable age column; this is expected |

## 13. Project map
```text
main.py            command-line entry point
app.py             dashboard
config/config.yaml settings
src/data/          loading, cleaning, language detection, normalization, open datasets, synthetic data
src/analysis/      age, language, code-mixed, combined analysis
src/models/        training, group-wise evaluation, explanations
src/genai/         insights, awareness content, guardrails, optional online client
tests/             automated tests
docs/              requirements, dataset research, plan, survey pack, report draft, this manual
```

## 14. Responsible use
Not a diagnostic tool. Do not use results to judge individuals. Do not publish raw posts. Keep personal data private and follow your ethics approval.
