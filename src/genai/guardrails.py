import re

_NUM = re.compile(r"\d+(?:\.\d+)?")
BANNED = re.compile(
    r"\b(diagnosed with|diagnoses you|prescrib\w*|medicat\w*|dosage|you have (depression|anxiety)|you are (depressed|mentally ill)|"
    r"cure[sd]?|treatment plan)\b", re.I)


def _collect(obj, out):
    if isinstance(obj, bool) or obj is None:
        return
    if isinstance(obj, (int, float)):
        out.append(float(obj))
    elif isinstance(obj, str):
        out.extend(float(x) for x in _NUM.findall(obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _collect(str(k), out)
            _collect(v, out)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _collect(v, out)


def allowed_numbers(facts):
    vals = []
    _collect(facts, vals)
    return vals


def verify_numbers(text, facts):
    """Every number in generated text must match a number in the facts (at the number's own precision)."""
    allowed = allowed_numbers(facts)
    bad = []
    for tok in _NUM.findall(text):
        d = len(tok.split(".")[1]) if "." in tok else 0
        x = float(tok)
        if not any(round(v, d) == x or abs(round(v, d) - x) < 1e-9 for v in allowed):
            bad.append(tok)
    return {"ok": not bad, "unverified_numbers": bad, "numbers_checked": len(_NUM.findall(text))}


def check_safety(text):
    hits = sorted({m.group(0).lower() for m in BANNED.finditer(text)})
    return {"ok": not hits, "banned_phrases_found": hits}
