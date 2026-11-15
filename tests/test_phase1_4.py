import pandas as pd
import pytest

from src.config import load_config
from src.data.clean import clean_dataframe, scrub_pii
from src.data.language import detect_language
from src.data.load import load_dataset, phq9_to_label
from src.data.synthetic import generate_base, make_messy, write_all
from src.utils.stats import benjamini_hochberg, wilson_ci

CFG = load_config()


def test_scrub_pii():
    t = scrub_pii("mail a.b@x.com see https://x.com/a call +91 98765 43210 hi @bob")
    assert "@" not in t.replace("<USER>", "") and "http" not in t and "98765" not in t
    for tok in ("<EMAIL>", "<URL>", "<PHONE>", "<USER>"):
        assert tok in t


@pytest.mark.parametrize("text,expected", [
    ("I feel sad and tired today", "en"),
    ("मुझे बहुत उदासी रहती है और नींद नहीं आती", "hi"),
    ("मला खूप उदास वाटतं आणि झोप येत नाही", "mr"),
    ("Mujhe bahut thak gaya hoon aur neend nahi aati", "hinglish"),
    ("Mala khup udas vatate ani zop yet nahi", "roman_mr"),
    ("12345 !!!", "unknown"),
])
def test_detect_language(text, expected):
    assert detect_language(text) == expected


def test_phq9_bands():
    assert [phq9_to_label(x) for x in (0, 4, 5, 9, 10, 19, 20, 27)] == [
        "none", "none", "mild", "mild", "moderate", "moderate", "severe", "severe"]
    assert phq9_to_label(28) is None and phq9_to_label("x") is None


def test_stats_helpers():
    lo, hi = wilson_ci(50, 100)
    assert 0.39 < lo < 0.41 and 0.59 < hi < 0.61
    adj = benjamini_hochberg([0.01, 0.04, 0.03])
    assert all(a >= p for a, p in zip(adj, [0.01, 0.04, 0.03]))


def test_clean_messy_data():
    base = generate_base(400, 1)
    df = make_messy(base, 1).assign(age_band=pd.NA, source="t")
    clean, rep = clean_dataframe(df, CFG)
    assert rep["rows_output"] == len(clean) < len(df)
    assert not clean["text_clean"].str.contains(r"@|https?://|\d{10}", regex=True).any()
    assert set(clean["label"]) <= {"none", "mild", "moderate", "severe"}
    assert clean["age"].dropna().between(13, 100).all()
    assert (clean.loc[clean["age"].isna(), "age_band"] == "unknown").all()
    assert not clean["text_clean"].str.lower().duplicated().any()
    assert (clean["text_original"] != clean["text_clean"]).any()


def test_all_sample_formats_load(tmp_path):
    written = write_all(tmp_path, 7)
    for name in written:
        df, mapping = load_dataset(tmp_path / name)
        assert len(df) > 0 and {"text", "label"} <= set(mapping)
        clean, rep = clean_dataframe(df, CFG)
        assert len(clean) > 0
    df, _ = load_dataset(tmp_path / "sample_no_age.csv")
    clean, _ = clean_dataframe(df, CFG)
    assert (clean["age_band"] == "unknown").all()
    survey, m = load_dataset(tmp_path / "sample_survey_trackC.csv")
    clean, _ = clean_dataframe(survey, CFG)
    assert "derived" in m["label"] and (clean["age_band"] != "unknown").all()


def test_missing_columns_give_clear_error(tmp_path):
    p = tmp_path / "bad.csv"
    pd.DataFrame({"foo": ["a"], "bar": ["b"]}).to_csv(p, index=False)
    with pytest.raises(ValueError, match="No text column"):
        load_dataset(p)


def test_language_detector_accuracy_on_synthetic():
    base = generate_base(600, 3)
    pred = base["text"].map(detect_language)
    assert (pred == base["language"]).mean() >= 0.95
