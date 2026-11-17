"""Build the Mini Project-I presentation from the D. Y. Patil PPT template."""
import copy
import os
import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.opc.packuri import PackURI
from pptx.dml.color import RGBColor
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
from report_content1 import TITLE  # noqa: E402

TEMPLATE = os.environ.get("PPT_TEMPLATE", os.environ["TEMP"] + r"\tpl\tpl.pptx")
OUT = ROOT / "report" / "MiniProject_I_Presentation.pptx"
F = ROOT / "report" / "figures"
UI = F / "ui"
NAVY = RGBColor(0x1F, 0x2D, 0x5C)
GREY = RGBColor(0x55, 0x55, 0x55)

prs = Presentation(TEMPLATE)
LAYOUT = prs.slides[2].slide_layout  # Title and Content

# keep title (1), literature table (5) and thank-you (14); the rest are rebuilt
KEEP = {0, 4, 13}
ids = prs.slides._sldIdLst
orig = list(ids)
for i, sid in enumerate(orig):
    if i not in KEEP:
        prs.part.drop_rel(sid.rId)
        ids.remove(sid)
title_el, lit_el, thanks_el = [e for e in ids]
for n, sl in zip((901, 902, 903), prs.slides):
    sl.part.partname = PackURI("/ppt/slides/slide%d.xml" % n)


def set_title(slide, text, size=32):
    t = slide.shapes.title
    t.text_frame.text = text
    for p in t.text_frame.paragraphs:
        for r in p.runs:
            r.font.size = Pt(size)
    t.left, t.top, t.width, t.height = Inches(0.5), Inches(0.25), Inches(9.0), Inches(0.9)


def bullets(frame, items, size=20, color=None):
    frame.clear()
    frame.word_wrap = True
    first = True
    for it in items:
        sub = it.startswith("- ")
        txt = it[2:] if sub else it
        p = frame.paragraphs[0] if first else frame.add_paragraph()
        first = False
        p.level = 1 if sub else 0
        r = p.add_run()
        r.text = txt
        r.font.size = Pt(size - 3 if sub else size)
        if color:
            r.font.color.rgb = color
        p.space_after = Pt(6)


def add_slide(title, items=None, size=20, box=(0.6, 1.3, 8.8, 5.4), tsize=32):
    s = prs.slides.add_slide(LAYOUT)
    set_title(s, title, tsize)
    body = s.placeholders[1]
    for ph in list(s.placeholders):
        if ph.placeholder_format.idx not in (0, 1):
            ph._element.getparent().remove(ph._element)
    if items is None:
        body._element.getparent().remove(body._element)
    else:
        body.left, body.top, body.width, body.height = [Inches(v) for v in box]
        bullets(body.text_frame, items, size if size <= 14 else size + 3)
    return s


def add_pic(slide, path, x, y, w, h, caption=None):
    im = Image.open(path)
    ar = im.width / im.height
    pw, ph = w, w / ar
    if ph > h:
        ph, pw = h, h * ar
    px, py = x + (w - pw) / 2, y + (h - ph) / 2
    slide.shapes.add_picture(str(path), Inches(px), Inches(py), Inches(pw), Inches(ph))
    if caption:
        tb = slide.shapes.add_textbox(Inches(x), Inches(y + h), Inches(w), Inches(0.35))
        p = tb.text_frame.paragraphs[0]
        p.alignment = 2
        r = p.add_run()
        r.text = caption
        r.font.size = Pt(12)
        r.font.italic = True
        r.font.color.rgb = GREY


def add_note(slide, text, y=6.55, size=12):
    tb = slide.shapes.add_textbox(Inches(0.6), Inches(y), Inches(8.8), Inches(0.5))
    tb.text_frame.word_wrap = True
    r = tb.text_frame.paragraphs[0].add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.italic = True
    r.font.color.rgb = GREY


def add_table(slide, header, rows, col_w, x=0.4, y=1.35, size=11, row_h=0.4):
    gt = slide.shapes.add_table(len(rows) + 1, len(header), Inches(x), Inches(y),
                                Inches(sum(col_w)), Inches(row_h * (len(rows) + 1)))
    t = gt.table
    for j, w in enumerate(col_w):
        t.columns[j].width = Inches(w)
    for j, h in enumerate(header):
        c = t.cell(0, j)
        c.text = h
        for r in c.text_frame.paragraphs[0].runs:
            r.font.size = Pt(size)
            r.font.bold = True
    for i, row in enumerate(rows, 1):
        for j, v in enumerate(row):
            c = t.cell(i, j)
            c.text = str(v)
            for p in c.text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(size)
    return t


# ---------------- slide 1: title
s = prs.slides[0]
for sh in s.shapes:
    if sh.is_placeholder and sh.placeholder_format.idx == 0:
        sh.text_frame.text = "A\nMini Project - I Presentation\non"
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(20)
    elif sh.is_placeholder and sh.placeholder_format.idx == 1:
        tf = sh.text_frame
        lines = [("\u201c" + TITLE + "\u201d", 26, False),
                 ("Presented by", 18, True),
                 ("<Student Name> : <PRN No.>", 20, False),
                 ("Under the guidance of", 18, True),
                 ("Prof. Dr. <Guide Name>", 20, False),
                 ("Department of Computer Engineering (AIML)", 18, False),
                 ("School of Engineering & Technology", 18, False),
                 ("D.Y. Patil University, Pune.", 18, False),
                 ("Academic Year 2026-27", 18, False)]
        tf.clear()
        for k, (txt, sz, it) in enumerate(lines):
            p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            p.alignment = 2
            r = p.add_run()
            r.text = txt
            r.font.size = Pt(sz)
            r.font.italic = it
            r.font.color.rgb = NAVY
            p.space_after = Pt(8)
            ppr = p._p.get_or_add_pPr()
            ppr.set("marL", "0")
            ppr.set("indent", "0")
            for ch in list(ppr):
                if ch.tag.split("}")[1] in ("buFont", "buChar", "buAutoNum", "buNone"):
                    ppr.remove(ch)
            ppr.append(ppr.makeelement("{http://schemas.openxmlformats.org/drawingml/2006/main}buNone", {}))

# ---------------- literature slide (template table)
ls = None
for sl in prs.slides:
    if any(sh.has_table for sh in sl.shapes if hasattr(sh, "has_table")):
        ls = sl
tbl_shape = [sh for sh in ls.shapes if getattr(sh, "has_table", False)][0]
tbl = tbl_shape.table
LIT = [
    ("1", "Low et al. (2020)", "NLP reveals vulnerable mental-health support groups (COVID-19)", "J. Med. Internet Res.", "Reddit; LIWC, topic models, classifiers", "English only; no age or language split"),
    ("2", "Yates, Cohan, Goharian (2017)", "Depression and self-harm risk assessment in online forums (RSDD)", "EMNLP 2017", "Self-reported diagnoses; CNN / linear models", "No age field; restricted access"),
    ("3", "Schler et al. (2006)", "Effects of age and gender on blogging", "AAAI Spring Symp.", "Blog corpus; word-use differences by age", "Not mental-health; English"),
    ("4", "Aguirre, Harrigian, Dredze (2021)", "Gender and racial fairness in depression research", "EACL 2021", "Fairness audit of depression models", "Age and Indian languages not covered"),
    ("5", "Muhammad et al. (2025)", "BRIGHTER: emotion data for 28 languages", "arXiv:2502.11926", "Annotated emotion data incl. Hindi, Marathi", "Emotion labels, not diagnosis; no age"),
    ("6", "Ji et al.; Yang et al.; Xu et al.", "MentalBERT; MentaLLaMA; Mental-LLM", "LREC 2022; WWW 2024; IMWUT 2024", "Domain-adapted and instruction-tuned LMs", "Raw text to models; hallucination risk"),
]
# template has header + 2 body rows: clone a body row to reach len(LIT) rows
tr_lst = tbl._tbl.tr_lst
while len(tbl._tbl.tr_lst) < len(LIT) + 1:
    tbl._tbl.append(copy.deepcopy(tr_lst[1 + (len(tbl._tbl.tr_lst) % 2)]))
widths = [0.5, 1.3, 2.1, 1.3, 2.1, 2.0]
for j, w in enumerate(widths):
    tbl.columns[j].width = Inches(w)
for i, row in enumerate(LIT, 1):
    tbl.rows[i].height = Inches(0.8)
    for j, v in enumerate(row):
        c = tbl.cell(i, j)
        c.text = v
        for p in c.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(11)
tbl.rows[0].height = Inches(0.5)
for j in range(6):
    for p in tbl.cell(0, j).text_frame.paragraphs:
        for r in p.runs:
            r.font.size = Pt(12)
tbl_shape.left, tbl_shape.top, tbl_shape.width = Inches(0.3), Inches(1.0), Inches(sum(widths))
# remove date/number placeholders overlapping the table
for sh in list(ls.shapes):
    if sh.is_placeholder and sh.placeholder_format.idx in (10, 12):
        sh._element.getparent().remove(sh._element)
ls.shapes.title.text_frame.text = "Literature Survey"
t_ = ls.shapes.title
t_.left, t_.top, t_.width, t_.height = Inches(0.5), Inches(0.2), Inches(9.0), Inches(0.7)
for p in ls.shapes.title.text_frame.paragraphs:
    for r in p.runs:
        r.font.size = Pt(30)

# ---------------- new slides
new = []


def reg(s):
    new.append(s)
    return s


reg(add_slide("Presentation Outline", [
    "Introduction and Problem Statement", "Objectives", "Literature Survey and Research Gap",
    "Proposed Block Diagram and Methodology", "Data Flow and Algorithm", "Datasets and Experimental Set-up",
    "Results and Discussion", "Dashboard, Applications", "Conclusions, Future Scope and References"], 22))

reg(add_slide("Introduction", [
    "Mental-health distress is common and under-reported; people express it in text on social media and chats.",
    "Writing style differs by age (teenagers vs older adults) and by language (English, Hindi, Marathi, Hinglish).",
    "Most existing work: English only, one pooled accuracy score, no age or language breakdown.",
    "A single overall score can hide large gaps between groups.",
    "This project builds a reproducible, privacy-preserving framework for age- and language-wise analysis, with a number-verified Generative AI layer.",
], 19))

reg(add_slide("Problem Statement and Objectives", [
    "Problem: design a framework that analyses mental-health-related text by age band and language, measures group-wise model fairness and explains results in plain language.",
    "O1 Age-wise text patterns    O2 Age-based risk analysis",
    "O3 Multilingual and code-mixed analysis    O4 Age x language analysis",
    "O5 Group-wise models, fairness gaps and explainability",
    "O6 GenAI age-wise insights    O7 GenAI multilingual awareness drafts",
    "Not a diagnostic tool: research and awareness only.",
], 18))

# literature slide goes here; research gap slide
reg(add_slide("Research Gap", [
    "Existing studies cover (i) English, (ii) pooled metrics, (iii) raw text sent to LLMs.",
    "No single study found that jointly combines:",
    "- age-band stratification and Hindi / Marathi / Romanized code-mixed text",
    "- group-wise performance with confidence intervals and fairness gaps",
    "- explainability and LLM output restricted to aggregated, number-verified statistics",
    "Gap claim is provisional; a systematic search is future work.",
], 20))

s = reg(add_slide("Proposed Block Diagram"))
add_pic(s, F / "fig_architecture.png", 0.4, 1.2, 9.2, 5.3, "Fig: Layered architecture of the proposed system")

reg(add_slide("Methodology", [
    "Pipeline: load and validate -> clean (PII scrub, de-duplicate, hash authors) -> language ID and normalisation -> O1-O4 analysis -> models -> GenAI layer.",
    "Features: word 1-2 gram + character 2-5 gram TF-IDF.",
    "Models: Logistic Regression, Linear SVM, Complement Naive Bayes.",
    "Validation: author-grouped stratified 5-fold CV, 3 seeds (42, 7, 2024), 200 bootstrap resamples.",
    "Statistics: Wilson CI, chi-square with Cramer's V, Benjamini-Hochberg.",
    "Hardware / Software: standard laptop, no GPU; Python 3.14, scikit-learn, pandas, Streamlit.",
], 17))

s = reg(add_slide("Schematic: Data Flow (Level 1)"))
add_pic(s, F / "fig_dfd1.png", 0.4, 1.3, 9.2, 5.0, "Fig: DFD level 1 - five processes and four data stores")

s = reg(add_slide("Flowchart / Algorithm"))
add_pic(s, F / "fig_flowchart.png", 0.3, 1.2, 5.4, 5.6)
tb = s.shapes.add_textbox(Inches(5.8), Inches(1.4), Inches(3.9), Inches(5))
tb.text_frame.word_wrap = True
bullets(tb.text_frame, [
    "Group by age band / language.",
    "Train on train fold only (no text leakage).",
    "Pool out-of-fold predictions.",
    "Skip groups with n < 100.",
    "Macro-F1 + 95% bootstrap CI per group.",
    "Fairness gap = max F1 - min F1.",
], 18)

reg(add_slide("Datasets and Experimental Set-up", [
    "Run A - synthetic sample (1,200 invented posts; age, language, 4 severity labels): validates the code only; NOT evidence about real people.",
    "Run B - BRIGHTER open emotion data: 7,500 posts (English, Hindi, Marathi) -> 6,662 after cleaning.",
    "- 836 exact duplicates, 2 conflicting-label duplicates, 2 PII rows removed",
    "- Label proxy: negative affect (sadness, fear) vs neutral / other; no age field",
    "Language detector agreement with provided language: 93.3% (Run B), 99.5% (Run A).",
    "39 automated tests pass.",
], 17))

s = reg(add_slide("Results: Run A (Synthetic, Code Validation)"))
add_pic(s, F / "chart_syn_age_elevated.png", 0.3, 1.3, 4.7, 4.2, "Elevated-label share by age band")
add_pic(s, F / "chart_model_comparison.png", 5.0, 1.3, 4.7, 4.2, "Macro-F1 by model")
add_note(s, "Pattern was built into the generator: 38.9% (13-17) ... 16.5% (46+); chi-square p = 4.8e-9, Cramer's V = 0.133. Label vs language: p = 0.84. The code recovers a known effect.", 5.95, 13)

s = reg(add_slide("Results: Run B (Real BRIGHTER Data)"))
add_pic(s, F / "chart_real_language_f1.png", 0.3, 1.3, 5.0, 4.3, "Macro-F1 by language (95% bootstrap CI)")
tb = s.shapes.add_textbox(Inches(5.4), Inches(1.4), Inches(4.3), Inches(4.5))
tb.text_frame.word_wrap = True
bullets(tb.text_frame, [
    "Best model: Linear SVM, macro-F1 0.816, MCC 0.632.",
    "English 0.626 vs Hindi 0.841 vs Marathi 0.887: gap 0.261.",
    "Negative-affect share: en 64.1%, hi 30.9%, mr 33.2% (V = 0.307).",
    "Naive Bayes: English macro-recall 0.5 = majority-class predictor.",
], 17)
add_note(s, "Overall score hides the weak English group. Labels are emotion proxies, not clinical diagnoses.", 6.0, 13)

s = reg(add_slide("Results: Fairness Gaps and Dashboard"))
add_pic(s, F / "chart_fairness_gaps.png", 0.3, 1.3, 4.6, 4.5, "Fairness gaps (max - min macro-F1)")
add_pic(s, UI / "ui_models.png", 5.0, 1.3, 4.7, 4.5, "Streamlit dashboard: model comparison")
add_note(s, "Streamlit dashboard has 8 pages: overview, age, language, age x language, models, explainability, GenAI, limitations.", 6.0, 13)

reg(add_slide("GenAI Layer and Guardrails", [
    "Generator receives only aggregated statistics (no raw text).",
    "verify_numbers: every number in the output must match a computed fact.",
    "check_safety: rejects clinical or directive phrases.",
    "On failure: fall back to a deterministic offline template.",
    "Run A check: 24 numbers verified, all matched; safety OK.",
    "12 awareness drafts (3 languages x 4 age groups) from a curated offline bank; all PENDING_HUMAN_REVIEW with a helpline placeholder.",
], 18))

reg(add_slide("Applications", [
    "Research on language- and age-aware mental-health NLP.",
    "Fairness auditing of text classifiers before deployment.",
    "Drafting multilingual, age-appropriate awareness material (human-reviewed).",
    "Campus wellbeing and public-health communication planning (aggregate level).",
    "Teaching template for reproducible, privacy-safe ML experiments.",
], 20))

reg(add_slide("Conclusions and Future Scope", [
    "A reproducible framework for age- and language-wise analysis was built and tested (39 tests).",
    "Synthetic run: pipeline recovers the planted age effect; code validated.",
    "Real BRIGHTER run: best model macro-F1 0.816, but 0.626 on English vs 0.841 / 0.887 on Hindi / Marathi - an overall score hides a 0.261 gap.",
    "Limits: proxy labels, no real age data, offline awareness bank, not diagnostic.",
    "Future: consented survey (Track C) with age and PHQ-9; transformer models (MuRIL, XLM-R); more Indian languages; live LLM with native-speaker review.",
], 17))

reg(add_slide("References", [
    "[1] A. Yates, A. Cohan, N. Goharian, \"Depression and self-harm risk assessment in online forums,\" EMNLP, 2017.",
    "[2] A. Cohan et al., \"SMHD: a large-scale resource for exploring online language usage for multiple mental health conditions,\" COLING, 2018.",
    "[3] D. E. Low et al., \"NLP reveals vulnerable mental health support groups ... during COVID-19,\" J. Med. Internet Res., 2020.",
    "[4] J. Schler et al., \"Effects of age and gender on blogging,\" AAAI Spring Symp., 2006.",
    "[5] C. Aguirre, K. Harrigian, M. Dredze, \"Gender and racial fairness in depression research using social media,\" EACL, 2021.",
    "[6] S. M. Muhammad et al., \"BRIGHTER: bridging the gap in human-annotated textual emotion recognition datasets for 28 languages,\" arXiv:2502.11926, 2025.",
    "[7] S. Khanuja et al., \"MuRIL: multilingual representations for Indian languages,\" arXiv:2103.10730, 2021.",
    "[8] F. Pedregosa et al., \"Scikit-learn: machine learning in Python,\" JMLR, 2011.",
], 14, box=(0.5, 1.2, 9.0, 5.6)))

# ---------------- ordering
order = [title_el] + [s.slide_id for s in new[:4]]
ids = prs.slides._sldIdLst
by_id = {int(e.get("id")): e for e in ids}
seq = [title_el]
seq += [by_id[s.slide_id] for s in new[:4]]  # outline, intro, problem, research-gap placeholder
# desired: title, outline, intro, problem, literature, gap, block ... thanks
seq = [title_el, by_id[new[0].slide_id], by_id[new[1].slide_id], by_id[new[2].slide_id], lit_el, by_id[new[3].slide_id]]
seq += [by_id[s.slide_id] for s in new[4:]]
seq.append(thanks_el)
for e in list(ids):
    ids.remove(e)
for e in seq:
    ids.append(e)

# slide numbers / date placeholders left out of new slides; remove stray date from kept slides
for sl in prs.slides:
    for sh in list(sl.shapes):
        if sh.is_placeholder and sh.placeholder_format.idx == 10:
            sh._element.getparent().remove(sh._element)

OUT.parent.mkdir(exist_ok=True)
prs.save(str(OUT))
print("saved", OUT, len(prs.slides), "slides")
