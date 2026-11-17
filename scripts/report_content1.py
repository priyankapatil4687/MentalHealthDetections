"""Report content: Chapters 1-3."""
from pathlib import Path

TITLE = "Age and Language-Based Mental Health Text Analysis Using Generative AI"


def abstract_paragraphs():
    return [
        "Mental-health conditions are common, under-reported and strongly shaped by age and by the language in which people "
        "express distress. Most text-analysis studies treat all users as one group, work almost only in English and report a single "
        "overall accuracy, which can hide large differences between teenagers and older adults, or between English, Hindi and Marathi "
        "writers. This mini project builds a reproducible, privacy-preserving framework that studies these differences explicitly.",
        "The framework ingests public or consented text datasets, validates and cleans them (PII scrubbing, duplicate and "
        "conflicting-label removal, age validation, author hashing), identifies language and Romanized code-mixed text, and then "
        "runs seven analyses: age-wise text patterns (O1), age-based risk analysis (O2), multilingual and code-mixed analysis (O3), "
        "age x language analysis (O4), group-wise model comparison with fairness gaps and explainability (O5), and two Generative AI "
        "components that turn only aggregated statistics into age-wise insights (O6) and multilingual awareness drafts (O7). "
        "Models are TF-IDF word and character n-gram classifiers (Logistic Regression, Linear SVM, Complement Naive Bayes) evaluated "
        "with author-grouped stratified cross-validation, three seeds and bootstrap confidence intervals. A number-verification "
        "guardrail rejects any generated sentence whose figures do not match the computed statistics.",
        "The implementation (about 2,400 lines of Python, 39 automated tests, a Streamlit dashboard and a command-line interface) was "
        "validated on a synthetic dataset and run on 6,662 cleaned English, Hindi and Marathi texts from the open BRIGHTER emotion "
        "corpus. On this real data, negative-affect proxy labels differ strongly by language (64.1% English, 30.9% Hindi, 33.2% Marathi; "
        "Cramer's V = 0.31), and the best model (Linear SVM) reaches macro-F1 0.816 overall but only 0.626 on English against 0.841 "
        "(Hindi) and 0.887 (Marathi), a language gap of 0.261 that an overall score would hide. Labels are emotion proxies, not clinical "
        "diagnoses, and the tool is intended for research and awareness only.",
    ]


KEYWORDS = ("mental health, text analysis, age-wise analysis, multilingual, code-mixed, Hindi, Marathi, "
            "fairness, explainability, generative AI, privacy")

ABBREVIATIONS = [
    ("AIML", "Artificial Intelligence and Machine Learning"), ("API", "Application Programming Interface"),
    ("BH", "Benjamini-Hochberg (false-discovery-rate correction)"), ("CI", "Confidence Interval"),
    ("CLI", "Command-Line Interface"), ("CSV", "Comma-Separated Values"), ("CV", "Cross-Validation"),
    ("DFD", "Data Flow Diagram"), ("EDA", "Exploratory Data Analysis"), ("F1", "Harmonic mean of precision and recall"),
    ("GenAI", "Generative Artificial Intelligence"), ("JSON", "JavaScript Object Notation"),
    ("LLM", "Large Language Model"), ("LR", "Logistic Regression"), ("MCC", "Matthews Correlation Coefficient"),
    ("MH", "Mental Health"), ("NB", "Naive Bayes"), ("NLP", "Natural Language Processing"),
    ("OOF", "Out-Of-Fold"), ("PHQ-9", "Patient Health Questionnaire-9"), ("PII", "Personally Identifiable Information"),
    ("SRS", "Software Requirements Specification"), ("SVM", "Support Vector Machine"),
    ("TF-IDF", "Term Frequency - Inverse Document Frequency"), ("UI", "User Interface"),
    ("UML", "Unified Modeling Language"), ("WHO", "World Health Organization"),
]


def chapter1(r):
    r.chapter(1, "Introduction")
    r.h2("1.1 Introduction")
    r.p("Mental-health disorders are among the leading causes of disability worldwide. The World Health Organization estimates that "
        "roughly 280 million people live with depression [1], and the National Mental Health Survey of India (2015-16) reported "
        "that about one in ten adults had a mental-health condition at the time of the survey, with a very large treatment gap [2]. "
        "A large share of this distress is first expressed informally, in posts, comments, chats and short messages, long before any "
        "clinical contact. Natural Language Processing (NLP) can read such text at scale and is therefore an attractive tool for "
        "population-level research and for designing awareness material.")
    r.p("Two facts make the problem harder than a standard text-classification task. First, **age matters**: teenagers, "
        "young adults and older adults use different vocabulary, different topics (school and exams versus work, family and health) "
        "and different ways of disclosing distress. Second, **language matters**: in India a person may write in English, Hindi, Marathi, "
        "or a Romanized mixture such as Hinglish, often switching language inside a single sentence. A model trained on one group "
        "can behave very differently on another, and a single overall accuracy figure hides this.")
    r.p("This mini project therefore builds an end-to-end, reproducible framework for **age-wise and language-wise mental-health "
        "text analysis**, with fairness reporting, explainability, privacy safeguards and a carefully guarded Generative AI "
        "layer that explains the results in plain language.")

    r.h2("1.2 Problem Identified")
    r.bl([
        "Existing mental-health NLP work is dominated by English text and by one-size-fits-all models; Hindi, Marathi and Romanized "
        "code-mixed text are poorly covered.",
        "Datasets seldom contain a reliable age field, so age-wise analysis is rarely attempted and age effects are confounded "
        "with platform effects.",
        "Results are usually reported as one overall score, so performance gaps between age bands or languages go unnoticed.",
        "Raw user text is sensitive; many pipelines keep identifiers and personal details, and cloud LLM tools may receive raw posts.",
        "Generated explanations can contain invented numbers or clinical-sounding claims that are not supported by the data.",
    ])

    r.h2("1.3 Problem Statement")
    r.p("__To design and implement a privacy-preserving, reproducible framework that analyses mental-health-related text by age band "
        "and by language (English, Hindi, Marathi and Romanized code-mixed variants), measures how well text classifiers perform for "
        "each group, explains the learned patterns, and uses Generative AI only on aggregated, verified statistics to produce "
        "age-wise insights and multilingual awareness content.__", italic=False)
    r.h3("Statement of scope")
    r.bl([
        "The system performs **research and awareness analysis**. It does not diagnose individuals, does not give treatment advice "
        "and does not replace professional care.",
        "Labels used are those supplied by public datasets (emotion proxies) or by a consented survey; they are not clinical diagnoses.",
        "Age analysis is performed only where an explicit, valid age (13-100 years) is available; ages are never inferred from text.",
        "Awareness content produced by the system is a draft that must be reviewed by a native speaker and a qualified person "
        "before any use.",
    ])

    r.h2("1.4 Motivation and Need")
    r.p("A model that is 85% accurate overall but only 60% accurate for English-writing users, or for teenagers, is not a reliable "
        "foundation for any awareness programme. Fairness in mental-health NLP has been raised as a concern for gender and race "
        "[15], but age and Indian-language variation have received far less attention. At the same time, awareness campaigns work "
        "best when they speak in the audience's language and tone. Combining group-wise evaluation with age- and language-aware "
        "content generation addresses both needs, provided that privacy and honesty constraints are built in from the start.")

    r.h2("1.5 Project Idea")
    r.p("The project is organised as a pipeline of small, testable modules that move from raw files to guarded text: "
        "load and validate, clean and anonymise, identify language, analyse by age and by language, train and compare models by "
        "group, aggregate statistics, and finally generate insights from the aggregates only. The same code runs on a synthetic "
        "dataset (for validation), on open datasets (BRIGHTER, a Reddit mental-health dataset) and on a consented survey with "
        "PHQ-9-based labels. A Streamlit dashboard and a command-line interface expose every step.")

    r.h2("1.6 Objectives at a Glance")
    r.tbl("Project objectives and the module that delivers each", ["ID", "Objective", "Main outputs"], [
        ["O1", "Age-wise text patterns", "Length/lexical features and distinctive terms per age band"],
        ["O2", "Age-based risk analysis (primary)", "Elevated-label share per band with Wilson CI, chi-square, Cramer's V"],
        ["O3", "Multilingual and code-mixed analysis", "Language distribution, code-mixing share, language-vs-label tests, normalisation effect"],
        ["O4", "Age x language analysis", "Cross-table with minimum-cell suppression and heat-map"],
        ["O5", "Group-wise model comparison, fairness, explainability", "Macro-F1 per group, bootstrap CI, fairness gaps, top features"],
        ["O6", "GenAI age-wise insights", "Verified narrative from aggregated statistics"],
        ["O7", "GenAI multilingual awareness content", "12 drafts: 3 languages x 4 age tones, pending human review"],
    ], widths=[0.5, 2.5, 3.5], fs=10, align=["c", "l", "l"])
    r.h2("1.7 Organisation of the Report")
    r.p("Chapter 2 reviews related work. Chapter 3 defines the problem, modules and algorithms. Chapter 4 presents the system design "
        "(architecture, DFDs, UML diagrams and the mathematical model). Chapter 5 gives the project plan. Chapter 6 reports "
        "implementation results, tests and discussion, and Chapter 7 concludes with future scope. References and appendices follow.")


LIT_TABLE = [
    ["1", "Low et al. (2020) [3]", "Reddit mental-health subreddits; LIWC and topic models; supervised classifiers",
     "Large Reddit corpus of mental-health communities; language differs markedly by condition",
     "English only; no age or language stratification"],
    ["2", "Yates, Cohan, Goharian (2017) [4]", "RSDD: self-reported depression diagnosis on Reddit; CNN/linear models",
     "Large-scale depression dataset built from self-reported diagnoses",
     "English; no age field; access restricted"],
    ["3", "Cohan et al. (2018) [5]", "SMHD: nine conditions with matched controls",
     "Multi-condition benchmark; condition-specific language", "English only; no demographic fairness analysis"],
    ["4", "De Choudhury et al. (2013) [11]", "Twitter behavioural and linguistic features with SVM",
     "Early evidence that social-media language predicts depression", "Small sample; English; no group-wise evaluation"],
    ["5", "Schler et al. (2006) [8]", "Blog Authorship Corpus; age and gender differences in word use",
     "Shows systematic age-related vocabulary shift", "Not mental-health specific; English; 2000s blogs"],
    ["6", "Aguirre, Harrigian, Dredze (2021) [15]", "Fairness audit of depression models by gender and race",
     "Performance differs across demographic groups", "Age and Indian languages not covered"],
    ["7", "Muhammad et al. (2025) [6], [7]", "BRIGHTER: human-annotated emotion data in 28 languages (incl. Hindi, Marathi, English)",
     "Open multilingual emotion data and shared task", "Emotion labels, not mental-health diagnosis; no age field"],
    ["8", "Khanuja et al. (2021) [17]", "MuRIL: transformer pre-trained for Indian languages and transliterated text",
     "Strong gains on Indian-language tasks", "General NLP model; not applied to mental-health fairness"],
    ["9", "Patwa et al. (2020) [18]", "SemEval-2020 Task 9: sentiment of Hindi-English code-mixed tweets",
     "Established code-mixed sentiment benchmark", "Sentiment, not mental health; no age"],
    ["10", "Ji et al. (2022) [19]; Yang et al. (2023) [21]; Xu et al. (2024) [20]",
     "MentalBERT, MentaLLaMA and Mental-LLM: domain-adapted and instruction-tuned language models",
     "LLMs improve mental-health prediction and give explanations", "Raw text sent to models; hallucination risk; English-centred"],
    ["11", "Harrigian et al. (2021) [14]", "Survey of datasets used in mental-health NLP",
     "Documents data bias, label noise and demographic gaps", "Review only; no new framework"],
]


def chapter2(r):
    r.chapter(2, "Literature Survey")
    r.h2("2.1 Overview")
    r.p("The literature relevant to this project falls into five groups: (a) datasets and early studies of mental-health language "
        "on social media; (b) the effect of age and demographics on language; (c) multilingual and code-mixed NLP for Indian "
        "languages; (d) modern language-model and Generative AI approaches; and (e) fairness, ethics and statistical practice. "
        "This chapter summarises representative work in each group and then identifies the gap addressed by this project. "
        "Bibliographic details should be verified against the original sources before final submission.")

    r.h2("2.2 Review of Existing Work")
    r.h3("2.2.1 Mental-health language on social media")
    r.p("**Paper:** Predicting depression via social media. **Authors:** M. De Choudhury, M. Gamon, S. Counts, E. Horvitz (ICWSM 2013) [11]. "
        "**Description:** The authors crowd-sourced depression scores for Twitter users and showed that behavioural and linguistic "
        "features (activity, social-network, emotion and language style) can predict depression, establishing social media as a "
        "signal for mental-health research.")
    r.p("**Paper:** Depression and self-harm risk assessment in online forums (RSDD). **Authors:** A. Yates, A. Cohan, N. Goharian "
        "(EMNLP 2017) [4]. **Description:** A large Reddit dataset of users who self-report a depression diagnosis, with matched "
        "controls; neural and linear models were compared. The work set the standard for forum-scale datasets but is English-only.")
    r.p("**Paper:** SMHD: a large-scale resource for exploring online language usage for multiple mental-health conditions. "
        "**Authors:** A. Cohan et al. (COLING 2018) [5]. **Description:** Extends RSDD to nine conditions and shows that "
        "condition-specific language differences exist, again without demographic stratification.")
    r.p("**Paper:** NLP reveals vulnerable mental-health support groups and heightened health anxiety on Reddit during COVID-19. "
        "**Authors:** D. E. Low et al. (J. Med. Internet Res., 2020) [3]. **Description:** A public Reddit dataset of "
        "mental-health communities analysed with NLP; its labels are community-based, which is why this project treats "
        "Reddit labels as proxies only.")
    r.h3("2.2.2 Age and demographic effects")
    r.p("**Paper:** Effects of age and gender on blogging. **Authors:** J. Schler, M. Koppel, S. Argamon, J. Pennebaker (2006) [8]. "
        "**Description:** The Blog Authorship Corpus shows that word choice shifts systematically with age. This motivates "
        "analysing text patterns per age band (O1) instead of pooling all users.")
    r.p("**Paper:** Gender and racial fairness in depression research using social media. **Authors:** C. Aguirre, K. Harrigian, "
        "M. Dredze (EACL 2021) [15]. **Description:** Depression classifiers perform unequally across gender and race; "
        "the authors recommend group-wise evaluation. This project applies that idea to age and language.")
    r.h3("2.2.3 Multilingual and code-mixed NLP for Indian languages")
    r.p("**Paper:** BRIGHTER. **Authors:** S. M. Muhammad et al. (2025) [6], with the SemEval-2025 Task 11 overview [7]. "
        "**Description:** Human-annotated emotion data for 28 languages, including English, Hindi and Marathi. It is the open "
        "multilingual dataset used here for real-data runs; its emotion labels are mapped to a negative-affect proxy.")
    r.p("**Paper:** MuRIL: Multilingual representations for Indian languages. **Authors:** S. Khanuja et al. (2021) [17]. "
        "**Description:** A transformer pre-trained on Indian languages and their transliterated forms, a promising future "
        "backbone. **Paper:** SemEval-2020 Task 9 on Hindi-English code-mixed sentiment (Patwa et al. [18]) provides "
        "benchmarks for code-mixed text.")
    r.h3("2.2.4 Language models and Generative AI")
    r.p("MentalBERT [19], Mental-LLM [20] and MentaLLaMA [21] adapt or prompt language models for mental-health prediction and "
        "explanation, and XLM-R [16] gives general multilingual representations. They improve accuracy and can explain "
        "predictions, but they usually send raw text to the model, can hallucinate, and are evaluated mostly in English. "
        "This project instead restricts Generative AI to **aggregated statistics** and verifies every number it produces.")
    r.h3("2.2.5 Ethics, fairness and statistics")
    r.p("Blodgett et al. [22] argue that bias studies in NLP need clear definitions of harm; Benton et al. [30] describe "
        "ethical protocols for social-media health research; Harrigian et al. [14] document dataset biases. For statistics "
        "the project uses Wilson intervals [23], the Benjamini-Hochberg correction [24] and log-odds term ranking [25].")

    r.h2("2.3 Summary of Literature Survey")
    r.tbl("Literature survey", ["S.N.", "Author / year", "Methodology", "Findings", "Drawbacks / gap"], LIT_TABLE,
          widths=[0.4, 1.2, 1.7, 1.7, 1.5], fs=8.5, align=["c", "l", "l", "l", "l"])

    r.h2("2.4 Research Gap")
    r.p("Across the surveyed work, no single study was found that jointly (i) stratifies results by **age band and language**, "
        "(ii) covers **Hindi, Marathi and Romanized code-mixed text**, (iii) reports **group-wise fairness gaps with confidence "
        "intervals and explainability**, and (iv) uses **Generative AI only on aggregated, number-verified statistics** to "
        "produce age-aware and language-aware awareness material. This statement is based on the limited review above and should "
        "be confirmed by a systematic search before it is presented as a claim of novelty.")
    r.h2("2.5 Summary")
    r.p("Existing studies establish that social-media text carries mental-health signals, that language varies with age, and that "
        "models can be unfair across groups. What is missing is an open, reproducible, privacy-aware workflow that combines these "
        "elements for Indian languages. Chapter 3 formalises the problem that fills this gap.")


def chapter3(r):
    r.chapter(3, "Problem Definition and Scope")
    r.h2("3.1 Proposed Problem Definition")
    r.p("Given a collection of text records, each with a language and optionally an explicit age, and a label (an emotion proxy or "
        "a PHQ-9 band mapped to elevated / not elevated), the system must: (1) clean and anonymise the data; (2) describe how "
        "label rates and wording differ by age band and language; (3) train standard text classifiers and quantify how their "
        "performance differs across age bands, languages and age x language cells; (4) explain what each model relies on; and "
        "(5) produce age-wise insights and multilingual awareness drafts whose numbers are guaranteed to match the analysis.")
    r.h2("3.2 Existing System and Its Disadvantages")
    r.p("Existing practice is a single classifier trained on pooled English data, reported with one overall accuracy or F1 score. "
        "Its disadvantages are:")
    r.bl(["group-wise performance and fairness gaps are invisible;",
          "age and Indian-language variation are ignored or confounded;",
          "raw text and identifiers are often retained, creating privacy risk;",
          "LLM-written explanations may contain unverified numbers or clinical claims;",
          "experiments are hard to reproduce (no fixed seeds, no author-grouped validation, so posts of one author leak between "
          "train and test)."])
    r.h2("3.3 Proposed Solution: Modules")
    r.tbl("Software modules", ["Module", "Source file(s)", "Responsibility"], [
        ["Data loading and validation", "src/data/load.py, validate.py", "Read CSV/TSV/JSON/JSONL/XLSX, auto-map columns, profile missing values, duplicates, labels"],
        ["Cleaning", "src/data/clean.py", "PII scrubbing, duplicate and conflicting-label removal, age validation 13-100, author hashing"],
        ["Language layer", "src/data/language.py, normalize.py", "Rule-based language ID, Romanized Hindi/Marathi detection, conservative normalisation"],
        ["Age and language analysis", "src/analysis/", "O1-O4 tables, statistics, figures"],
        ["Models", "src/models/train.py", "TF-IDF pipelines, grouped CV, group metrics, bootstrap CI, fairness gaps, explainability"],
        ["Generative AI", "src/genai/", "Facts builder, offline/online generator, guardrails, awareness content"],
        ["Interface", "app.py, main.py", "Streamlit dashboard (8 pages) and CLI (fetch-open, check, clean, analyze, run, genai, full)"],
    ], widths=[1.6, 1.8, 3.1], fs=9.5)
    r.h2("3.4 Area, Scope and Limitations")
    r.bl(["Area: computational social science and responsible AI for mental-health awareness.",
          "Scope: English, Hindi, Marathi and Romanized forms (Hinglish, Roman Marathi); text of at least 3 characters; "
          "five age bands 13-17, 18-25, 26-35, 36-45 and 46+.",
          "Out of scope: clinical diagnosis, individual risk scoring, crisis response, and any age inference from text.",
          "Groups smaller than 30 records are suppressed in reports; groups smaller than 100 are not given model metrics."])
    r.h2("3.5 Details of Algorithms")
    r.h3("3.5.1 Feature extraction")
    r.p("Each text is represented by a union of two TF-IDF spaces: word unigrams and bigrams, and character n-grams of length 2 to 5 "
        "(analyzer char_wb). Character n-grams are important because Romanized Hindi and Marathi have no standard spelling, "
        "and Devanagari words are well captured by sub-word patterns.")
    r.h3("3.5.2 Classifiers")
    r.bl(["**Logistic Regression** - linear probabilistic model; coefficients give direct explanations.",
          "**Linear SVM (LinearSVC)** - maximum-margin linear model; usually strongest on sparse text.",
          "**Complement Naive Bayes** - generative baseline that handles class imbalance well but is weaker on short text."])
    r.h3("3.5.3 Validation and metrics")
    r.p("StratifiedGroupKFold with 5 folds keeps every post of an author in one fold and preserves class ratios; the full run "
        "is repeated for seeds 42, 7 and 2024, and the out-of-fold predictions are pooled. Reported metrics are accuracy, "
        "macro-precision, macro-recall, macro-F1 and the Matthews Correlation Coefficient [28]. For each group with at least "
        "100 records the macro-F1 receives a 95% bootstrap interval (200 resamples), and the **fairness gap** is the maximum "
        "minus the minimum group macro-F1.")
    r.h3("3.5.4 Statistical tests")
    r.bl(["Chi-square test of independence with Cramer's V (effect size) for label vs age band and label vs language.",
          "Kruskal-Wallis test with epsilon-squared for numeric text features across groups.",
          "Wilson score interval for proportions [23] and Benjamini-Hochberg correction for multiple tests [24].",
          "Log-odds ratio with informative Dirichlet prior (z-score) to rank group-distinctive terms [25]."])
    r.h3("3.5.5 Generative AI guardrails")
    r.p("The generator receives only a facts dictionary built from aggregates. Two checks run on every output: "
        "**verify_numbers**, which requires each number to match a fact at its own precision, and **check_safety**, which rejects "
        "banned clinical or directive phrases. If either check fails, the system falls back to a deterministic offline template. "
        "Awareness drafts are always marked PENDING_HUMAN_REVIEW and carry a helpline placeholder "
        "[ADD VERIFIED LOCAL HELPLINE].")
    r.h2("3.6 Goal")
    r.p("To show, with reproducible code and honest reporting, how mental-health text analysis changes when age and language are "
        "treated as first-class dimensions, and to provide a safe pattern for using Generative AI on top of such analysis.")
    r.h2("3.7 Requirements")
    r.tbl("Functional requirements", ["ID", "Requirement"], [
        ["FR1", "Load CSV, TSV, JSON, JSONL and XLSX files and auto-map column names."],
        ["FR2", "Validate data and report missing values, duplicates, label and age problems."],
        ["FR3", "Scrub PII, remove duplicates and conflicting labels, hash author identifiers."],
        ["FR4", "Derive age bands from explicit ages only; mark age analysis unavailable otherwise."],
        ["FR5", "Identify language and code-mixing; normalise Romanized text conservatively."],
        ["FR6", "Produce age-wise and language-wise label statistics with confidence intervals and tests."],
        ["FR7", "Train three classifiers with author-grouped CV and multiple seeds."],
        ["FR8", "Report group-wise metrics, bootstrap CIs and fairness gaps."],
        ["FR9", "Generate verified age-wise insights and multilingual awareness drafts."],
        ["FR10", "Expose all steps through a CLI and a Streamlit dashboard."],
    ], widths=[0.7, 5.8], fs=10, align=["c", "l"])
    r.tbl("Non-functional requirements", ["ID", "Requirement"], [
        ["NFR1", "Reproducibility: fixed seeds, configuration in config.yaml, deterministic offline GenAI."],
        ["NFR2", "Privacy: no raw text or identifiers leave the pipeline; only aggregates reach GenAI."],
        ["NFR3", "Honesty: every report states label type, sample size and limitations."],
        ["NFR4", "Testability: automated tests for each module (39 tests)."],
        ["NFR5", "Portability: Python 3.10+ on Windows, Linux or macOS, no GPU required."],
    ], widths=[0.7, 5.8], fs=10, align=["c", "l"])
    r.tbl("Hardware and software used", ["Item", "Specification"], [
        ["Hardware", "Standard laptop/PC, 8 GB RAM; no GPU needed (linear models on sparse features)"],
        ["Operating system", "Windows 11 (portable to Linux/macOS)"],
        ["Language", "Python 3.14 (virtual environment)"],
        ["Libraries", "pandas, NumPy, SciPy, scikit-learn, matplotlib, seaborn, Streamlit, PyYAML, joblib, openpyxl, requests, pytest"],
        ["Optional", "OpenAI-compatible API (model gpt-4o-mini) for online GenAI mode"],
        ["Tools", "VS Code, Git/GitHub, Microsoft Word/PowerPoint for documentation"],
    ], widths=[1.6, 4.9], fs=10)
    r.h2("3.8 Objectives")
    r.p("The objectives O1 to O7 listed in Table 1 of Chapter 1 are the formal objectives of the project. Acceptance criteria: "
        "(a) every objective produces tables and figures from a single command; (b) all automated tests pass; (c) results "
        "are reproducible from the stated seeds; and (d) no generated sentence passes the guardrail unless every number in it matches "
        "the computed statistics.")
