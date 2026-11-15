# 04 – Track C Survey, Consent and Ethics Pack (DRAFT)

**Status:** Draft for supervisor / ethics committee review. Do not collect data until written approval is received.
Items in [brackets] must be filled in by you. Legal and ethics requirements differ by institution; follow your committee's rules over this draft.

---

## 1. Steps before collecting any data
1. Show this document to your supervisor and obtain written approval (keep the email or signed form).
2. Submit to the institutional ethics committee if one exists; wait for the decision.
3. Decide who can see raw responses (recommended: only you and your supervisor) and where they are stored (password-protected drive, not public cloud links).
4. Fill in a verified helpline for your region wherever `[HELPLINE]` appears. Do not guess numbers.
5. Pilot with 5 volunteers who are told it is a test; fix confusing questions.
6. Collect, export to CSV, and run the pipeline (`python main.py full --input <file>`).

## 2. Study summary
- **Purpose:** a student research project studying how written text about mood relates to age group and language, and how well simple software models work across groups.
- **Who:** adults aged 18+ (see Section 7 for minors). Recommended: do **not** include under-18s in this mini project unless the ethics committee and guardians' consent procedure allow it; this removes the 13-17 band from Track C data.
- **What:** about 5 minutes; 4 short questions plus a mood questionnaire and one free-text answer.
- **Voluntary:** participants may skip any question and stop at any time.

## 3. Consent page (show first; participant must tick to continue)

> **Research information and consent**
> I am a student at [institution] working on a research project supervised by [supervisor name]. The project studies how people write about their mood in different languages and age groups. It is **not** a medical or diagnostic test, and your answers will not be used to assess you personally.
>
> **What you will do:** answer a few questions and write 2-4 sentences about how you have felt recently, in English, Hindi, Marathi or a mix.
>
> **Privacy:** do not write your name, phone number, email, address, school/workplace or other identifying details. No names or emails are collected. Answers are stored securely, shown only in summary form, and individual texts will not be published.
>
> **Voluntary:** taking part is optional. You can leave any question blank or close the form at any time. Once submitted, responses cannot be traced back to you, so they cannot be removed later.
>
> **Wellbeing:** some questions are about low mood. If you feel upset, you can stop at any time. If you are struggling or in danger, please contact [HELPLINE] or local emergency services. This form is not monitored in real time.
>
> **Contact:** [your email] / [supervisor email] / [ethics committee contact].
>
> ☐ I am 18 years or older. ☐ I have read this information and agree to take part.

## 4. Survey questions

| # | Question | Type | Maps to |
|---|---|---|---|
| 1 | Your age group | Single choice: 18-25, 26-35, 36-45, 46+ | `age_band` |
| 2 | Language you will write in | Single choice: English, Hindi, Marathi, Hinglish (Hindi+English) | `preferred_language` |
| 3 | In 2-4 sentences, describe how you have felt over the last two weeks. Do not include names or contact details. | Free text | `mood_text` |
| 4 | PHQ-9 questionnaire (below) | 9 items, 0-3 each | `phq9_score` (sum, 0-27) |

Age bands are self-reported choices; the project never estimates age from writing.

### PHQ-9 (public-domain screening questionnaire)
"Over the last 2 weeks, how often have you been bothered by the following?" Options: 0 Not at all, 1 Several days, 2 More than half the days, 3 Nearly every day.
1. Little interest or pleasure in doing things
2. Feeling down, depressed, or hopeless
3. Trouble falling or staying asleep, or sleeping too much
4. Feeling tired or having little energy
5. Poor appetite or overeating
6. Feeling bad about yourself, or that you are a failure or have let yourself or your family down
7. Trouble concentrating on things
8. Moving or speaking so slowly that others could notice, or the opposite: being fidgety or restless
9. Thoughts that you would be better off dead, or of hurting yourself in some way

**Item 9 handling (important):** ask your supervisor/ethics committee whether to keep it. If kept, show the wellbeing message with `[HELPLINE]` immediately after submission to **every** participant, and state clearly that the form is not monitored in real time. If your committee prefers, use the shorter PHQ-2 (items 1-2) and adjust the label mapping with your supervisor.

Score bands used by the project (from `src/data/load.py`): 0-4 none, 5-9 mild, 10-19 moderate, 20-27 severe. These are **screening** categories for research grouping, not a diagnosis. Check the exact band wording against the official PHQ-9 guidance before reporting.

## 5. Form-to-file layout
Export responses as CSV with these columns (any order). The loader already understands this layout (see `data/sample/sample_survey_trackC.csv`):

```text
response_id,age_band,preferred_language,mood_text,phq9_score
R0001,18-25,Hindi,"...",7
```
Remove timestamps, emails and IP addresses from the export before use.

## 6. Data handling
- Store raw export in a restricted folder; never commit it to git (`data/raw/` is already git-ignored).
- Run only on the cleaned copy; PII scrubbing is applied automatically but is not perfect, so read samples manually.
- Set `codemixed.save_examples: false` in `config/config.yaml` for real data so raw text is not written to outputs.
- Do not send raw responses to any online AI service. The online mode only sends aggregated statistics.
- Report group results only where group size is at least 30 (analysis) or 100 (model metrics), as configured.
- Delete raw data after the project period set by your institution.

## 7. Minors
If under-18s are to be included, obtain approval for guardian consent and age-appropriate assent. Without it, restrict to 18+.

## 8. Sample size guidance
Age band x language gives up to 20 cells. With 300 responses most cells will have fewer than 30 answers, so the combined analysis (O4) will mostly report "insufficient evidence". A realistic target is 400+ responses, with recruitment spread across languages and ages. State this limitation in the report.

## 9. Responsible-use statement for the report
This study analyses text patterns for research. It does not diagnose, screen or assess any individual, and its models must not be used for decisions about people.
