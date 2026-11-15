import json

from src.config import get_dir
from src.analysis.common import save_json
from src.genai import client
from src.genai.guardrails import check_safety, verify_numbers

SYSTEM = (
    "You write short, cautious research summaries. Use ONLY numbers that appear in the JSON facts. "
    "Do not invent numbers, do not claim causes, do not give diagnoses, treatment or advice about individuals. "
    "Mention that results describe dataset labels, not clinical status. 120-180 words."
)


def build_facts(analysis, models, sources, min_n):
    """Aggregated, non-identifying statistics only. Groups below min_n are suppressed."""
    age = analysis.get("age_analysis_O1_O2", {})
    lang = analysis.get("language_analysis_O3", {})
    facts = {
        "rows_after_cleaning": analysis.get("rows"),
        "dataset_files": sources,
        "synthetic_test_data": all(str(s).startswith("sample") for s in sources),
        "proxy_labels": any("proxy" in str(s) for s in sources),
        "min_group_n": min_n,
        "significance_threshold": 0.05,
        "p_value_reporting_floor": 0.001,
    }
    if age.get("status") == "ok":
        sizes = age["group_sizes"]
        share = {b: round(v, 1) for b, v in age["elevated_share_by_age_band_pct"].items() if sizes.get(b, 0) >= min_n}
        facts["age"] = {"rows_with_age": age["rows_with_age"], "elevated_share_pct_by_age_band": share,
                        "group_sizes": {b: n for b, n in sizes.items() if n >= min_n}}
        chi = age.get("label_vs_age_chi_square")
        if chi:
            facts["age"]["chi_square"] = {"p_value": chi["p_value"], "cramers_v": round(chi["cramers_v"], 3)}
    else:
        facts["age"] = {"status": "unavailable"}
    facts["language"] = {
        "counts": {k: v for k, v in lang.get("language_counts", {}).items() if v >= min_n},
        "code_mixed_share_pct": round(lang.get("code_mixed_share_pct", 0.0), 1),
    }
    if models and models.get("status") == "ok":
        best = models["best_model"]
        row = next(r for r in models["overall"] if r["model"] == best)
        facts["models"] = {
            "n_models_compared": len(models["overall"]),
            "best_model": best,
            "best_macro_f1": round(row["macro_f1_mean"], 3),
            "gaps": [{"group_type": g["group_type"], "model": g["model"], "macro_f1_gap": round(g["macro_f1_gap"], 3)}
                     for g in models.get("fairness_gaps", []) if g["model"] == best],
        }
    return facts


def offline_summary(f):
    s = []
    if f.get("synthetic_test_data"):
        s.append("NOTE: this run used synthetic test data, so none of the findings below are evidence about real people.")
    s.append(f"After cleaning, the dataset contains {f['rows_after_cleaning']} posts.")
    if f.get("proxy_labels"):
        s.append("The labels are proxies (emotion tags or forum membership), not clinical status.")
    age = f.get("age", {})
    shares = age.get("elevated_share_pct_by_age_band")
    if shares:
        hi = max(shares, key=shares.get)
        lo = min(shares, key=shares.get)
        s.append(f"The share of posts with an elevated label ranges from {shares[lo]}% in age band {lo} "
                 f"to {shares[hi]}% in age band {hi} (age bands with at least {f['min_group_n']} posts).")
        chi = age.get("chi_square")
        if chi:
            p = chi["p_value"]
            ptxt = f"p = {round(p, 3)}" if p >= f["p_value_reporting_floor"] else f"p < {f['p_value_reporting_floor']}"
            verdict = "differs" if p < f["significance_threshold"] else "does not clearly differ"
            s.append(f"A chi-square test indicates the label distribution {verdict} across age bands "
                     f"({ptxt}; Cramer's V = {chi['cramers_v']}).")
    else:
        s.append("Age-wise insights are unavailable because reliable age information is missing or groups are too small.")
    lang = f.get("language", {})
    if lang.get("counts"):
        s.append(f"Languages with enough posts: {', '.join(f'{k} ({v})' for k, v in lang['counts'].items())}; "
                 f"{lang['code_mixed_share_pct']}% of posts are code-mixed or Romanized.")
    m = f.get("models")
    if m:
        s.append(f"Of {m['n_models_compared']} models compared, {m['best_model']} had the best macro-F1 ({m['best_macro_f1']}).")
        for g in m["gaps"]:
            s.append(f"Across {g['group_type']} groups its macro-F1 gap is {g['macro_f1_gap']}.")
    s.append("These are associations in dataset labels only. They do not show causes, are not a diagnosis, "
             "and must not be used to make decisions about individuals.")
    return " ".join(s)


def generate_insights(analysis, models, sources, cfg, mode="offline"):
    min_n = cfg["analysis"]["min_group_n"]
    facts = build_facts(analysis, models, sources, min_n)
    offline = offline_summary(facts)
    text, used, notes = offline, "offline-template", []
    if mode == "online":
        if not client.online_available():
            notes.append("OPENAI_API_KEY not set; used offline template.")
        else:
            try:
                cand = client.chat(SYSTEM, "FACTS:\n" + json.dumps(facts, ensure_ascii=False), cfg["genai"]["online_model"])
                num, safe = verify_numbers(cand, facts), check_safety(cand)
                if num["ok"] and safe["ok"]:
                    text, used = cand, "online-llm"
                else:
                    notes.append(f"LLM output rejected by guardrails (numbers={num}, safety={safe}); used offline template.")
            except Exception as e:  # network/auth errors must not break the pipeline
                notes.append(f"Online call failed ({type(e).__name__}); used offline template.")
    guard = {"numbers": verify_numbers(text, facts), "safety": check_safety(text), "source": used, "notes": notes}
    rep = get_dir(cfg, "reports_dir")
    (rep / "genai_age_insights.md").write_text(
        f"# Age-wise insights (generated, source: {used})\n\n{text}\n\n"
        "_Generated from aggregated statistics only. Verify before use._\n", encoding="utf-8")
    save_json({"facts_sent": facts, "guardrail": guard}, rep / "genai_age_insights_guardrail.json")
    return text, guard
