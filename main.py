"""Command-line entry point.

Examples (run from the project folder, with the virtual environment active):
    python main.py check
    python main.py generate-data
    python main.py run --input data/sample/sample_messy.csv
"""
import argparse
import sys
from pathlib import Path

from src.config import ROOT, get_dir, load_config

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def cmd_check(cfg, args):
    import matplotlib, numpy, pandas, scipy, sklearn, yaml  # noqa: F401
    print("Age and Language-Based Mental Health Risk Analysis")
    print(f"Python {sys.version.split()[0]} | pandas {pandas.__version__} | scikit-learn {sklearn.__version__}")
    print("Project environment is ready.")


def cmd_generate(cfg, args):
    from src.data.synthetic import write_all
    out = get_dir(cfg, "sample_dir")
    written = write_all(out, cfg["seed"])
    print(f"Synthetic TEST data written to {out} (invented data, not evidence):")
    for name, desc in written.items():
        print(f"  {name:28s} {desc}")


def _resolve(p):
    p = Path(p)
    return p if p.is_absolute() else ROOT / p


def cmd_validate(cfg, args):
    from src.analysis.common import save_json
    from src.data.load import load_dataset
    from src.data.validate import profile_dataset
    df, mapping = load_dataset(_resolve(args.input))
    prof = profile_dataset(df, mapping)
    save_json(prof, get_dir(cfg, "reports_dir") / "data_validation.json")
    print(f"Loaded {prof['rows']} rows. Column mapping: {prof['column_mapping']}")
    print(f"Missing values: {prof['missing_counts']}")
    print(f"Raw labels: {prof['label_counts_raw']}")
    for w in prof["warnings"]:
        print("WARNING:", w)
    return df, mapping


def cmd_clean(cfg, args):
    from src.analysis.common import save_json
    from src.data.clean import clean_dataframe
    from src.data.load import load_dataset
    df, _ = load_dataset(_resolve(args.input))
    clean, rep = clean_dataframe(df, cfg)
    out = get_dir(cfg, "processed_dir") / "clean.csv"
    clean.to_csv(out, index=False, encoding="utf-8-sig")
    save_json(rep, get_dir(cfg, "reports_dir") / "cleaning_report.json")
    print(f"Cleaned {rep['rows_input']} -> {rep['rows_output']} rows. Saved {out}")
    for k, v in rep.items():
        print(f"  {k}: {v}")


def cmd_analyze(cfg, args):
    import pandas as pd
    from src.analysis.age_analysis import run_age_analysis
    from src.analysis.common import save_json
    from src.analysis.language_analysis import run_combined_analysis, run_language_analysis
    from src.analysis.codemixed_analysis import run_codemixed_analysis
    from src.models.train import run_model_analysis
    path = get_dir(cfg, "processed_dir") / "clean.csv"
    if not path.exists():
        sys.exit("No cleaned data found. Run: python main.py clean --input <file>")
    df = pd.read_csv(path, encoding="utf-8-sig", keep_default_na=False, na_values=[""])
    df["label"] = df["label"].astype(str)
    print("Running age, language and code-mixed analysis...", flush=True)
    summary = {
        "rows": int(len(df)),
        "sources": sorted(df["source"].astype(str).unique()),
        "age_analysis_O1_O2": run_age_analysis(df, cfg),
        "language_analysis_O3": run_language_analysis(df, cfg),
        "codemixed_O3": run_codemixed_analysis(df, cfg),
        "age_language_O4": run_combined_analysis(df, cfg),
        "models_O5": (print("Training and comparing models (this can take 1-2 minutes, please wait)...", flush=True)
                      or run_model_analysis(df, cfg)),
    }
    save_json(summary, get_dir(cfg, "reports_dir") / "analysis_summary.json")
    a = summary["age_analysis_O1_O2"]
    print(f"Age analysis: {a.get('status')}")
    if a.get("label_vs_age_chi_square"):
        c = a["label_vs_age_chi_square"]
        print(f"  label vs age: chi2={c['chi2']:.2f}, p={c['p_value']:.4f}, Cramer's V={c['cramers_v']:.3f}")
    print(f"Language analysis: {summary['language_analysis_O3']['status']}")
    cm = summary["codemixed_O3"]
    print(f"Code-mixed analysis: {cm['status']}", {k: cm[k] for k in cm if k.startswith('macro_f1')})
    print(f"Age x language: {summary['age_language_O4']['status']}")
    m = summary["models_O5"]
    print(f"Models: {m['status']}")
    if m["status"] == "ok":
        for r in m["overall"]:
            print(f"  {r['model']:14s} macro-F1 {r['macro_f1_mean']:.3f} +/- {r['macro_f1_std']:.3f}")
        print(f"  best: {m['best_model']} ({m['cv']})")
    print(f"Tables -> {get_dir(cfg, 'tables_dir')}\nFigures -> {get_dir(cfg, 'figures_dir')}")
    print(f"Summary -> {get_dir(cfg, 'reports_dir') / 'analysis_summary.json'}")


def cmd_genai(cfg, args):
    import json
    from src.genai.awareness import generate_awareness
    from src.genai.insights import generate_insights
    path = get_dir(cfg, "reports_dir") / "analysis_summary.json"
    if not path.exists():
        sys.exit("No analysis found. Run: python main.py run --input <file>")
    summary = json.loads(path.read_text(encoding="utf-8"))
    text, guard = generate_insights(summary, summary.get("models_O5"), summary.get("sources", []), cfg, args.llm)
    print("--- O6 Age-wise insights ---")
    print(text)
    print(f"Guardrail: numbers ok={guard['numbers']['ok']}, safety ok={guard['safety']['ok']}, source={guard['source']}")
    for n in guard["notes"]:
        print("NOTE:", n)
    items, notes = generate_awareness(cfg, args.llm)
    print(f"--- O7 Awareness content: {len(items)} items written (status PENDING_HUMAN_REVIEW) ---")
    for n in notes:
        print("NOTE:", n)
    print(f"Files -> {get_dir(cfg, 'reports_dir')}")


def cmd_fetch_open(cfg, args):
    from src.data.open_datasets import fetch_brighter, prepare_brighter
    print(f"Downloading BRIGHTER '{args.lang}' (CC-BY-4.0) from Hugging Face...", flush=True)
    raw = fetch_brighter(args.lang, max_rows=args.max_rows)
    out = prepare_brighter(raw, args.lang)
    path = ROOT / "data" / "raw" / f"brighter_{args.lang}_proxy.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Saved {len(out)} rows -> {path}")
    print(f"Label counts: {out['label'].value_counts().to_dict()}")
    print("No age field in this dataset. Labels are emotion PROXIES, not mental-health status.")
    print(f"Next: python main.py full --input data/raw/{path.name}")


def cmd_prepare_reddit(cfg, args):
    from src.data.open_datasets import age_validation_sample, prepare_reddit_mh
    files = [_resolve(f) for f in args.files]
    for f in files:
        if not f.exists():
            sys.exit(f"ERROR: file not found: {f}")
    out = prepare_reddit_mh(files, positive=args.positive.split(","))
    if args.max_per_class:
        import pandas as pd
        out = pd.concat([g.sample(min(len(g), args.max_per_class), random_state=cfg["seed"])
                         for _, g in out.groupby("label")], ignore_index=True)
    path = ROOT / "data" / "raw" / "reddit_mh_proxy.csv"
    out.to_csv(path, index=False, encoding="utf-8-sig")
    n_age = int(out["age"].notna().sum())
    print(f"Saved {len(out)} rows -> {path}")
    print(f"Label counts: {out['label'].value_counts().to_dict()}")
    print(f"Posts with an explicitly stated age: {n_age} ({100 * n_age / max(1, len(out)):.1f}%)")
    if n_age:
        sample = age_validation_sample(out)
        sp = ROOT / "data" / "raw" / "age_extraction_check.csv"
        sample.to_csv(sp, index=False, encoding="utf-8-sig")
        print(f"Manually check {sp.name} (fill correct_yes_no) before trusting the age bands.")
    print(f"Next: python main.py full --input data/raw/{path.name}")


def cmd_run(cfg, args):
    print("=== Step 1: validate ==="); cmd_validate(cfg, args)
    print("\n=== Step 2: clean ==="); cmd_clean(cfg, args)
    print("\n=== Step 3: analyze ==="); cmd_analyze(cfg, args)


def cmd_full(cfg, args):
    cmd_run(cfg, args)
    print("\n=== Step 4: generative AI ==="); cmd_genai(cfg, args)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("fetch-open", help="download BRIGHTER (Hindi/Marathi/English emotion data)")
    p.set_defaults(fn=cmd_fetch_open)
    p.add_argument("--lang", choices=["eng", "hin", "mar"], default="hin")
    p.add_argument("--max-rows", type=int, default=None)
    p = sub.add_parser("prepare-reddit", help="prepare Reddit Mental Health Dataset CSVs from Zenodo")
    p.set_defaults(fn=cmd_prepare_reddit)
    p.add_argument("--files", nargs="+", required=True)
    p.add_argument("--positive", default="depression", help="comma-separated subreddits labelled mh_forum")
    p.add_argument("--max-per-class", type=int, default=None)
    for name, fn in [("check", cmd_check), ("generate-data", cmd_generate), ("validate", cmd_validate),
                     ("clean", cmd_clean), ("analyze", cmd_analyze), ("run", cmd_run),
                     ("genai", cmd_genai), ("full", cmd_full)]:
        p = sub.add_parser(name)
        p.set_defaults(fn=fn)
        if name in ("validate", "clean", "run", "full"):
            p.add_argument("--input", default="data/sample/sample_clean.csv")
        if name in ("genai", "full"):
            p.add_argument("--llm", choices=["offline", "online"], default="offline",
                           help="online needs OPENAI_API_KEY; only aggregated statistics are sent")
    args = parser.parse_args()
    try:
        args.fn(load_config(), args)
    except (FileNotFoundError, ValueError) as e:
        sys.exit(f"ERROR: {e}")


if __name__ == "__main__":
    main()
