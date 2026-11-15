import pandas as pd
import pytest

from src.data.open_datasets import extract_stated_age, prepare_brighter, prepare_reddit_mh, age_validation_sample


@pytest.mark.parametrize("text,expected", [
    ("I (24F) have felt low", 24),
    ("Hi, 31M here and tired", 31),
    ("I am 19 and failing exams", 19),
    ("I'm 45 years old", 45),
    ("I have 20 dollars", None),
    ("I am 10 minutes late", None),
    ("my brother is 30", None),
    ("I am 95", None),
    ("", None),
])
def test_extract_stated_age(text, expected):
    assert extract_stated_age(text) == expected


def test_prepare_brighter_proxy_labels():
    raw = pd.DataFrame({"id": ["a", "b", "c"], "text": ["x", "y", "z"], "anger": [1, 0, 0],
                        "fear": [0, 0, 0], "joy": [0, 1, 0], "sadness": [0, 0, 1], "surprise": [0, 0, 0]})
    out = prepare_brighter(raw, "hin")
    assert out["label"].tolist() == ["neutral_or_other", "neutral_or_other", "negative_affect"]
    assert (out["language"] == "hi").all() and out["age"].isna().all()


def test_prepare_reddit_hashes_authors_and_labels(tmp_path):
    f = tmp_path / "d.csv"
    pd.DataFrame({"subreddit": ["depression", "fitness"], "author": ["alice", "bob"],
                  "post": ["I (24F) feel hopeless and tired today, nothing helps.", "Leg day was great today, hit a new record."]}
                 ).to_csv(f, index=False)
    out = prepare_reddit_mh([f], positive=["depression"])
    assert out["label"].tolist() == ["mh_forum", "control"]
    assert not out["source_id"].str.contains("alice|bob").any()
    assert out.loc[0, "age"] == 24 and pd.isna(out.loc[1, "age"])
    assert len(age_validation_sample(out)) == 1
