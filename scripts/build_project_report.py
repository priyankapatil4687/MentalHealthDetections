"""Generate an editable PowerPoint report from project outputs.

Run from the project root: python scripts/build_project_report.py
"""
import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "outputs" / "reports"
OUT = REPORTS / "age_language_mental_health_project_report.pptx"
SUMMARY = REPORTS / "analysis_summary.json"
W, H = 13.333, 7.5
INK, MUTED, PAPER = "183238", "607579", "F5F7F2"
WHITE, TEAL, MINT = "FFFFFF", "087E78", "DCEFE9"
CORAL, PEACH, GOLD = "E76F51", "FCE8DD", "E6B84A"
PALE_GOLD, PALE_BLUE, BLUE, LINE = "F8EFCF", "E5EDF2", "496B85", "C8D6D1"
FONT = "Aptos"


def color(hex_value):
    return RGBColor.from_string(hex_value)


def text(slide, x, y, w, h, value, size=15, fg=INK, bold=False, align=PP_ALIGN.LEFT):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = Inches(.06)
    frame.margin_top = frame.margin_bottom = Inches(.04)
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = frame.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = str(value)
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = FONT, Pt(size), bold, color(fg)
    return shape


def box(slide, x, y, w, h, label, fill=WHITE, stroke=LINE, fg=INK, size=14, oval=False):
    kind = MSO_SHAPE.OVAL if oval else MSO_SHAPE.ROUNDED_RECTANGLE
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = color(fill)
    s.line.color.rgb = color(stroke)
    s.line.width = Pt(1.2)
    s.text_frame.clear()
    s.text_frame.word_wrap = True
    s.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    s.text_frame.margin_left = s.text_frame.margin_right = Inches(.10)
    p = s.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = label
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = FONT, Pt(size), True, color(fg)
    return s


def store(slide, x, y, w, h, label):
    return box(slide, x, y, w, h, label, PALE_GOLD, GOLD, INK, 12)


def arrow(slide, x1, y1, x2, y2, label=None, lx=None, ly=None, lw=1.5, shade=TEAL):
    line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    line.line.color.rgb, line.line.width = color(shade), Pt(1.7)
    dx, dy = x2 - x1, y2 - y1
    if abs(dx) >= abs(dy):
        rot = 90 if dx > 0 else 270
        tx, ty = x2 - (.03 if dx > 0 else .17), y2 - .08
    else:
        rot = 180 if dy > 0 else 0
        tx, ty = x2 - .08, y2 - (.16 if dy > 0 else .02)
    tip = slide.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(tx), Inches(ty), Inches(.17), Inches(.16))
    tip.rotation = rot
    tip.fill.solid()
    tip.fill.fore_color.rgb = color(shade)
    tip.line.fill.background()
    if label:
        text(slide, lx if lx is not None else (x1+x2)/2-lw/2,
             ly if ly is not None else (y1+y2)/2-.18, lw, .32, label, 9, MUTED, align=PP_ALIGN.CENTER)


def slide(prs, title, section, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = color(PAPER)
    band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(.12))
    band.fill.solid()
    band.fill.fore_color.rgb = color(TEAL)
    band.line.fill.background()
    text(s, .62, .28, 12, .25, section.upper(), 10, TEAL, True)
    text(s, .62, .58, 12, .65, title, 26, INK, True)
    text(s, .62, 7.10, 11, .22, "AGE & LANGUAGE-BASED MENTAL-HEALTH TEXT ANALYSIS  |  RESEARCH PROJECT", 8, MUTED)
    text(s, 12.0, 7.07, .7, .25, f"{page:02d}", 9, TEAL, True, PP_ALIGN.RIGHT)
    return s


def build():
    data = json.loads(SUMMARY.read_text(encoding="utf-8")) if SUMMARY.exists() else {}
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(W), Inches(H)

    # Cover
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = color(INK)
    for x, y, d, c in [(10, -.5, 4, TEAL), (10.8, 4.5, 3, CORAL), (8.8, 5.7, 1, GOLD)]:
        shape = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
        shape.fill.solid(); shape.fill.fore_color.rgb = color(c); shape.fill.transparency = 12
        shape.line.fill.background()
    text(s, .85, .8, 5, .35, "MINI PROJECT REPORT  |  2026", 12, "A6D8CF", True)
    text(s, .85, 1.55, 8.5, 2.2, "Age and Language-Based\nMental-Health Text Analysis", 34, WHITE, True)
    text(s, .88, 4.0, 7.9, .8, "Group-wise evaluation with privacy-aware analytics and guarded generative-AI reporting", 18, "D4E1DD")
    box(s, .88, 5.5, 4.2, .65, "Research and educational tool · not diagnostic", "26474A", "26474A", WHITE, 12)
    text(s, .88, 6.72, 7, .28, "Project team: ____________________     Guide: ____________________", 11, "D4E1DD")

    # Overview
    s = slide(prs, "Project overview", "01 / Context", 2)
    text(s, .8, 1.65, 5.8, 1.05, "A reproducible Python framework for studying how text-analysis results vary across age bands and languages.", 20, INK, True)
    text(s, .8, 2.85, 5.7, 1.05, "It combines data validation, privacy cleaning, descriptive analysis, baseline NLP models, subgroup evaluation and an interactive dashboard.", 15, MUTED)
    for x,y,label,fill in [(7.1,1.8,"AGE\nPatterns + labels",MINT),(9.8,1.8,"LANGUAGE\nMultilingual + code-mixed",PALE_BLUE),(7.1,3.3,"MODELS\nGroup evaluation",PALE_GOLD),(9.8,3.3,"DASHBOARD\nTables + reports",PEACH)]:
        box(s,x,y,2.25,1.05,label,fill,fill,INK,14)
    text(s,.8,4.85,11.6,.6,"Objectives O1–O5: analytics and evaluation  ·  O6: guarded insights  ·  O7: reviewable awareness content",14,TEAL,True)
    text(s,.8,5.7,11.6,.7,"The system does not diagnose people, infer age from writing, or send raw posts to an external language model.",16,CORAL,True)

    # Problem / objectives
    s = slide(prs, "Problem statement and objectives", "02 / Research framing", 3)
    box(s,.8,1.75,4.25,3.85,"PROBLEM\n\nOne aggregate model score can hide differences across age and language groups. Relevant data may be sparse, proxy-labelled, or missing age-language combinations.",WHITE,LINE,INK,16)
    text(s,5.55,1.75,6,.35,"PROJECT OBJECTIVES",12,TEAL,True)
    objectives=[("O1–O2","Age-wise text patterns and label-category analysis"),("O3","Multilingual and code-mixed text analysis"),("O4","Age × language analysis with minimum-n guards"),("O5","Compare baseline models and subgroup metrics"),("O6–O7","Number-checked insights and human-reviewable awareness content")]
    for i,(tag,label) in enumerate(objectives):
        y=2.2+i*.68
        box(s,5.55,y,1.25,.46,tag,MINT,MINT,TEAL,11)
        text(s,6.98,y,5.5,.46,label,14)
    text(s,.85,6.0,11.4,.45,"Research patterns and model behaviour only; no individual clinical risk scoring.",15,CORAL,True)

    # Inputs and scope
    s = slide(prs,"Data sources and scope","03 / Inputs",4)
    src=[("CSV / TSV / JSON / XLSX","Uploaded or local data",MINT),("Open corpora","Reddit / BRIGHTER preparations",PALE_BLUE),("Survey track","Consent + ethics approval required",PALE_GOLD),("Synthetic samples","Software tests only; not evidence",PEACH)]
    for i,(head,desc,fill) in enumerate(src):
        box(s,.85+(i%2)*3.25,1.8+(i//2)*1.45,2.8,1.08,f"{head}\n{desc}",fill,fill,INK,13)
    box(s,7.45,1.8,4.8,3.05,"SCOPE GUARDRAILS\n\n• Datasets are analysed separately\n• Labels may be proxies, not diagnoses\n• Age is only used when supplied / validated\n• Small groups are flagged or suppressed\n• Raw text and identifiers stay local",WHITE,LINE,INK,14)
    text(s,.85,5.35,11.2,.7,"Data handling: validate schema, clean identifiers, map to a unified format, and save aggregate outputs for reporting.",15,MUTED)

    # Architecture
    s=slide(prs,"System architecture","04 / Components",5)
    nodes=[(.75,"INPUT\nCSV / TSV / JSON / XLSX",MINT),(3.1,"DATA LAYER\nLoad · validate · clean",PALE_BLUE),(5.45,"ANALYSIS\nAge · language · combined",PALE_GOLD),(7.8,"ML LAYER\nTrain · evaluate · explain",PEACH),(10.15,"PRESENTATION\nStreamlit dashboard",MINT)]
    for x,label,fill in nodes: box(s,x,1.85,2.05,1.0,label,fill,fill,INK,12)
    for x in [2.83,5.18,7.53,9.88]: arrow(s,x,2.35,x+.22,2.35)
    store(s,2.1,3.75,2.4,.85,"Clean dataset\nprocessed/")
    store(s,5.45,3.75,2.4,.85,"Tables · figures\nreports · model")
    box(s,9.05,3.6,3.1,1.15,"OPTIONAL GENAI\nAggregates only\nO6 insights · O7 drafts",PALE_BLUE,BLUE,INK,13)
    arrow(s,4.5,4.15,5.45,4.15,"clean data",4.57,3.83,1.0)
    arrow(s,7.85,4.15,9.05,4.15,"aggregates",8.0,3.83,1.0)
    text(s,.85,5.2,11.5,.68,"`main.py` orchestrates the pipeline; `app.py` provides upload, run controls, analysis pages and limitations.",14,MUTED)
    text(s,.85,6.0,11.5,.5,"Privacy boundary: external LLM requests, if enabled, receive aggregate statistics, not raw posts.",15,CORAL,True)

    # DFD 0
    s=slide(prs,"DFD Level 0 · Context diagram","05 / Data-flow diagrams",6)
    text(s,.85,1.55,11.5,.35,"One process represents the complete Age & Language Mental-Health Text Analysis System.",13,MUTED)
    box(s,.9,2.65,2.0,.95,"DATA SOURCES",PALE_BLUE,BLUE,INK,13,True)
    box(s,.9,4.55,2.0,.95,"ANALYST / USER",PALE_BLUE,BLUE,INK,13,True)
    box(s,5.0,3.15,3.0,1.35,"0\nAGE & LANGUAGE\nTEXT ANALYSIS SYSTEM",MINT,TEAL,INK,16)
    box(s,10.15,3.25,2.0,.95,"OPTIONAL LLM",PEACH,CORAL,INK,13,True)
    arrow(s,2.9,3.0,5.0,3.55,"text + labels",3.35,2.75,1.4)
    arrow(s,2.9,4.85,5.0,4.1,"upload / run",3.3,4.48,1.3)
    arrow(s,5.0,4.25,2.9,5.0,"charts / reports",3.3,5.1,1.4,CORAL)
    arrow(s,8.0,3.55,10.15,3.55,"aggregates only",8.2,3.12,1.6,CORAL)
    arrow(s,10.15,4.0,8.0,4.0,"guarded text",8.45,4.13,1.3)
    text(s,8.75,5.45,3.8,.45,"Raw text never crosses this boundary.",13,CORAL,True,PP_ALIGN.CENTER)

    # DFD 1
    s=slide(prs,"DFD Level 1 · Main processes","05 / Data-flow diagrams",7)
    text(s,.85,1.55,11.5,.35,"Major processes and persistent data stores.",13,MUTED)
    steps=[(.7,"1.0\nLoad data",MINT),(2.78,"2.0\nValidate + clean",PALE_BLUE),(4.86,"3.0\nAge / language\nanalysis",PALE_GOLD),(6.94,"4.0\nTrain + evaluate\nmodels",PEACH),(9.02,"5.0\nGenAI\n(aggregates)",PALE_BLUE),(11.1,"6.0\nDashboard +\nreports",MINT)]
    for x,label,fill in steps: box(s,x,2.25,1.55,1.05,label,fill,fill,INK,11)
    for x in [2.25,4.33,6.41,8.49,10.57]: arrow(s,x,2.78,x+.52,2.78)
    box(s,.7,4.45,1.55,.72,"USER / FILE",PALE_BLUE,BLUE,INK,11,True)
    store(s,3.0,4.35,2.15,.88,"D1 · Clean\ndataset")
    store(s,6.0,4.35,2.15,.88,"D2 · Tables +\nfigures")
    store(s,9.1,4.35,2.15,.88,"D3 · Reports +\nmodel artifact")
    arrow(s,1.48,3.3,1.48,4.45,"dataset",1.55,3.65,.85)
    arrow(s,3.5,3.3,4.0,4.35,"clean output",3.35,3.72,1.2)
    arrow(s,5.65,3.3,6.75,4.35,"aggregates",5.72,3.72,1.0)
    arrow(s,7.7,3.3,10.1,4.35,"metrics / model",8.0,3.72,1.45)
    text(s,.85,5.72,11.5,.65,"Optional GenAI receives filtered aggregates; generated awareness content remains pending human review.",14,MUTED)

    # DFD 2
    s=slide(prs,"DFD Level 2 · Analysis and evaluation","05 / Data-flow diagrams",8)
    text(s,.85,1.55,11.5,.35,"Decomposition of Level 1 process 3.0 and its model-evaluation handoff.",13,MUTED)
    store(s,.8,3.1,1.75,.95,"D1\nClean data")
    parts=[(2.85,2.0,"3.1\nAge patterns +\nlabels",MINT),(5.0,2.0,"3.2\nLanguage +\ncode-mix",PALE_BLUE),(7.15,2.0,"3.3\nAge × language\nminimum-n",PALE_GOLD),(2.85,4.35,"3.4\nTrain baseline\nmodels",PEACH),(5.0,4.35,"3.5\nGroup metrics +\nfairness gaps",MINT),(7.15,4.35,"3.6\nExplain +\naggregate results",PALE_BLUE)]
    for x,y,label,fill in parts: box(s,x,y,1.85,.98,label,fill,fill,INK,11)
    store(s,10.1,3.25,2.05,.95,"D2\nTables + reports")
    for x,y in [(2.85,2.5),(5.0,2.5),(7.15,2.5),(2.85,4.8)]: arrow(s,2.55,3.6,x,y)
    arrow(s,4.7,2.5,5.0,4.8,"features / groups",4.0,3.45,1.4)
    arrow(s,4.7,4.8,5.0,4.8)
    arrow(s,6.85,4.8,7.15,4.8)
    arrow(s,9.0,2.5,10.1,3.5,"guarded aggregates",8.85,2.9,1.5)
    arrow(s,9.0,4.8,10.1,3.95,"tables / metrics",9.0,4.35,1.2)
    text(s,.9,5.95,11.5,.5,"Groups below configured sample thresholds are marked insufficient, not treated as reliable findings.",14,CORAL,True)

    # Method
    s=slide(prs,"Methodology and processing pipeline","06 / Approach",9)
    phases=[("01","Validate","Schema, missingness, labels, age and language"),("02","Clean","PII placeholders, deduplication, unified fields"),("03","Analyze","Age, language, code-mix and age × language"),("04","Model","TF-IDF baselines; grouped cross-validation"),("05","Report","Metrics, uncertainty, limitations and dashboard")]
    for i,(n,head,desc) in enumerate(phases):
        y=1.7+i*.88
        box(s,.9,y,.68,.52,n,TEAL if i<3 else CORAL,TEAL if i<3 else CORAL,WHITE,13)
        text(s,1.85,y,1.65,.48,head,16,INK,True)
        text(s,3.65,y,8.2,.48,desc,15,MUTED)
        if i<4: arrow(s,1.24,y+.53,1.24,y+.82,shade=LINE)
    box(s,.9,6.2,11.3,.48,"Primary metric: macro-F1  ·  Tests: chi-square / Cramér's V and Kruskal–Wallis where supported",PALE_BLUE,PALE_BLUE,INK,12)

    # Models
    s=slide(prs,"Model comparison and subgroup reporting","07 / Evaluation",10)
    for i,(name,fill) in enumerate([("Logistic Regression",MINT),("Linear SVM",PALE_BLUE),("Complement NB",PALE_GOLD)]):
        box(s,.9+i*2.55,1.9,2.2,1.0,f"{name}\nTF-IDF baseline",fill,fill,INK,14)
    box(s,9.0,1.8,3.1,1.25,"VALIDATION\n5-fold author-grouped stratified CV × 3 seeds",PEACH,PEACH,INK,13)
    text(s,.95,3.45,5,.35,"REPORTED METRICS",12,TEAL,True)
    text(s,.95,3.9,5.1,1.25,"Macro-F1 · accuracy · precision / recall\nMCC · confusion matrix · per-group metrics\nFairness gaps when groups have sufficient n",15)
    text(s,6.65,3.45,5,.35,"INTERPRETATION RULES",12,CORAL,True)
    text(s,6.65,3.9,5.35,1.5,"Vectorizers fit inside training folds. Group results include sample counts; underpowered groups are marked insufficient. Explanations describe model behaviour, not causes or diagnoses.",15)

    # Results
    s=slide(prs,"Saved run snapshot · cautious interpretation","08 / Current outputs",11)
    rows=data.get("models_O5",{}).get("overall",[])
    label={"linear_svm":"Linear SVM","complement_nb":"Complement NB","logreg":"Logistic Regression"}
    text(s,.9,1.6,5.4,.35,f"Dataset: {', '.join(data.get('sources',['not available']))}",13,MUTED)
    text(s,.9,2.0,5,.4,f"Rows after cleaning: {data.get('rows','n/a')}",17,INK,True)
    text(s,.9,2.6,5,.32,"MODEL SNAPSHOT · MACRO-F1",12,TEAL,True)
    box(s,.9,3.05,5.35,2.0,"",WHITE,LINE,INK,12)
    for i,row in enumerate(rows):
        y=3.2+i*.53
        text(s,1.12,y,2.5,.3,label.get(row.get('model'),row.get('model')),13,INK,True)
        text(s,4.0,y,1.9,.3,f"{row.get('macro_f1_mean',0):.3f} ± {row.get('macro_f1_std',0):.3f}",13,TEAL,True,PP_ALIGN.RIGHT)
    box(s,6.8,1.75,5.2,3.75,"DATA ADEQUACY\n\nAge: all bands are below the configured group-size minimum.\n\nLanguage: 16 records per category in this run, below the reporting threshold.\n\nAge × language: 0 of 16 cells meet the minimum sample-size rule.\n\nNo dependable subgroup conclusion can be drawn.",PALE_GOLD,GOLD,INK,14)
    p=data.get("age_analysis_O1_O2",{}).get("label_vs_age_chi_square",{}).get("p_value")
    text(s,.9,5.6,11.2,.45,f"Age-label association p = {p:.3f}. Exploratory and underpowered." if isinstance(p,(int,float)) else "Age-label association: unavailable in saved run.",14,MUTED)
    text(s,.9,6.2,11.2,.42,"Pipeline outputs only; not clinical findings or evidence of population-level risk.",14,CORAL,True)

    # Safety
    s=slide(prs,"Privacy, responsible use and GenAI controls","09 / Trust boundaries",12)
    bullets=[(.95,1.8,"Local preprocessing","Remove / replace identifiers; preserve source text locally.",TEAL),(.95,2.85,"Aggregate-only GenAI","Only summary statistics may reach an optional external model.",CORAL),(.95,3.9,"Number guardrail","Generated insight numbers are checked against source aggregates.",TEAL),(6.8,1.8,"Human review","Awareness copy is pending reviewer approval.",CORAL),(6.8,2.85,"No diagnosis","No screening, treatment or individual decisions.",TEAL),(6.8,3.9,"Visible limits","Proxy labels, language variation and small samples affect validity.",GOLD)]
    for x,y,head,desc,c in bullets:
        box(s,x,y,.13,.13,c,c,c,10,True)
        text(s,x+.23,y-.05,5,.32,head,15,INK,True)
        text(s,x+.23,y+.32,5,.42,desc,12,MUTED)
    box(s,.95,5.35,11.2,.85,"This system studies text patterns. It is not a diagnostic tool and must not be used to make decisions about individuals.",INK,INK,WHITE,16)

    # Limitations / future
    s=slide(prs,"Limitations and future work","10 / Conclusion",13)
    text(s,.95,1.75,5.2,.35,"CURRENT LIMITATIONS",12,CORAL,True)
    text(s,.95,2.2,5.3,2.55,"• Proxy labels may not represent clinical status\n• Age is sparse and only used when available\n• Rule-based language hints are not ground truth\n• Small groups limit fair comparison\n• Survey data requires consent and ethics approval\n• Awareness content needs human review",14)
    text(s,6.65,1.75,5,.35,"NEXT STEPS",12,TEAL,True)
    text(s,6.65,2.2,5.3,2.55,"• Validate age extraction and language labels\n• Collect approved age × language survey data\n• Expand evaluation with adequately sized groups\n• Add calibration and explanation stability checks\n• Complete literature review and final results\n• Review multilingual content with qualified people",14)
    box(s,.95,5.3,11.1,.85,"Conclusion: a reproducible, privacy-aware analysis workflow with explicit uncertainty and responsible-use boundaries.",MINT,MINT,INK,16)

    # Reproducibility
    s=slide(prs,"Reproducibility and references","11 / Appendix",14)
    text(s,.9,1.7,5.5,.35,"RUN THE PROJECT",12,TEAL,True)
    box(s,.9,2.15,5.7,2.15,"python main.py check\npython main.py full --input data/sample/sample_clean.csv\nstreamlit run app.py\npython -m pytest -q",INK,INK,WHITE,14)
    text(s,7.0,1.7,5,.35,"PROJECT DOCUMENTS",12,TEAL,True)
    refs=["docs/01_Requirements_Objectives_Outcomes.md","docs/03_Implementation_Plan_and_Action_Plan.md","docs/04_TrackC_Survey_and_Consent.md","docs/05_IEEE_Report_Draft.md","Dashboard and CLI: app.py · main.py"]
    for i,r in enumerate(refs): text(s,7.0,2.15+i*.62,5.2,.48,r,12)
    text(s,.92,5.15,11.2,.72,"Before submission: add team/institution details, verify dataset provenance and citations, and replace this saved-run snapshot with approved final results.",14,CORAL,True)
    text(s,.92,6.15,11.2,.38,"End of project report",17,TEAL,True,PP_ALIGN.CENTER)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"Created {OUT.relative_to(ROOT)} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    build()