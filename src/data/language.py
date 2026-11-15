import re

from src.utils.text import tokenize

_DEVA = re.compile(r"[\u0900-\u097F]")
_LATIN = re.compile(r"[A-Za-z]")

HI_DEVA = {"है", "हैं", "नहीं", "मैं", "मुझे", "और", "हूँ", "कुछ", "बहुत", "रहा", "रही", "था", "में", "को", "का", "की", "से"}
MR_DEVA = {"आहे", "आणि", "मला", "नाही", "काय", "खूप", "वाटतं", "वाटत", "होता", "आम्ही", "मी", "आता", "सगळं", "कशातच"}

HI_ROMAN = {
    "hai", "hoon", "hun", "mujhe", "mera", "meri", "bahut", "kuch", "raha", "rahi", "lagta", "lagti",
    "neend", "aur", "mein", "aaj", "aajkal", "thoda", "zyada", "kisi", "cheez", "bekar", "maza",
    "mann", "samajhta", "mushkil", "chinta", "kiya", "saath", "ke", "ki", "ka", "se", "dikhti",
    "dikhta", "gaya", "khud", "koi", "dono", "rehti", "thak", "accha", "sab", "ab",
}
MR_ROMAN = {
    "mala", "aahe", "ahe", "ani", "khup", "kay", "vatat", "vatate", "vatta", "zop", "udas", "thaklo",
    "thaklyasarkhe", "kashat", "kahi", "divasanpasun", "halli", "aata", "sagla", "chhan", "shant",
    "bahutek", "divas", "nirarthak", "asha", "disat", "konatihi", "swatahla", "samajto", "sahan",
    "shakat", "yet", "lagat", "lagte", "maja", "vyavasthit", "chalu",
}

LANG_ALIASES = {
    "english": "en", "en": "en", "eng": "en",
    "hindi": "hi", "hi": "hi",
    "marathi": "mr", "mr": "mr",
    "hinglish": "hinglish", "hi-en": "hinglish", "hindi-english": "hinglish",
    "roman_mr": "roman_mr", "romanized marathi": "roman_mr", "marathi-roman": "roman_mr",
    "code_mixed": "code_mixed", "code-mixed": "code_mixed",
}

CODE_MIXED_LANGS = {"hinglish", "roman_mr", "code_mixed"}


def detect_language(text):
    """Rule-based script and marker-word language hint. Support only, not ground truth.

    Returns: en, hi, mr, hinglish, roman_mr, code_mixed, deva_unknown or unknown.
    """
    s = str(text)
    deva = len(_DEVA.findall(s))
    latin = len(_LATIN.findall(s))
    if deva + latin == 0:
        return "unknown"
    toks = tokenize(s)
    frac = deva / (deva + latin)
    if frac > 0.7:
        hi = sum(t in HI_DEVA for t in toks)
        mr = sum(t in MR_DEVA for t in toks)
        if hi > mr:
            return "hi"
        if mr > hi:
            return "mr"
        return "deva_unknown"
    if frac > 0.1:
        return "code_mixed"
    hi = sum(t in HI_ROMAN for t in toks)
    mr = sum(t in MR_ROMAN for t in toks)
    hits = max(hi, mr)
    if hits >= 2 or (hits == 1 and len(toks) <= 6):
        return "roman_mr" if mr > hi else "hinglish"
    return "en"


def normalize_language_name(value):
    if value is None:
        return None
    key = str(value).strip().lower()
    return LANG_ALIASES.get(key)
