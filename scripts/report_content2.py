"""Report content: Chapters 4-5."""
FIG = None  # set by builder


def chapter4(r, F):
    r.chapter(4, "System Design")
    r.h2("4.1 System Architecture")
    r.p("The system is a layered pipeline (Figure 1). Four kinds of input (BRIGHTER emotion data, a Reddit mental-health dataset, "
        "an own consented survey, and synthetic test data) enter through one ingestion layer. A cleaning layer produces the unified "
        "schema, the language and age layers add the two analysis dimensions, and four analysis modules (O1/O2, O3, O4, O5) "
        "write tables and figures. Everything the Generative AI layer sees must first pass the **privacy boundary**: a JSON file "
        "of aggregates from which groups below the minimum size have been removed.")
    r.fig(F / "fig_architecture.png", "System architecture", 5.0)
    r.h3("Unified data schema")
    r.tbl("Unified schema produced by the cleaning step", ["Column", "Meaning"], [
        ["source_id", "Hashed author or record identifier (used for author-grouped validation)"],
        ["text_original / text_clean / text_norm", "Raw text, PII-scrubbed text, and conservatively normalised text used by the models"],
        ["label", "Label after alias mapping (none, mild, moderate, severe, negative_affect, mh_forum ...)"],
        ["age, age_band", "Validated explicit age (13-100) and band (13-17, 18-25, 26-35, 36-45, 46+); 'unknown' otherwise"],
        ["language, language_source, language_detected", "Final language, whether it was provided or detected, and the detector output"],
        ["source", "Name of the input file or dataset"],
    ], widths=[2.2, 4.3], fs=9.5)

    r.h2("4.2 Data Flow Diagrams")
    r.h3("4.2.1 DFD level 0")
    r.p("The context diagram (Figure 2) shows one process and four external entities: the researcher, dataset providers, "
        "an optional LLM provider (which receives aggregated statistics only) and a human reviewer who approves awareness drafts.")
    r.fig(F / "fig_dfd0.png", "Context diagram (DFD level 0)", 5.6)
    r.h3("4.2.2 DFD level 1")
    r.p("Level 1 (Figure 3) splits the system into five processes: load and validate, clean and normalise, analyse O1-O4, train and "
        "evaluate O5, and generate insights. Four data stores hold raw datasets, the processed file, tables/figures/JSON and the "
        "saved best model.")
    r.fig(F / "fig_dfd1.png", "DFD level 1", 5.6)
    r.h3("4.2.3 DFD level 2")
    r.p("Figure 4 expands process 4.0. Features are built from the processed file, author-grouped cross-validation produces "
        "out-of-fold predictions for three seeds, group metrics and bootstrap intervals are computed, fairness gaps are derived "
        "and explainability tables and the best pipeline are written to the stores.")
    r.fig(F / "fig_dfd2.png", "DFD level 2 for process 4.0", 5.6)

    r.h2("4.3 UML Diagrams")
    r.h3("4.3.1 Use-case diagram")
    r.p("Three actors interact with the system (Figure 5): the analyst, who runs and reads every analysis; an optional LLM "
        "provider used in online mode; and a reviewer who checks the awareness drafts.")
    r.fig(F / "fig_usecase.png", "Use-case diagram", 5.3)
    r.h3("4.3.2 Activity diagram")
    r.p("The activity diagram (Figure 6) highlights the three decisions that shape the run: whether reliable ages exist, whether "
        "the online LLM is enabled, and whether the guardrail passes.")
    r.fig(F / "fig_activity.png", "Activity diagram", 4.9)
    r.h3("4.3.3 Sequence diagrams")
    r.fig(F / "fig_seq_training.png", "Sequence diagram: pipeline execution and model training", 6.0)
    r.fig(F / "fig_seq_testing.png", "Sequence diagram: GenAI insight generation with guardrail", 6.0)
    r.h3("4.3.4 Class (module) diagram")
    r.p("Although the code base is mostly functional, the modules play the role of classes (Figure 9); the operations listed are "
        "real function names from the source code.")
    r.fig(F / "fig_class.png", "Class (module) diagram", 5.6)

    r.h2("4.4 Flowchart of the Core Algorithm")
    r.p("Figure 10 shows the group-wise evaluation procedure: grouped folds, training on the training fold only (so no text from the "
        "test authors influences TF-IDF vocabulary or model weights), pooling of out-of-fold predictions, the minimum group size of "
        "100 for model metrics, and the fairness-gap computation.")
    r.fig(F / "fig_flowchart.png", "Flowchart: group-wise model evaluation", 4.9)

    r.h2("4.5 Mathematical Model")
    r.p("The system is described as S = {I, P, O} with inputs I, processes P and outputs O.")
    r.p("**Inputs.** I = {D, C}, where D = {(t_i, y_i, a_i, l_i)}, i = 1..N, is the dataset of text t_i, label y_i, optional age a_i "
        "and language l_i, and C is the configuration (age edges, minimum group sizes, seeds, bootstrap count).")
    r.p("**Processes.** P = {P1, ..., P6}:")
    r.bl(["P1 (clean): D' = {(scrub(t_i), y_i, band(a_i), l_i) : a_i in [13, 100] or a_i missing}, duplicates removed.",
          "P2 (age band): band(a) = b_k if e_k <= a < e_(k+1) with edges e = (13, 18, 26, 36, 46, 101).",
          "P3 (proportion with CI): for group g with k elevated of n records, p = k / n and the Wilson interval is shown below.",
          "P4 (TF-IDF): x_i = [tfidf_word(t_i) ; tfidf_char(t_i)], with idf(w) = ln((1 + N) / (1 + df(w))) + 1.",
          "P5 (classifier): f(x) = argmax_c (w_c . x + b_c) for LR and SVM, trained on the training fold only.",
          "P6 (group metrics and fairness): macro-F1 per group and gap = max_g F1_g - min_g F1_g."])
    r.eq("Wilson interval = [ p + z^2/2n -/+ z * sqrt( p(1-p)/n + z^2/4n^2 ) ] / (1 + z^2/n),   z = 1.96", "1")
    r.eq("macro-F1 = (1/|C|) * sum over classes c of  2 * P_c * R_c / (P_c + R_c)", "2")
    r.eq("MCC = (TP*TN - FP*FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))   (multi-class generalisation used)", "3")
    r.eq("Cramer's V = sqrt( chi^2 / ( N * (min(r, c) - 1) ) )", "4")
    r.eq("fairness gap(G) = max over g in G of F1_g  -  min over g in G of F1_g,   n_g >= 100", "5")
    r.p("**Outputs.** O = {tables, figures, analysis_summary.json, insights.md, awareness.md, best_model.joblib}. The guardrail "
        "function V(text, facts) returns True only if every number in text equals a fact at the precision it is written and "
        "no banned phrase occurs; otherwise the offline template is returned, so the final text always satisfies V.")
    r.h2("4.6 Privacy and Ethics by Design")
    r.bl(["PII patterns (URLs, e-mails, handles, phone numbers) are replaced by tokens before any analysis.",
          "Author identifiers are hashed; author-grouped validation prevents leakage and avoids user-level inference.",
          "Reports suppress groups with n < 30; model metrics need n >= 100.",
          "Only aggregates reach the (optional) LLM; offline mode is the default.",
          "Survey data requires informed consent, withdrawal rights and ethics approval (consent pack in docs/04).",
          "Labels are described as proxies; the dashboard has a Limitations page."])


def chapter5(r, F):
    r.chapter(5, "Project Plan")
    r.h2("5.1 Methodology and Phases")
    r.p("Development followed 13 phases (P0-P12) with a deliverable and a verification step in each; later phases were started "
        "only when the previous phase's tests passed.")
    r.tbl("Phase plan", ["Phase", "Activity", "Deliverable / check"], [
        ["P0", "Literature study and scope", "Objectives O1-O7, requirements FR/NFR"],
        ["P1", "Environment and project skeleton", "Repository layout, config.yaml, virtual environment"],
        ["P2", "Dataset acquisition and audit", "Dataset research notes, open-data fetchers"],
        ["P3", "Cleaning and unified schema", "clean.py, validate.py, cleaning audit report"],
        ["P4", "EDA for O1, O2, O3", "Age and language tables, statistics, figures"],
        ["P5", "Code-mixed pipeline", "Language ID, conservative normalisation, effect test"],
        ["P6", "Models and group-wise evaluation", "Grouped CV, metrics, bootstrap CI, fairness gaps"],
        ["P7", "Age x language analysis (O4)", "Cross-table with suppression, heat-map"],
        ["P8", "Explainability", "Top positive features per class and group"],
        ["P9", "GenAI age insights (O6)", "Facts builder, guardrails, offline template"],
        ["P10", "GenAI awareness content (O7)", "12 reviewed-pending drafts"],
        ["P11", "Dashboard", "Streamlit app with 8 pages, UI tests"],
        ["P12", "Report and presentation", "Mini project report, slides, appendix"],
    ], widths=[0.6, 2.7, 3.2], fs=9.5, align=["c", "l", "l"])
    r.h2("5.2 Project Schedule")
    r.p("The plan spans one semester of 16 weeks. Several phases overlap (for example explainability with age x language "
        "analysis), as shown in the Gantt chart (Figure 11).")
    r.fig(F / "fig_gantt.png", "Project timeline", 6.3)
    r.h2("5.3 Team and Responsibilities")
    r.tbl("Roles and responsibilities", ["Role", "Responsibility"], [
        ["Student developer(s)", "Literature review, data pipeline, analysis and modelling, dashboard, testing, documentation"],
        ["Project guide", "Scope approval, methodology review, weekly progress review, ethics guidance"],
        ["Native-speaker reviewer", "Review of Hindi and Marathi awareness drafts for tone and accuracy"],
        ["Project coordinator", "Schedule, format and submission compliance"],
    ], widths=[1.8, 4.7], fs=10)
    r.h2("5.4 Risk Management")
    r.tbl("Risks and mitigations", ["Risk", "Impact", "Mitigation"], [
        ["No reliable age field in open data", "O1/O2/O4 cannot be run on real data", "Mark age analysis unavailable; use consented survey (Track C) and synthetic data for code validation"],
        ["Proxy labels are not diagnoses", "Over-interpretation", "State label meaning in every report; Limitations page"],
        ["Small cells after stratification", "Unstable estimates", "min n = 30 for reporting, 100 for model metrics; suppress and mark"],
        ["Author leakage between train and test", "Inflated scores", "StratifiedGroupKFold by hashed author"],
        ["LLM hallucination", "Wrong numbers or unsafe text", "Aggregates only; number verification; offline fallback; human review"],
        ["Privacy breach", "Harm to users", "PII scrubbing, hashing, no raw text to LLM, consent pack"],
        ["Dataset licence or access limits", "Cannot redistribute data", "Fetch scripts instead of bundled data; document terms"],
    ], widths=[1.9, 1.7, 2.9], fs=9.5)
