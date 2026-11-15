"""Synthetic test-data generator.

The data is invented to exercise the code in different file formats. It is
NOT real and must never be used as evidence for research conclusions.
"""
import json
import random

import numpy as np
import pandas as pd

from src.data.normalize import INVERSE

LABELS = ["none", "mild", "moderate", "severe"]
BANDS = [("13-17", 13, 17, 0.12), ("18-25", 18, 25, 0.30), ("26-35", 26, 35, 0.25),
         ("36-45", 36, 45, 0.18), ("46+", 46, 65, 0.15)]
LABEL_PROBS = {
    "13-17": [0.30, 0.30, 0.25, 0.15],
    "18-25": [0.30, 0.30, 0.25, 0.15],
    "26-35": [0.38, 0.30, 0.20, 0.12],
    "36-45": [0.42, 0.30, 0.18, 0.10],
    "46+": [0.48, 0.28, 0.16, 0.08],
}
LANGS = ["en", "hi", "mr", "hinglish", "roman_mr"]
LANG_PROBS = [0.40, 0.15, 0.15, 0.20, 0.10]

CORE = {
    "en": {
        "none": ["I had a good day today and feel relaxed.", "Feeling happy and full of energy, spent time with friends.", "Life is going well and I am sleeping fine."],
        "mild": ["Feeling a bit low and tired lately.", "I worry sometimes and cannot focus much.", "I am not very motivated this week."],
        "moderate": ["I feel sad most days and I cannot sleep properly.", "Nothing feels enjoyable anymore and I feel exhausted.", "I feel anxious and alone all the time."],
        "severe": ["I feel hopeless and empty, everything feels pointless.", "I cannot cope any more and I feel worthless.", "I have no energy and nothing matters to me."],
    },
    "hi": {
        "none": ["आज मैं बहुत खुश हूँ और अच्छा महसूस कर रहा हूँ।", "सब कुछ ठीक चल रहा है और मैं आराम से सोता हूँ।", "दोस्तों के साथ समय बिताकर मुझे अच्छा लगा।"],
        "mild": ["आजकल थोड़ा उदास और थका हुआ महसूस होता है।", "कुछ दिनों से मन नहीं लगता है।", "इस हफ़्ते मुझे कुछ करने का मन नहीं है।"],
        "moderate": ["मुझे ज़्यादातर दिन उदासी रहती है और नींद नहीं आती।", "अब किसी चीज़ में मज़ा नहीं आता और मैं बहुत थका हूँ।", "मुझे हर समय घबराहट और अकेलापन महसूस होता है।"],
        "severe": ["मुझे कोई उम्मीद नहीं दिखती और सब कुछ बेकार लगता है।", "मैं अब सँभाल नहीं पा रहा और खुद को बेकार समझता हूँ।", "मुझमें कोई ताकत नहीं है और कुछ भी मायने नहीं रखता।"],
    },
    "mr": {
        "none": ["आज मी खूप आनंदी आहे आणि मला छान वाटत आहे.", "सगळं व्यवस्थित सुरू आहे आणि मला शांत झोप लागते.", "मित्रांसोबत वेळ घालवून मला बरं वाटलं."],
        "mild": ["हल्ली मला थोडं उदास आणि थकल्यासारखं वाटतं.", "काही दिवसांपासून कशातच मन लागत नाही.", "या आठवड्यात मला काही करायची इच्छा नाही."],
        "moderate": ["मला बहुतेक दिवस उदास वाटतं आणि झोप येत नाही.", "आता कशातच मजा वाटत नाही आणि मी खूप थकलो आहे.", "मला सतत चिंता आणि एकटेपणा वाटतो."],
        "severe": ["मला कोणतीही आशा दिसत नाही आणि सगळं निरर्थक वाटतं.", "मी आता सहन करू शकत नाही आणि स्वतःला निरुपयोगी समजतो.", "माझ्यात ताकद नाही आणि काहीच महत्त्वाचं वाटत नाही."],
    },
    "hinglish": {
        "none": ["Aaj main bahut khush hoon aur sab kuch theek chal raha hai.", "Friends ke saath time spend kiya, mujhe accha lag raha hai.", "Sab kuch accha hai aur neend bhi poori hoti hai."],
        "mild": ["Aajkal thoda low aur tired feel hota hai.", "Kuch din se kisi cheez mein mann nahi lag raha.", "Is week mujhe kuch karne ka mann nahi hai."],
        "moderate": ["Mujhe zyada tar din sad lagta hai aur neend nahi aati.", "Ab kisi cheez mein maza nahi aata, bahut thak gaya hoon.", "Mujhe hamesha anxiety aur akelapan feel hota hai."],
        "severe": ["Mujhe koi hope nahi dikhti, sab kuch bekar lagta hai.", "Main ab handle nahi kar pa raha aur khud ko bekar samajhta hoon.", "Mujhmein koi energy nahi hai, kuch bhi matter nahi karta."],
    },
    "roman_mr": {
        "none": ["Aaj mi khup khush aahe ani mala chhan vatat aahe.", "Sagla vyavasthit chalu aahe ani mala shant zop lagte.", "Mitranbarobar vel ghalvun mala bara vatla."],
        "mild": ["Halli mala thoda udas ani thaklyasarkhe vatate.", "Kahi divasanpasun kashat mann lagat nahi.", "Ya athvadyat mala kahi karnyachi ichha nahi."],
        "moderate": ["Mala bahutek divas udas vatate ani zop yet nahi.", "Aata kashat maja vatat nahi ani mi khup thaklo aahe.", "Mala satat chinta ani ekatepana vatato."],
        "severe": ["Mala konatihi asha disat nahi ani sagla nirarthak vatate.", "Mi aata sahan karu shakat nahi ani swatahla nirupayogi samajto.", "Majhyat takat nahi ani kahich mahattvache vatat nahi."],
    },
}

OPENERS = {
    "en": ["", "Honestly, ", "To be frank, "],
    "hi": ["", "सच कहूँ तो ", "आजकल "],
    "mr": ["", "खरं सांगायचं तर ", "हल्ली "],
    "hinglish": ["", "Honestly, ", "Sach bolun toh "],
    "roman_mr": ["", "Khar sangayche tar ", "Halli "],
}
CLOSERS = {
    "en": ["", " I wanted to write this down.", " Not sure why I am sharing this."],
    "hi": ["", " बस यही लिखना था।", " पता नहीं क्यों बता रहा हूँ।"],
    "mr": ["", " हेच लिहायचं होतं.", " का सांगतोय माहीत नाही."],
    "hinglish": ["", " Bas yahi likhna tha.", " Pata nahi kyun share kar raha hoon."],
    "roman_mr": ["", " Hech lihaycha hota.", " Ka sangtoy mahit nahi."],
}
TOPICS_EN = {
    "13-17": ["Exams and school pressure are stressing me out.", "My parents keep comparing me to others."],
    "18-25": ["College results and internship worries are on my mind.", "Placement season is making me nervous."],
    "26-35": ["Work deadlines and rent are piling up.", "My job feels demanding."],
    "36-45": ["Managing family responsibilities and my job is hard.", "Loans and children's studies worry me."],
    "46+": ["Health worries and retirement planning bother me.", "My children live far away."],
}
TOPICS_HINGLISH = {
    "13-17": ["Exams ka pressure bahut hai.", "Ghar mein comparison hota rehta hai."],
    "18-25": ["College aur placement ki tension hai.", "Internship ka stress hai."],
    "26-35": ["Office ke deadlines aur EMI ka stress hai.", "Job bahut demanding hai."],
    "36-45": ["Ghar aur job dono sambhalna mushkil hai.", "Loan aur bachchon ki padhai ki chinta hai."],
    "46+": ["Health aur retirement ki chinta rehti hai.", "Bachche door rehte hain."],
}


def _make_text(rng, lang, label, band, used):
    for _ in range(40):
        core = rng.choice(CORE[lang][label])
        if rng.random() < 0.6:
            second = rng.choice(CORE[lang][label])
            if second != core:
                core = f"{core} {second}"
        topic = ""
        if rng.random() < 0.5:
            if lang == "en":
                topic = " " + rng.choice(TOPICS_EN[band])
            elif lang == "hinglish":
                topic = " " + rng.choice(TOPICS_HINGLISH[band])
        text = rng.choice(OPENERS[lang]) + core + topic + rng.choice(CLOSERS[lang])
        if text not in used:
            used.add(text)
            return text
    return text


def generate_base(n=1200, seed=42, label_noise=0.2):
    """Clean canonical dataset: source_id, text, label, age, language (+ true age_band)."""
    rng = random.Random(seed)
    nprng = np.random.default_rng(seed)
    n_users = max(10, n // 2)
    users = []
    for u in range(n_users):
        band = BANDS[nprng.choice(len(BANDS), p=[b[3] for b in BANDS])]
        users.append({
            "source_id": f"user_{u:04d}",
            "age": int(nprng.integers(band[1], band[2] + 1)),
            "band": band[0],
            "lang": LANGS[nprng.choice(len(LANGS), p=LANG_PROBS)],
        })
    used, rows = set(), []
    for _ in range(n):
        u = users[int(nprng.integers(0, n_users))]
        label = LABELS[nprng.choice(4, p=LABEL_PROBS[u["band"]])]
        style = label
        if rng.random() < label_noise:  # ambiguous wording so models are not trivially perfect
            style = LABELS[min(3, max(0, LABELS.index(label) + rng.choice([-1, 1])))]
        rows.append({
            "source_id": u["source_id"],
            "text": _make_text(rng, u["lang"], style, u["band"], used),
            "label": label,
            "age": u["age"],
            "language": u["lang"],
        })
    return pd.DataFrame(rows)


def make_messy(base, seed=42):
    """Dirty version: PII, duplicates, missing values, bad ages, label/language aliases, conflicts."""
    rng = random.Random(seed)
    d = base.copy().astype({"age": "object"})
    n = len(d)
    pii = [" Contact me at test.user@example.com.", " See https://example.com/post/123 for more.",
           " Call me on +91 98765 43210.", " Thanks @someuser for listening."]
    for i in rng.sample(range(n), int(0.15 * n)):
        d.loc[i, "text"] = d.loc[i, "text"] + rng.choice(pii)
    bad_age = [5, 150, -3, "twenty", "", "N/A"]
    for i in rng.sample(range(n), int(0.04 * n)):
        d.loc[i, "age"] = rng.choice(bad_age)
    for i in rng.sample(range(n), int(0.03 * n)):
        d.loc[i, "text"] = rng.choice([None, "", "   "])
    for i in rng.sample(range(n), int(0.02 * n)):
        d.loc[i, "label"] = None
    for i in rng.sample(range(n), int(0.05 * n)):
        d.loc[i, "label"] = rng.choice([" Mild ", "NONE", "Moderate", "Normal", "SEVERE"])
    names = {"en": "English", "hi": "Hindi", "mr": "Marathi", "hinglish": "Hinglish", "roman_mr": "Romanized Marathi"}
    for i in rng.sample(range(n), int(0.25 * n)):
        d.loc[i, "language"] = names.get(d.loc[i, "language"], d.loc[i, "language"])
    for i in rng.sample(range(n), int(0.30 * n)):
        d.loc[i, "language"] = None
    dups = d.sample(int(0.05 * n), random_state=seed)
    conflict = d.sample(6, random_state=seed + 1).copy()
    conflict["label"] = conflict["label"].map(lambda x: "severe" if x != "severe" else "none")
    d = pd.concat([d, dups, conflict], ignore_index=True)
    return d.sample(frac=1, random_state=seed).reset_index(drop=True)


def make_survey(base, n=300, seed=42):
    """Track C style: survey export with age band, language name, free text, PHQ-9 score."""
    rng = random.Random(seed)
    s = base.sample(n, random_state=seed).reset_index(drop=True)
    rng_ranges = {"none": (0, 4), "mild": (5, 9), "moderate": (10, 19), "severe": (20, 27)}
    names = {"en": "English", "hi": "Hindi", "mr": "Marathi", "hinglish": "Hinglish", "roman_mr": "Hinglish"}
    band = s["age"].map(lambda a: next(b[0] for b in BANDS if b[1] <= a <= b[2]))
    return pd.DataFrame({
        "response_id": [f"R{i:04d}" for i in range(n)],
        "age_band": band,
        "preferred_language": s["language"].map(names),
        "mood_text": s["text"],
        "phq9_score": [rng.randint(*rng_ranges[l]) for l in s["label"]],
    })


def make_codemixed_noisy(base, seed=42):
    """Romanized rows with spelling variants and letter elongation, to test normalization."""
    rng = random.Random(seed)
    sub = base[base["language"].isin(["hinglish", "roman_mr"])].copy()

    def noisy(text):
        out = []
        for w in text.split(" "):
            core = w.strip(".,!?").lower()
            if core in INVERSE and rng.random() < 0.6:
                w = w.lower().replace(core, rng.choice(INVERSE[core]))
            elif rng.random() < 0.05 and len(w) > 3:
                w = w + w[-1] * 2
            out.append(w)
        return " ".join(out)

    sub["text"] = sub["text"].map(noisy)
    return sub.reset_index(drop=True)


def write_all(out_dir, seed=42):
    """Write sample files in several formats. Returns {filename: description}."""
    out_dir.mkdir(parents=True, exist_ok=True)
    base = generate_base(1200, seed)
    written = {}

    base.to_csv(out_dir / "sample_clean.csv", index=False, encoding="utf-8-sig")
    written["sample_clean.csv"] = "1200 clean rows: source_id,text,label,age,language"

    make_messy(base, seed).to_csv(out_dir / "sample_messy.csv", index=False, encoding="utf-8-sig")
    written["sample_messy.csv"] = "dirty: PII, duplicates, missing, bad ages, label/language aliases, conflicts"

    sub = base.sample(400, random_state=seed)
    sub.rename(columns={"text": "post", "label": "diagnosis", "age": "years",
                        "language": "lang", "source_id": "user_id"}).to_excel(
        out_dir / "sample_alt_columns.xlsx", index=False)
    written["sample_alt_columns.xlsx"] = "Excel with alternative column names (post, diagnosis, years, lang, user_id)"

    small = base.sample(300, random_state=seed + 1)
    small.to_csv(out_dir / "sample.tsv", sep="\t", index=False, encoding="utf-8-sig")
    written["sample.tsv"] = "300 rows, tab-separated"
    with open(out_dir / "sample.jsonl", "w", encoding="utf-8") as f:
        for rec in small.to_dict("records"):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    written["sample.jsonl"] = "300 rows, JSON Lines"
    with open(out_dir / "sample.json", "w", encoding="utf-8") as f:
        json.dump({"records": small.to_dict("records")}, f, ensure_ascii=False, indent=1)
    written["sample.json"] = "300 rows, JSON {'records': [...]}"

    base.drop(columns=["age"]).to_csv(out_dir / "sample_no_age.csv", index=False, encoding="utf-8-sig")
    written["sample_no_age.csv"] = "no age column (tests honest 'age analysis unavailable')"

    make_survey(base, 300, seed).to_csv(out_dir / "sample_survey_trackC.csv", index=False, encoding="utf-8-sig")
    written["sample_survey_trackC.csv"] = "survey layout: response_id, age_band, preferred_language, mood_text, phq9_score"
    make_codemixed_noisy(base, seed).to_csv(out_dir / "sample_codemixed_noisy.csv", index=False, encoding="utf-8-sig")
    written["sample_codemixed_noisy.csv"] = "Romanized rows with spelling variants (tests normalization)"
    return written
