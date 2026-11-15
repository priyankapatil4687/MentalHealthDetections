import re

# Conservative: only well-known spelling variants of Romanized Hindi/Marathi words.
VARIANTS = {
    "nahin": "nahi", "nai": "nahi", "nahee": "nahi", "nhi": "nahi",
    "hain": "hai", "mujhey": "mujhe", "muje": "mujhe", "mujhko": "mujhe",
    "bohot": "bahut", "bahot": "bahut", "bhot": "bahut",
    "kuchh": "kuch", "kucch": "kuch",
    "udaas": "udas", "nind": "neend", "nend": "neend",
    "khoop": "khup", "aahey": "aahe", "ahe": "aahe", "mla": "mala",
    "aani": "ani", "jhop": "zop",
}
INVERSE = {}
for _v, _c in VARIANTS.items():
    INVERSE.setdefault(_c, []).append(_v)

_WORD = re.compile(r"[A-Za-z]+")
_ELONGATION = re.compile(r"([A-Za-z])\1{2,}")
ROMAN_LANGS = {"hinglish", "roman_mr", "code_mixed"}


def normalize_roman(text):
    """Collapse letter elongation and map known spelling variants. Original text is kept elsewhere."""
    t = _ELONGATION.sub(r"\1\1", str(text))

    def repl(m):
        w = m.group(0)
        return VARIANTS.get(w.lower(), w)

    return _WORD.sub(repl, t)


def normalize_for_nlp(text, language):
    return normalize_roman(text) if language in ROMAN_LANGS else text
