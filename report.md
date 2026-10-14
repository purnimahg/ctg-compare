# ctg-compare — comparability report

**A** · [NCT06470828](https://clinicaltrials.gov/study/NCT06470828) · snapshot 2026-09-14  
**B** · [NCT07455383](https://clinicaltrials.gov/study/NCT07455383) · snapshot 2026-09-14  
Rendered 2026-10-04 21:01:27Z · **11 checks / 13 comparisons**

This report names where two registered trials are not measuring the same thing in the same patients. It reports counts and field values. It does not reach a conclusion about either trial — see *What this report will not say*, below.

## Counts

| Verdict | n | Comparisons |
|---|---|---|
| SAME | 4 | C1, C8, C3, C4 |
| SAME (N1) | 1 | C6 |
| DIFFERENT | 3 | C2, C7a, C7b |
| REVIEW | 1 | C5 |
| NOT REPORTED | 1 | C10 |
| NOT REPORTED (M) | 3 | C9, C11a, C11b |
| UNPARSED | 0 | — |
| **total** | **13** | |

- **PRECONDITION** 2 — C1, C8
- **MATURITY** 4 — C9, C10, C11a, C11b
- **COMPARABILITY** 7 — C2, C3, C4, C5, C6, C7a, C7b

## Record maturity

**DIFFERENT LIFECYCLE STAGES** — this block prints whether or not it fires, because an absent check and a passed check look identical to a reader.

| | A | B |
|---|---|---|
| results posted | 2026-08-31 | None |
| overall status | COMPLETED | RECRUITING |
| primary completion | 2025-06-03 | 2027-05 |
| …date type | ACTUAL | ESTIMATED |
| FDA-regulated drug | True | True |
| US sites / total | 15 / 53 | 22 / 42 |

Every NOT REPORTED below may reflect this rather than a sponsor's disclosure practice. Verdicts tagged **(M)** are the ones where a results obligation has not yet been triggered at all. **(M) means confounded, not excused.** The submission deadline itself is a legal determination with exceptions — see 42 CFR 11.44 — and is not computed here.

## PRECONDITION — 2

*Is a comparison meaningful at all? Shared phase, shared arm structure.*

| Check | | Verdict | Field |
|---|---|---|---|
| C1 | phase | **SAME** | `protocolSection.designModule.phases` |
| C8 | arm types | **SAME** | `protocolSection.armsInterventionsModule.armGroups[].type` |

## MATURITY — 4

*Is the record complete enough to compare, or simply young?*

| Check | | Verdict | Field |
|---|---|---|---|
| C9 | results posted | **NOT REPORTED (M)** | `protocolSection.statusModule.resultsFirstPostDateStruct.date` |
| C10 | method described | **NOT REPORTED** | `protocolSection.outcomesModule.primaryOutcomes[0].description` |
| C11a | document labels | **NOT REPORTED (M)** | `documentSection.largeDocumentModule.largeDocs[].label` |
| C11b | document dates | **NOT REPORTED (M)** | `documentSection.largeDocumentModule.largeDocs[].date` |

## COMPARABILITY — 7

*Are the two trials measuring the same thing in the same people?*

| Check | | Verdict | Field |
|---|---|---|---|
| C2 | minimum age | **DIFFERENT** | `(path not reported)` |
| C3 | maximum age | **SAME** | `protocolSection.eligibilityModule.maximumAge` |
| C4 | sex eligible | **SAME** | `protocolSection.eligibilityModule.sex` |
| C5 | main measurement | **REVIEW** | `protocolSection.outcomesModule.primaryOutcomes[0].measure` |
| C6 | measurement timing | **SAME (N1)** | `protocolSection.outcomesModule.primaryOutcomes[0].timeFrame` |
| C7a | masking level | **DIFFERENT** | `protocolSection.designModule.designInfo.maskingInfo.masking` |
| C7b | who was masked | **DIFFERENT** | `protocolSection.designModule.designInfo.maskingInfo.whoMasked` |

## What this report will not say

The verdicts above are counts over registry fields. This tool has no standing to turn them into an overall judgement, so the rendered text is checked mechanically against a published list of phrasings it may not contain:

<!-- published refusal list - excluded from the refusal scan -->

```
  are comparable
  not comparable
  broadly comparable
  directly comparable
  is comparable
  aren't comparable
  more transparent
  less transparent
  more forthcoming
  better disclosure
  worse disclosure
  we conclude
  we assess
  overall assessment
  our view
  score:
  grade:
  rating:
  ranked
```

<!-- end published refusal list -->

A render containing any of them fails and writes nothing. The list is published so the refusal can be audited rather than trusted — which necessarily puts every forbidden phrase into this document, so the block above is fenced out of the scan. That exclusion is the one hole in the guard; it is marked in the source of this file and tested against a planted sentence outside it.

Three boundaries worth naming explicitly:

- **A document-presence field attests existence, not completeness.** 42 CFR 11.48(a)(5) permits redacting trade secret and confidential commercial information before submission, so a posted statistical analysis plan may have its model redacted. See `KNOWN-LIMITATIONS.md`, L4.
- **Free-text eligibility criteria are not parsed.** They are printed verbatim elsewhere under *human read required*, and no claim is made.
- **The assay behind an eligibility threshold is absent from every field path, permanently.** Two trials can enrol materially different populations and the registry will not show it.

## Verdict legend

Generated from the verdict constants in the code at render time, not written into this template.

- **SAME** — Both records carry the field and the values match.
- **SAME (N1)** — Matched only after rule N1 removed words that DIFFERED. The count of erased words is shown; the tool does not judge whether they mattered.
- **DIFFERENT** — Both records carry the field and the values do not match.
- **REVIEW** — Free text, still unlike after N1. The tool is not authorised to rule on meaning in either direction. A word diff is printed instead.
- **NOT REPORTED** — Absent from at least one record, or present and empty. Silence is not agreement.
- **NOT REPORTED (M)** — Absent, AND the record missing it has no results obligation triggered yet. CONFOUNDED, not excused.
- **UNPARSED** — Present but unreadable - outside the field's controlled vocabulary, or not parseable as a value. Never guessed.

