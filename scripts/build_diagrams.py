"""Draw the design diagrams and result charts used in the Mini Project report and presentation.

Run from the project root: python scripts/build_diagrams.py
Output: report/figures/*.png
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Ellipse, FancyBboxPatch, Polygon, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
SYN = ROOT / "outputs"
REAL = ROOT / "outputs" / "real_brighter"

NAVY, TEAL, LIGHT, PALE = "#1F3864", "#2CA1BF", "#CDE0E8", "#EAF2F6"
ORANGE, PEACH, GREEN, GREY = "#D9622B", "#FCE8DD", "#2E8B57", "#6B7B83"
plt.rcParams["font.family"] = "DejaVu Sans"


def canvas(w, h, xmax=100, ymax=None):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax if ymax else xmax * h / w)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, fc=LIGHT, ec=NAVY, fs=8, bold=False, color="black", lw=1.2, ls="-", round_=True):
    if round_:
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=1.2", fc=fc, ec=ec, lw=lw, ls=ls)
    else:
        p = Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, ls=ls)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color=color, wrap=True, linespacing=1.25)
    return (x, y, w, h)


def arrow(ax, p1, p2, label=None, color=NAVY, fs=7, lw=1.2, style="-|>", ls="-", off=(0, 1.2), rad=0.0, ha="center"):
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle=style, color=color, lw=lw, ls=ls, shrinkA=0, shrinkB=0,
                                connectionstyle=f"arc3,rad={rad}"))
    if label:
        ax.text((p1[0] + p2[0]) / 2 + off[0], (p1[1] + p2[1]) / 2 + off[1], label, fontsize=fs, ha=ha,
                va="center", color=color, bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", name)


def cx(b):
    return b[0] + b[2] / 2


def cy(b):
    return b[1] + b[3] / 2


def top(b):
    return (cx(b), b[1] + b[3])


def bottom(b):
    return (cx(b), b[1])


def left(b):
    return (b[0], cy(b))


def right(b):
    return (b[0] + b[2], cy(b))


# ---------------------------------------------------------------- 4.1 architecture
def architecture():
    fig, ax = canvas(8, 10.2, 100, 128)
    ax.text(50, 125, "System architecture", ha="center", fontsize=11, fontweight="bold", color=NAVY)
    src = [("BRIGHTER\nemotion data\n(hi, mr, en)", 2), ("Reddit Mental\nHealth Dataset\n(proxy labels)", 27),
           ("Own survey\n(Track C, PHQ-9)", 52), ("Synthetic\ntest data", 77)]
    sb = [box(ax, x, 106, 21, 13, t, fc=PALE, fs=7.5) for t, x in src]
    ing = box(ax, 8, 91, 84, 9, "Data ingestion and validation  (load.py, validate.py)\nCSV / TSV / JSON / JSONL / XLSX  -  column auto-mapping  -  missing, duplicate and label checks",
              fs=7.5)
    for b in sb:
        arrow(ax, bottom(b), (cx(b), 100))
    cl = box(ax, 8, 76, 84, 10, "Privacy-preserving cleaning and unified schema  (clean.py)\nPII scrubbing  -  exact / conflicting duplicate removal  -  age validation (13-100)  -  author hashing",
             fs=7.5)
    arrow(ax, (50, 91), (50, 86))
    lg = box(ax, 8, 61, 40, 10, "Language layer\nrule-based language ID  -  conservative\ncode-mixed normalisation", fs=7.5)
    ag = box(ax, 52, 61, 40, 10, "Age layer\nage bands 13-17, 18-25, 26-35,\n36-45, 46+  (explicit ages only)", fs=7.5)
    arrow(ax, (30, 76), (30, 71))
    arrow(ax, (72, 76), (72, 71))
    mods = [("O1 / O2\nAge-wise text\nand risk analysis", 3), ("O3\nLanguage and\ncode-mixed\nanalysis", 27),
            ("O4\nAge x Language\ncross analysis", 51), ("O5\nModels, group-wise\nfairness and\nexplainability", 75)]
    mb = []
    for t, x in mods:
        mb.append(box(ax, x, 40, 22, 14, t, fc=TEAL, ec=NAVY, fs=7.5, color="white", bold=True))
    for b in mb:
        arrow(ax, (50, 61), (cx(b), 54), off=(0, 0))
    ax.text(50, 57.4, "", fontsize=6)
    js = box(ax, 8, 26, 84, 9, "Aggregated statistics JSON  (analysis_summary.json)\nPRIVACY BOUNDARY: only aggregates cross this line; groups below minimum n are suppressed",
             fc=PEACH, ec=ORANGE, fs=7.5, ls="--", lw=1.6)
    for b in mb:
        arrow(ax, bottom(b), (cx(b), 35), off=(0, 0))
    g6 = box(ax, 8, 10, 40, 11, "O6  Age-wise insights\noffline template or optional online LLM\nnumber-verification guardrail", fs=7.5)
    g7 = box(ax, 52, 10, 40, 11, "O7  Multilingual awareness content\nEnglish / Hindi / Marathi, four age tones\nstatus: PENDING_HUMAN_REVIEW", fs=7.5)
    arrow(ax, (30, 26), (30, 21))
    arrow(ax, (72, 26), (72, 21))
    ui = box(ax, 8, -4, 84, 9, "Streamlit dashboard (app.py)  -  command-line interface (main.py)\ntables, figures and reports (outputs/)",
             fc=NAVY, ec=NAVY, fs=7.5, color="white", bold=True)
    arrow(ax, (30, 10), (30, 5))
    arrow(ax, (72, 10), (72, 5))
    ax.set_ylim(-6, 128)
    save(fig, "fig_architecture.png")


# ---------------------------------------------------------------- DFDs
def circle(ax, x, y, r, text, fs=7.5, fc=LIGHT):
    ax.add_patch(Ellipse((x, y), 2 * r, 2 * r * 0.78, fc=fc, ec=NAVY, lw=1.3))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, fontweight="bold", color=NAVY, linespacing=1.2)


def store(ax, x, y, w, h, text, fs=7):
    ax.add_patch(Rectangle((x, y), w, h, fc="white", ec=NAVY, lw=1.3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.2)
    return (x, y, w, h)


def dfd0():
    fig, ax = canvas(8, 5.2, 100, 65)
    circle(ax, 50, 32, 14, "0\nMental-health text\nanalysis system", fs=8)
    box(ax, 3, 46, 22, 10, "Researcher /\nAnalyst", fc=PALE, round_=False, fs=8)
    box(ax, 3, 6, 22, 10, "Dataset providers\n(BRIGHTER, Reddit,\nsurvey)", fc=PALE, round_=False, fs=7.5)
    box(ax, 75, 46, 22, 10, "LLM provider\n(optional,\nOpenAI-compatible)", fc=PALE, round_=False, fs=7.5)
    box(ax, 75, 6, 22, 10, "Human reviewer\n(native speaker,\nsupervisor)", fc=PALE, round_=False, fs=7.5)
    def lab(x, y, t, ha="center", c=NAVY):
        ax.text(x, y, t, fontsize=7, ha=ha, va="center", color=c)
    arrow(ax, (25, 49), (40.5, 37))
    lab(3, 38, "dataset file,\nrun request", "left")
    arrow(ax, (43, 41.5), (25, 54))
    lab(38, 53, "tables, figures,\ninsights")
    arrow(ax, (25, 13), (39.5, 26))
    lab(3, 21, "raw datasets", "left")
    arrow(ax, (59, 41.5), (75, 53))
    lab(60, 56, "aggregated statistics\nJSON only")
    arrow(ax, (81, 46), (62, 37.5))
    lab(80, 40, "generated summary", "left")
    arrow(ax, (59, 24), (75, 14))
    lab(46, 9, "awareness drafts", "center")
    arrow(ax, (86, 16), (62, 27))
    lab(86, 24, "review decision", "left")
    ax.text(50, 62, "Context diagram (DFD level 0)", ha="center", fontsize=10, fontweight="bold", color=NAVY)
    save(fig, "fig_dfd0.png")


def dfd1():
    fig, ax = canvas(8, 6.4, 100, 80)
    ax.text(50, 77, "DFD level 1", ha="center", fontsize=10, fontweight="bold", color=NAVY)
    box(ax, 1, 57, 12, 10, "Analyst", fc=PALE, round_=False, fs=8)
    xs = [28, 48, 68, 88]
    names = ["1.0\nLoad and\nvalidate", "2.0\nClean and\nnormalise", "3.0\nAnalyse\nO1-O4", "4.0\nTrain and\nevaluate O5"]
    for x, n in zip(xs, names):
        circle(ax, x, 62, 7.3, n, fs=6.8)
    arrow(ax, (13, 62), (20.6, 62))
    ax.text(17, 65, "file", fontsize=6.5, ha="center")
    for x, t in zip(xs[:3], ["profile", "clean.csv", "clean.csv"]):
        arrow(ax, (x + 7.4, 62), (x + 12.6, 62))
        ax.text(x + 10, 65, t, fontsize=6.3, ha="center")
    d1 = store(ax, 19.5, 38, 17, 8, "D1  Raw\ndatasets")
    d2 = store(ax, 39.5, 38, 17, 8, "D2  clean.csv\n(processed)")
    d3 = store(ax, 59.5, 38, 17, 8, "D3  Tables,\nfigures, JSON")
    d4 = store(ax, 79.5, 38, 17, 8, "D4  best_model\n.joblib")
    arrow(ax, (28, 46), (28, 54.7))
    ax.text(29, 50, "read", fontsize=6.5, va="center")
    arrow(ax, (48, 54.7), (48, 46))
    ax.text(49, 50, "write", fontsize=6.5, va="center")
    arrow(ax, (68, 54.7), (68, 46))
    ax.text(62, 50, "write", fontsize=6.5, va="center")
    arrow(ax, (88, 54.7), (88, 46))
    ax.text(89, 50, "save", fontsize=6.5, va="center")
    arrow(ax, (83, 56.5), (75, 46))
    ax.text(79.5, 52, "metrics", fontsize=6.5, ha="right", va="center")
    circle(ax, 48, 16, 9, "5.0\nGenerate insights\nand awareness\ncontent", fs=6.8)
    arrow(ax, (66, 38), (55, 22.5))
    ax.text(64, 29, "aggregates", fontsize=6.5, ha="left", va="center")
    ax.plot([39, 7], [16, 16], color=GREEN, lw=1.2)
    arrow(ax, (7, 16), (7, 56.7), color=GREEN)
    ax.text(23, 18.5, "insights, awareness text", fontsize=6.5, ha="center", color=GREEN)
    box(ax, 79, 11, 19, 9, "LLM provider\n(optional)", fc=PALE, round_=False, fs=7)
    arrow(ax, (57, 16), (79, 16))
    ax.text(68, 18.6, "aggregates only", fontsize=6.5, ha="center", color=ORANGE)
    save(fig, "fig_dfd1.png")


def dfd2():
    fig, ax = canvas(8, 6, 100, 75)
    ax.text(50, 72, "DFD level 2: process 4.0 (model training and evaluation)", ha="center", fontsize=10, fontweight="bold", color=NAVY)
    pos = [(14, 52, "4.1\nBuild TF-IDF\nfeatures"), (38, 52, "4.2\nAuthor-grouped\nstratified CV"),
           (62, 52, "4.3\nOverall and\ngroup metrics"), (86, 52, "4.4\nFairness gaps\nand bootstrap CI")]
    for x, y, t in pos:
        circle(ax, x, y, 8.5, t, fs=6.6)
    for (x1, _, _), (x2, _, _) in zip(pos[:-1], pos[1:]):
        arrow(ax, (x1 + 8.6, 52), (x2 - 8.6, 52))
    ax.text(50, 56.5, "out-of-fold\npredictions x 3 seeds", fontsize=6, ha="center")
    ax.text(74, 55.5, "metrics", fontsize=6.3, ha="center")
    circle(ax, 62, 24, 8.5, "4.5\nExplain (LR\ncoefficients)", fs=6.6)
    store(ax, 2, 28, 22, 6, "D2  clean.csv")
    store(ax, 66, 4, 30, 6, "D3  tables / figures / JSON")
    store(ax, 26, 4, 30, 6, "D4  best_model.joblib")
    arrow(ax, (13, 34), (14, 43.5))
    ax.text(15, 39, "text_norm, label, source_id", fontsize=6.3, ha="left")
    arrow(ax, (62, 43.5), (62, 30.6))
    ax.text(63.5, 37, "group metrics", fontsize=6.3, ha="left")
    arrow(ax, (56, 19), (46, 10))
    ax.text(30, 15, "pickled best pipeline", fontsize=6.3, ha="left")
    arrow(ax, (68, 18.5), (74, 10))
    ax.text(76, 15, "top features", fontsize=6.3, ha="left")
    arrow(ax, (86, 43.5), (90, 10))
    ax.text(89, 28, "fairness gaps, CI", fontsize=6.3, ha="left")
    save(fig, "fig_dfd2.png")


# ---------------------------------------------------------------- UML
def usecase():
    fig, ax = canvas(8, 7.4, 100, 92)
    ax.add_patch(Rectangle((24, 2), 54, 86, fc="white", ec=NAVY, lw=1.5))
    ax.text(51, 85, "Age and Language Mental-Health Text Analysis System", ha="center", fontsize=8.5, fontweight="bold", color=NAVY)
    ucs = ["Upload / select dataset", "Run analysis pipeline", "View age-wise analysis (O1, O2)",
           "View language and code-mixed analysis (O3)", "View age x language analysis (O4)",
           "Compare models and fairness gaps (O5)", "View explanations", "Generate age-wise insights (O6)",
           "Generate awareness content (O7)", "Review awareness content", "Check number guardrail"]
    ys = np.linspace(79, 7, len(ucs))
    ell = []
    for t, y in zip(ucs, ys):
        ax.add_patch(Ellipse((51, y), 44, 5.6, fc=LIGHT, ec=NAVY, lw=1))
        ax.text(51, y, t, ha="center", va="center", fontsize=6.8)
        ell.append(y)

    def actor(x, y, name):
        ax.add_patch(plt.Circle((x, y + 8), 2, fc="white", ec=NAVY, lw=1.4))
        ax.plot([x, x], [y + 6, y], color=NAVY, lw=1.4)
        ax.plot([x - 3.5, x + 3.5], [y + 4.5, y + 4.5], color=NAVY, lw=1.4)
        ax.plot([x, x - 3], [y, y - 5], color=NAVY, lw=1.4)
        ax.plot([x, x + 3], [y, y - 5], color=NAVY, lw=1.4)
        ax.text(x, y - 8, name, ha="center", fontsize=7.5, fontweight="bold", va="top")
        return (x, y + 3)

    an = actor(10, 48, "Researcher /\nAnalyst")
    rv = actor(90, 30, "Reviewer\n(native speaker,\nsupervisor)")
    llm = actor(90, 68, "LLM provider\n(optional)")
    for i in range(0, 9):
        ax.plot([an[0] + 3.5, 29], [an[1], ell[i]], color=GREY, lw=0.8)
    ax.plot([rv[0] - 3.5, 73], [rv[1], ell[9]], color=GREY, lw=0.8)
    ax.plot([rv[0] - 3.5, 73], [rv[1], ell[8]], color=GREY, lw=0.8)
    ax.plot([llm[0] - 3.5, 73], [llm[1], ell[7]], color=GREY, lw=0.8, ls="--")
    ax.plot([llm[0] - 3.5, 73], [llm[1], ell[8]], color=GREY, lw=0.8, ls="--")
    ax.text(51, 0.2, "Dashed lines: optional online mode (aggregated statistics only)", ha="center", fontsize=6.5, color=GREY)
    ax.set_ylim(-3, 92)
    save(fig, "fig_usecase.png")


def decision(ax, cx_, cy_, w, h, text, fs=7):
    ax.add_patch(Polygon([(cx_, cy_ + h / 2), (cx_ + w / 2, cy_), (cx_, cy_ - h / 2), (cx_ - w / 2, cy_)],
                         fc=PEACH, ec=ORANGE, lw=1.2))
    ax.text(cx_, cy_, text, ha="center", va="center", fontsize=fs, linespacing=1.15)


def activity():
    fig, ax = canvas(7, 10.5, 100, 150)
    ax.text(50, 147, "Activity diagram", ha="center", fontsize=10, fontweight="bold", color=NAVY)
    ax.add_patch(plt.Circle((50, 141), 1.8, fc=NAVY))
    steps = [(134, "Select or upload dataset file"), (123, "Load file, map columns, profile data (validate.py)"),
             (112, "Clean: scrub PII, drop duplicates, derive age bands (clean.py)")]
    prev = (50, 139)
    for y, t in steps:
        b = box(ax, 12, y - 3.5, 76, 7, t, fs=7.5)
        arrow(ax, prev, (50, y + 3.5))
        prev = (50, y - 3.5)
    decision(ax, 50, 97, 44, 12, "Reliable ages\navailable?", fs=7)
    arrow(ax, prev, (50, 103))
    box(ax, 4, 73, 32, 8, "Age analysis O1/O2/O4\nrun", fs=7)
    box(ax, 64, 73, 32, 8, "Mark age analysis\n'unavailable'", fs=7, fc=PALE)
    arrow(ax, (28, 97), (20, 81), "yes", off=(-3, 0))
    arrow(ax, (72, 97), (80, 81), "no", off=(3, 0))
    box(ax, 20, 59, 60, 7, "Language analysis O3, code-mixed normalisation", fs=7.5)
    arrow(ax, (20, 73), (35, 66))
    arrow(ax, (80, 73), (65, 66))
    box(ax, 12, 47, 76, 7, "Train LR / SVM / NB with grouped CV; group metrics, fairness gaps", fs=7.5)
    arrow(ax, (50, 59), (50, 54))
    box(ax, 20, 35, 60, 7, "Build aggregated statistics JSON (suppress small groups)", fs=7.5)
    arrow(ax, (50, 47), (50, 42))
    decision(ax, 50, 22, 44, 12, "Online LLM\nenabled?", fs=7)
    arrow(ax, (50, 35), (50, 28))
    box(ax, 2, 6, 34, 8, "Generate summary with\nofflline template".replace("offlline", "offline"), fs=7)
    box(ax, 64, 6, 34, 8, "Generate summary with\nLLM (aggregates only)", fs=7)
    arrow(ax, (28, 22), (19, 14), "no", off=(-3, 0))
    arrow(ax, (72, 22), (81, 14), "yes", off=(3, 0))
    decision(ax, 50, -4, 40, 11, "Numbers and\nsafety verified?", fs=7)
    arrow(ax, (19, 6), (40, -1))
    arrow(ax, (81, 6), (60, -1))
    box(ax, 66, -20, 32, 8, "Fall back to offline\ntemplate", fs=7, fc=PALE)
    arrow(ax, (70, -4), (82, -12), "no", off=(3, 0))
    box(ax, 20, -20, 40, 8, "Publish insights + awareness\n(PENDING_HUMAN_REVIEW)", fs=7)
    arrow(ax, (47, -9.5), (40, -12), "yes", off=(-4, 0))
    arrow(ax, (66, -16), (60, -16))
    ax.add_patch(plt.Circle((40, -26), 2.2, fc="white", ec=NAVY, lw=2))
    ax.add_patch(plt.Circle((40, -26), 1.2, fc=NAVY))
    arrow(ax, (40, -20), (40, -24))
    ax.set_ylim(-30, 150)
    save(fig, "fig_activity.png")


def sequence(name, title, parts, msgs, h=7.2):
    n = len(parts)
    fig, ax = canvas(8, h, 100, 100 * h / 8)
    ymax = 100 * h / 8
    ax.text(50, ymax - 2, title, ha="center", fontsize=10, fontweight="bold", color=NAVY)
    xs = np.linspace(10, 90, n)
    for x, p in zip(xs, parts):
        box(ax, x - 8, ymax - 12, 16, 7, p, fs=6.6, fc=TEAL, color="white", bold=True)
        ax.plot([x, x], [ymax - 12, 4], color=GREY, lw=0.9, ls="--")
    y = ymax - 17
    step = (y - 8) / max(len(msgs), 1)
    for i, (a, b, t) in enumerate(msgs, 1):
        xa, xb = xs[a], xs[b]
        if a == b:
            ax.annotate("", xy=(xa, y - 2.6), xytext=(xa, y), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1,
                                                                             connectionstyle="arc3,rad=-1.6"))
            ax.text(xa + 2.5, y - 1.3, f"{i}. {t}", fontsize=6.4, va="center", ha="left")
        else:
            ls = "--" if t.startswith("<") else "-"
            arrow(ax, (xa, y), (xb, y), ls=ls, color=NAVY, lw=1)
            ax.text((xa + xb) / 2, y + 1.1, f"{i}. {t.lstrip('<')}", fontsize=6.4, ha="center", va="bottom",
                    bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.85))
        y -= step
    save(fig, name)


def sequences():
    sequence("fig_seq_training.png", "Sequence diagram: pipeline execution and model training",
             ["Analyst", "Dashboard /\nCLI", "Loader and\nCleaner", "Analysis\nmodules", "Model\ntrainer", "Output\nstore"],
             [(0, 1, "select dataset, Run"), (1, 2, "load_dataset(path)"), (2, 2, "validate and clean"),
              (2, 5, "write clean.csv, reports"), (1, 3, "run age/language analysis"),
              (3, 5, "write tables, figures"), (1, 4, "run_model_analysis()"), (4, 4, "grouped CV x 3 seeds"),
              (4, 4, "group metrics, bootstrap CI"), (4, 5, "write metrics, model"), (5, 1, "<results ready"),
              (1, 0, "<display pages")], h=8)
    sequence("fig_seq_testing.png", "Sequence diagram: GenAI insight generation with guardrail",
             ["Analyst", "Dashboard /\nCLI", "Insights\nmodule", "LLM client\n(optional)", "Guardrails", "Output\nstore"],
             [(0, 1, "request insights"), (1, 2, "generate_insights(summary)"), (2, 2, "build_facts() - aggregates only"),
              (2, 3, "chat(facts) [online mode]"), (3, 2, "<draft text"), (2, 4, "verify_numbers, check_safety"),
              (4, 2, "<ok / failed"), (2, 2, "fallback to offline template if failed"),
              (2, 5, "save markdown and guardrail JSON"), (2, 1, "<verified text"), (1, 0, "<show insights")], h=7.2)


def classdiagram():
    fig, ax = canvas(8.4, 8.8, 100, 105)
    ax.text(50, 102, "Class (module) diagram", ha="center", fontsize=10, fontweight="bold", color=NAVY)

    def cls(x, y, w, name, ops):
        h = 5 + 3.3 * len(ops)
        ax.add_patch(Rectangle((x, y - h), w, h, fc="white", ec=NAVY, lw=1.2))
        ax.add_patch(Rectangle((x, y - 5), w, 5, fc=TEAL, ec=NAVY, lw=1.2))
        ax.text(x + w / 2, y - 2.5, name, ha="center", va="center", fontsize=7, fontweight="bold", color="white")
        for i, o in enumerate(ops):
            ax.text(x + 1, y - 7.2 - 3.3 * i, o, fontsize=6, va="center")
        return (x, y - h, w, h)

    L = cls(2, 96, 28, "DataLoader / Validator", ["read_any(path)", "load_dataset(path)", "phq9_to_label(score)", "profile_dataset(df, mapping)"])
    C = cls(36, 96, 28, "Cleaner", ["scrub_pii(text)", "normalize_text(text)", "clean_dataframe(df, cfg)"])
    G = cls(70, 96, 28, "LanguageService", ["detect_language(text)", "normalize_language_name(v)", "normalize_roman(text)"])
    A = cls(2, 70, 28, "AgeAnalysis", ["run_age_analysis(df, cfg)", "top_terms_by_group(df, col)"])
    N = cls(36, 70, 28, "LanguageAnalysis", ["run_language_analysis()", "run_combined_analysis()", "run_codemixed_analysis()"])
    S = cls(70, 70, 28, "StatsUtils", ["wilson_ci(k, n)", "chi_square_test(ct)", "kruskal_test(groups)", "benjamini_hochberg(p)"])
    M = cls(2, 48, 38, "ModelTrainer", ["build_pipeline(kind, seed)", "oof_predict(df, kind, seed)", "metrics(y, p)",
                                         "bootstrap_ci(y, p, n)", "group_definitions(df)", "top_features(pipe)", "run_model_analysis(df, cfg)"])
    I = cls(44, 48, 25, "InsightGenerator", ["build_facts(...)", "offline_summary(f)", "generate_insights(...)"])
    K = cls(74, 48, 24, "Guardrails", ["verify_numbers(text, f)", "check_safety(text)"])
    W = cls(44, 28, 25, "AwarenessGenerator", ["generate_awareness(cfg)"])
    Q = cls(74, 28, 24, "LLMClient", ["online_available()", "chat(system, user, model)"])
    D = cls(2, 14, 60, "Dashboard (app.py) / CLI (main.py)", ["pages: Overview, Age, Language, Age x Language, Models, Explainability, GenAI, Limitations", "run_pipeline(path)", "cmd_full(cfg, args)"])
    arrow(ax, right(L), left(C))
    arrow(ax, right(C), left(G))
    ax.text(33, 87, "uses", fontsize=6, ha="center")
    ax.text(67, 87, "uses", fontsize=6, ha="center")
    arrow(ax, (50, C[1]), (50, 70))
    arrow(ax, (40, C[1]), (22, 70))
    arrow(ax, (70, 60), (64, 60))
    ax.text(67, 62.5, "uses", fontsize=6, ha="center")
    arrow(ax, right(I), left(K))
    ax.text(71.5, 43, "verified\nby", fontsize=5.5, ha="center")
    arrow(ax, (86, K[1]), (86, 28))
    ax.text(88, 32.5, "calls (online)", fontsize=6, ha="left")
    arrow(ax, (56, I[1]), (56, 28))
    arrow(ax, (56, 14), (56, W[1]))
    arrow(ax, (21, 14), (21, M[1]))
    ax.text(23, 17, "invokes", fontsize=6, ha="left")
    ax.set_ylim(-6, 104)
    save(fig, "fig_class.png")


def flowchart():
    fig, ax = canvas(7, 10.2, 100, 146)
    ax.text(50, 143, "Flowchart: group-wise model evaluation", ha="center", fontsize=10, fontweight="bold", color=NAVY)
    ax.add_patch(Ellipse((50, 136), 20, 5.5, fc=NAVY))
    ax.text(50, 136, "Start", ha="center", va="center", color="white", fontsize=7.5, fontweight="bold")
    items = [(126, "Input: clean data (text_norm, label, source_id, age_band, language)"),
             (115, "n_splits = min(5, smallest class size, number of authors)"),
             (104, "For each seed in (42, 7, 2024)"),
             (93, "StratifiedGroupKFold: all posts of one author in one fold"),
             (82, "Fit TF-IDF (word 1-2 + char 2-5) and classifier on TRAIN fold only"),
             (71, "Predict TEST fold -> out-of-fold predictions")]
    prev = (50, 133)
    for y, t in items:
        box(ax, 12, y - 4, 76, 8, t, fs=7)
        arrow(ax, prev, (50, y + 4))
        prev = (50, y - 4)
    decision(ax, 50, 57, 46, 12, "All folds and\nseeds done?", fs=7)
    arrow(ax, prev, (50, 63))
    ax.plot([27, 6, 6], [57, 57, 104], color=NAVY, lw=1.2)
    arrow(ax, (6, 104), (12, 104))
    ax.text(15, 59.5, "no", fontsize=7)
    box(ax, 12, 36, 76, 8, "Overall metrics: accuracy, macro-F1, macro P/R, MCC (mean +/- sd)", fs=7)
    arrow(ax, (50, 51), (50, 44), "yes", off=(3, 0))
    decision(ax, 50, 26, 46, 12, "Group n >= 100?", fs=7)
    arrow(ax, (50, 36), (50, 32))
    box(ax, 2, 6, 40, 9, "Group macro-F1 + bootstrap\n95% CI (200 resamples)", fs=7)
    box(ax, 58, 6, 40, 9, "Mark group 'insufficient n'\n(not interpreted)", fs=7, fc=PALE)
    arrow(ax, (30, 26), (22, 15), "yes", off=(-3, 0))
    arrow(ax, (70, 26), (78, 15), "no", off=(3, 0))
    box(ax, 12, -10, 76, 8, "Fairness gap per group type = max - min macro-F1; record worst group", fs=7)
    arrow(ax, (22, 6), (35, -2))
    arrow(ax, (78, 6), (65, -2))
    ax.add_patch(Ellipse((50, -19), 20, 5.5, fc=NAVY))
    ax.text(50, -19, "End", ha="center", va="center", color="white", fontsize=7.5, fontweight="bold")
    arrow(ax, (50, -10), (50, -16.3))
    ax.set_ylim(-24, 146)
    save(fig, "fig_flowchart.png")


def gantt():
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ph = [("P0 Literature and scope", 1, 2), ("P1 Environment and skeleton", 2, 1), ("P2 Dataset acquisition and audit", 2, 2),
          ("P3 Cleaning and unified schema", 3, 2), ("P4 EDA: O1, O2, O3", 4, 2), ("P5 Code-mixed pipeline", 5, 2),
          ("P6 Models and group-wise evaluation", 6, 3), ("P7 Age x language (O4)", 8, 1), ("P8 Explainability", 8, 2),
          ("P9 GenAI insights (O6)", 9, 2), ("P10 GenAI awareness (O7)", 10, 2), ("P11 Dashboard", 11, 3),
          ("P12 Report and presentation", 12, 4)]
    for i, (n, s, d) in enumerate(ph):
        ax.barh(i, d, left=s - 1, color=TEAL if i % 2 == 0 else NAVY, height=0.6)
    ax.set_yticks(range(len(ph)))
    ax.set_yticklabels([p[0] for p in ph], fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xticks(np.arange(0, 16) + 0.5)
    ax.set_xticklabels([f"W{i}" for i in range(1, 17)], fontsize=7)
    ax.set_xlim(0, 16)
    ax.grid(axis="x", color="#dddddd", lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title("Project timeline (weeks of the semester)", fontsize=10, color=NAVY, fontweight="bold")
    save(fig, "fig_gantt.png")


# ---------------------------------------------------------------- result charts
def result_charts():
    syn = json.loads((SYN / "reports" / "analysis_summary.json").read_text(encoding="utf-8"))
    real = json.loads((REAL / "reports" / "analysis_summary.json").read_text(encoding="utf-8"))
    # synthetic: elevated share by age band
    share = syn["age_analysis_O1_O2"]["elevated_share_by_age_band_pct"]
    sizes = syn["age_analysis_O1_O2"]["group_sizes"]
    order = ["13-17", "18-25", "26-35", "36-45", "46+"]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    bars = ax.bar(order, [share[k] for k in order], color=TEAL, edgecolor=NAVY)
    for b, k in zip(bars, order):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.8, f"{share[k]:.1f}%\n(n={sizes[k]})", ha="center", fontsize=7.5)
    ax.set_ylabel("Posts with elevated label (%)")
    ax.set_xlabel("Age band")
    ax.set_ylim(0, 54)
    ax.set_title("Synthetic test data: elevated-label share by age band", fontsize=9.5, color=NAVY)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "chart_syn_age_elevated.png")
    # overall model comparison: synthetic vs real
    s = pd.read_csv(SYN / "tables" / "model_comparison_overall.csv").set_index("model")
    r = pd.read_csv(REAL / "tables" / "model_comparison_overall.csv").set_index("model")
    models = ["logreg", "linear_svm", "complement_nb"]
    lab = ["Logistic\nRegression", "Linear SVM", "Complement\nNaive Bayes"]
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(6.4, 3.5))
    b1 = ax.bar(x - 0.19, [s.loc[m, "macro_f1_mean"] for m in models], 0.38, color=NAVY, label="Synthetic test data (n=1,200)")
    b2 = ax.bar(x + 0.19, [r.loc[m, "macro_f1_mean"] for m in models], 0.38, color=TEAL, label="BRIGHTER en/hi/mr, proxy labels (n=6,662)")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.01, f"{b.get_height():.3f}", ha="center", fontsize=7.5)
    ax.set_xticks(x)
    ax.set_xticklabels(lab, fontsize=8)
    ax.set_ylabel("Macro-F1 (mean of 5-fold x 3 seeds)")
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=7.5, loc="lower right")
    ax.set_title("Overall model comparison", fontsize=9.5, color=NAVY)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    save(fig, "chart_model_comparison.png")
    # real: macro-F1 by language per model with CI
    g = pd.read_csv(REAL / "tables" / "model_group_metrics.csv")
    g = g[g.group_type == "language"]
    langs = ["en", "hi", "mr"]
    names = {"en": "English", "hi": "Hindi", "mr": "Marathi"}
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    cols = {"logreg": NAVY, "linear_svm": TEAL, "complement_nb": ORANGE}
    for i, m in enumerate(models):
        d = g[g.model == m].set_index("group").loc[langs]
        yerr = [d.macro_f1_mean - d.macro_f1_ci_low, d.macro_f1_ci_high - d.macro_f1_mean]
        ax.bar(np.arange(3) + (i - 1) * 0.26, d.macro_f1_mean, 0.26, yerr=yerr, capsize=2.5, color=cols[m],
               label={"logreg": "Logistic Regression", "linear_svm": "Linear SVM", "complement_nb": "Complement NB"}[m])
        for xx, v in zip(np.arange(3) + (i - 1) * 0.26, d.macro_f1_mean):
            ax.text(xx, 0.02, f"{v:.2f}", ha="center", fontsize=6.8, color="white", fontweight="bold")
    ax.set_xticks(range(3))
    ax.set_xticklabels([names[l] for l in langs])
    ax.set_ylabel("Macro-F1 (bootstrap 95% CI)")
    ax.set_ylim(0, 1.0)
    ax.legend(fontsize=7.5, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.0))
    ax.set_title("BRIGHTER proxy-label task: macro-F1 by language", fontsize=9.5, color=NAVY, pad=14)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    save(fig, "chart_real_language_f1.png")
    # fairness gaps: both datasets, best-model-neutral view (all models)
    sg = pd.read_csv(SYN / "tables" / "model_fairness_gaps.csv")
    rg = pd.read_csv(REAL / "tables" / "model_fairness_gaps.csv")
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.4), sharey=True)
    for ax, d, ttl in ((axs[0], sg, "Synthetic test data"), (axs[1], rg, "BRIGHTER (real, proxy labels)")):
        types = list(d.group_type.unique())
        w = 0.26
        for i, m in enumerate(models):
            vals = [float(d[(d.model == m) & (d.group_type == t)].macro_f1_gap.iloc[0]) for t in types]
            ax.bar(np.arange(len(types)) + (i - 1) * w, vals, w, color=cols[m],
                   label={"logreg": "LogReg", "linear_svm": "Linear SVM", "complement_nb": "Compl. NB"}[m])
            for xx, v in zip(np.arange(len(types)) + (i - 1) * w, vals):
                ax.text(xx, v + 0.008, f"{v:.2f}", ha="center", fontsize=6.5)
        ax.set_xticks(range(len(types)))
        ax.set_xticklabels([t.replace(" x ", "\nx ") for t in types], fontsize=7.5)
        ax.set_title(ttl, fontsize=9, color=NAVY)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axs[0].set_ylabel("Macro-F1 gap (max - min)")
    axs[0].legend(fontsize=7)
    fig.tight_layout()
    save(fig, "chart_fairness_gaps.png")
    # label share by language (real)
    lt = pd.read_csv(REAL / "tables" / "language_label_table.csv")
    lt = lt[lt.label == "negative_affect"].set_index("language").loc[langs]
    fig, ax = plt.subplots(figsize=(5.6, 3.3))
    bars = ax.bar([names[l] for l in langs], lt.pct, yerr=[lt.pct - lt.ci_low_pct, lt.ci_high_pct - lt.pct], capsize=4,
                  color=[NAVY, TEAL, TEAL])
    for b, n in zip(bars, lt.n):
        ax.text(b.get_x() + b.get_width() / 2, 6, f"{b.get_height():.1f}%\nn={n}", ha="center", color="white", fontsize=8, fontweight="bold")
    ax.set_ylabel("negative_affect share (%), Wilson 95% CI")
    ax.set_ylim(0, 80)
    ax.set_title("BRIGHTER proxy-label share by language", fontsize=9.5, color=NAVY)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    save(fig, "chart_real_language_share.png")


if __name__ == "__main__":
    architecture()
    dfd0()
    dfd1()
    dfd2()
    usecase()
    activity()
    sequences()
    classdiagram()
    flowchart()
    gantt()
    result_charts()
