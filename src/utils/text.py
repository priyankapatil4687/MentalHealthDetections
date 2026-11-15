import re

# \w splits Devanagari words at vowel signs, so split on whitespace/punctuation instead.
_SPLIT = re.compile(r"[\s\.,!?;:()\[\]{}\"'\u201c\u201d\u2018\u2019\u0964|/\\\-]+")

FIRST_PERSON = {
    "i", "me", "my", "mine", "myself", "i'm", "i've", "i'd",
    "main", "mujhe", "mera", "meri", "mala", "mi", "maza", "majha",
    "मैं", "मुझे", "मेरा", "मेरी", "मैंने",
    "मी", "मला", "माझा", "माझी", "माझं",
}


def tokenize(text):
    return [t for t in _SPLIT.split(str(text).lower()) if t]


def text_features(text):
    toks = tokenize(text)
    n = len(toks)
    fp = sum(1 for t in toks if t in FIRST_PERSON)
    return {
        "word_count": n,
        "char_count": len(str(text)),
        "first_person_rate": fp / n if n else 0.0,
        "exclaim_count": str(text).count("!"),
    }
