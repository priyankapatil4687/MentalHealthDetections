import json

import pandas as pd

from src.config import load_config
from src.data.clean import clean_dataframe
from src.data.load import load_dataset
from src.data.normalize import normalize_roman
from src.data.synthetic import generate_base, write_all
from src.genai.awareness import BANK, DISCLAIMER
from src.genai.guardrails import check_safety, verify_numbers
from src.genai.insights import build_facts, offline_summary
from src.models.train import run_model_analysis

CFG = load_config()


def _clean_df(n=500, seed=5):
    base = generate_base(n, seed).assign(age_band=pd.NA, source="sample_test")
    clean, _ = clean_dataframe(base, CFG)
    return clean


def test_normalize_roman():
    assert normalize_roman("Mujhey bohot udaas lag raha hai, nahin") == "mujhe bahut udas lag raha hai, nahi"
    assert normalize_roman("sooooo sad") == "soo sad"
    assert normalize_roman("I feel fine") == "I feel fine"


def test_noisy_codemixed_file_is_normalized(tmp_path):
    write_all(tmp_path, 3)
    df, _ = load_dataset(tmp_path / "sample_codemixed_noisy.csv")
    clean, _ = clean_dataframe(df, CFG)
    assert (clean["text_norm"] != clean["text_clean"]).any()
    assert clean["text_original"].str.len().min() > 0


def test_models_and_groups(tmp_path):
    cfg = json.loads(json.dumps(CFG))
    for k in ("tables_dir", "figures_dir", "models_dir", "reports_dir"):
        cfg["paths"][k] = str(tmp_path / k)
    cfg["models"]["seeds"] = [1]
    cfg["models"]["bootstrap"] = 20
    res = run_model_analysis(_clean_df(), cfg)
    assert res["status"] == "ok"
    assert {r["model"] for r in res["overall"]} == {"logreg", "linear_svm", "complement_nb"}
    assert all(0 <= r["macro_f1_mean"] <= 1 for r in res["overall"])


def test_models_skip_tiny_data():
    res = run_model_analysis(_clean_df(30, 1).head(10), CFG)
    assert res["status"].startswith("skipped")


def test_guardrails():
    facts = {"a": 12.34, "b": {"13-17": 5}}
    assert verify_numbers("Value 12.3 and 5 in 13-17.", facts)["ok"]
    assert not verify_numbers("Value 99.", facts)["ok"]
    assert not check_safety("You are depressed and need medication.")["ok"]
    assert check_safety("This is not a diagnosis.")["ok"]


def test_offline_summary_passes_own_guardrails():
    analysis = {
        "rows": 500,
        "age_analysis_O1_O2": {"status": "ok", "rows_with_age": 480,
                               "group_sizes": {"13-17": 60, "18-25": 150},
                               "elevated_share_by_age_band_pct": {"13-17": 40.123, "18-25": 22.456},
                               "label_vs_age_chi_square": {"p_value": 0.0123, "cramers_v": 0.1234}},
        "language_analysis_O3": {"language_counts": {"en": 300, "hi": 20}, "code_mixed_share_pct": 12.345},
    }
    facts = build_facts(analysis, None, ["sample_x.csv"], 30)
    text = offline_summary(facts)
    assert verify_numbers(text, facts)["ok"] and check_safety(text)["ok"]
    assert "hi (20)" not in text


def test_awareness_bank_complete():
    assert set(BANK) == set(DISCLAIMER) == {"en", "hi", "mr"}
    for tones in BANK.values():
        assert set(tones) == {"teen", "young_adult", "adult", "older"}
        assert all(check_safety(t)["ok"] for t in tones.values())
