# ctg-compare

**A tool that names where two registered clinical trials are not measuring the
same thing in the same patients.**

Input: a set of NCT IDs. Output: a one-page comparability report in which
every verdict traces to a named field path in a dated snapshot committed to
this repository.

It reports counts over registry fields. **It does not conclude whether two
trials are comparable** — that judgement belongs to a reader, and the report
is checked mechanically against a published list of sentences it may not
contain.

---

## Run it

Python 3.8+. **No dependencies** — standard library only, deliberately, so
that a stranger needs no `pip install` and no network.

```
git clone <this repo>
cd ctg-compare
python3 report.py --ids NCT06470828 NCT07455383
```

That renders `report.md` from snapshots already committed here — no network
needed. The committed `report.md` is this pair.

`data/` ships two pairs, so **you have to name which two records to compare.**
Run it without `--ids` and it refuses:

```
$ python3 report.py
data/ holds snapshots for 4 trials: NCT02924727, NCT04023552, ...
Which two should be compared? Name them:
  python3 report.py --ids NCT... NCT...
Refusing to guess - picking two by filename order would compare records
that may have nothing to do with each other and report thirteen confident
verdicts about it.
```

That refusal is deliberate, and it is the youngest thing in this repo: for
eight sessions the input was *"whichever files are in `data/`"* while the
specification's first line said *"Input: a set of NCT IDs."* With one pair in
the folder those are indistinguishable. With two they are not. See L9.

To fetch and compare a different pair:

```
python3 fetch.py NCT02924727 NCT04023552
python3 report.py --ids NCT02924727 NCT04023552
```

To check whether your snapshots are still current, and to let the report say
so:

```
python3 resume-check.py
```

`fetch.py` is the only script that touches the network. Everything else runs
against files on disk.

---

## What it checks — 11 checks, 13 comparisons

C7 and C11 each report two values, which is why the two numbers differ. Both
are computed, never hard-coded.

| Category | Checks | The question it answers |
|---|---|---|
| **PRECONDITION** | C1 phase, C8 arm types | Is a comparison meaningful at all? |
| **MATURITY** | C9 results posted, C10 method described, C11a/b documents | Is the record complete, or simply young? |
| **COMPARABILITY** | C2/C3 age limits, C4 sex, C5 measure, C6 timing, C7a/b masking | Same thing, same people? |

**Precondition is printed first, deliberately.** If two trials do not share a
phase or an arm structure, every comparability verdict below is conditional
on a comparison whose basis is in question — and printing "C2 DIFFERENT"
above "C1 DIFFERENT" invites a reader to compare minimum ages between a
Phase 2 and a Phase 3 trial.

### Seven verdicts

The report generates its own legend from the constants in the code, so the
two cannot drift. In summary:

- **SAME** / **DIFFERENT** — both records carry the field; values match or don't.
- **SAME (N1)** — matched *only* after the declared tidying rule N1 removed
  words that differed, **with a count of how many**. The tool never decides
  whether an erased word mattered; it reports the price of agreement. One
  erased word is tidying. Ten is erasing.
- **REVIEW** — free text, still unlike after N1. The tool is not authorised
  to rule on meaning *in either direction*, so it prints a word diff instead.
- **NOT REPORTED** — absent from at least one record, or present and empty.
  **Silence is not agreement.**
- **NOT REPORTED (M)** — absent, *and* the record missing it has no results
  obligation triggered yet. **Confounded, not excused.**
- **UNPARSED** — present but unreadable: outside the field's controlled
  vocabulary, or not parseable. Never guessed.

### The maturity guard

Without it, this fixture supports the sentence *"Sponsor A disclosed their
statistical model and their SAP; Sponsor B disclosed neither."* That sentence
is **false while every underlying field value is correct** — the error has
moved out of the code and into the conclusion.

So the guard keys on the **primary completion date**, because that is what
42 CFR 11.48 keys the results obligation on, and `hasResults: false` means
something entirely different for a trial that finished two years ago and one
that finishes in 2027. It prints both dates with their ACTUAL/ESTIMATED type
and does **not** compute the submission deadline — that is a legal
determination with exceptions (see 42 CFR 11.44).

`(M)` is earned only where an absence is **logically impossible otherwise**.
`primaryOutcomes[].description` is a registration-time field, so its absence
is never excused on maturity grounds, and the report prints that reasoning
rather than hiding it.

---

## What it refuses to do

- **Conclude.** No statement that two trials are or are not comparable, no
  comparison of sponsor transparency, no score or grade. Counting is not
  concluding: *"4 of 13 comparisons are NOT REPORTED, 3 confounded by record
  maturity"* is a count. The refusal list is printed in every report so it
  can be audited rather than trusted, and a render containing any of those
  phrasings fails and writes nothing.
- **Parse free-text eligibility criteria.** Printed verbatim under *human
  read required*; no claim made.
- **Open PDFs.** A posted protocol or SAP is reported as *existing*, never as
  *readable*: 42 CFR 11.48(a)(5) permits redacting confidential commercial
  information before submission, so `hasSap: true` does not mean the
  statistical model is legible.
- **Report the assay behind an eligibility threshold.** It is absent from
  every field path, permanently. Two trials can enrol materially different
  populations and the registry will not show it. **This boundary is the
  point:** the tool marks exactly where the public record stops.

---

## Provenance and reproducibility

Every report carries, per record: snapshot filename, retrieval timestamp
(UTC), HTTP status, snapshot age in days, **response bytes and file bytes
reported separately** (the API response and the pretty-printed file on disk
differ by ~76%, and merging them would be a plausible-looking wrong number),
`sha256` of the file, the `protocolSection` fingerprint, and the sponsor's
own last-edit date.

**Reproducibility claim, with its exclusion named:** a clone of this repo
renders `report.md` byte-identical to the committed copy **except the
`Rendered` line** in the header, which carries the render timestamp.

**Fingerprint honesty.** `provenance.json` records a fingerprint at *fetch*
time, from the bytes as received. Snapshots taken before that file existed
are marked `computed post hoc — not independently verified`: their hashes
were computed from the very files they would be checking, so agreement is by
construction. **A checksum generated from the thing it checks is
decoration.** Tamper detection is live from the 2026-10-15 snapshots onward.

**Staleness.** `resume-check.py` is the only thing that asks the registry
whether a snapshot is still current; it writes its verdicts to
`staleness.json`, and the report cites that file rather than guessing. A
snapshot that no longer matches the registry is **kept** — a dated snapshot
is still a valid object of study, provided the report says it is stale.

---

## The fixture is not the subject

`data/` ships two pairs:

| Pair | Trials | Why |
|---|---|---|
| Orexin agonists, narcolepsy type 1 | NCT06470828 (Takeda), NCT07455383 (Alkermes) | The development fixture. Every acceptance record in `acceptance/` is evidence against these two snapshots. |
| Cardiology | NCT02924727 (PARADISE-MI), NCT04023552 (Lp(a)HORIZON) | **The domain-independence test.** Chosen after the tool was finished, in an unrelated disease area, and rendered 13 verdicts with zero code changes. |

The cardiology pair also produced the clearest demonstration of the maturity
guard: an 8,323-patient Phase 3 whose primary completion date had **passed**
with no results posted. The guard withheld `(M)` — it will not excuse that
absence on maturity grounds — and equally refused to accuse. It printed both
dates and pointed at the regulation. The orexin fixture could not have shown
this, because there the second trial's clock had not started.

---

## How this was built, and why that is the interesting part

Every session's **acceptance criteria were written and dated before its code
existed**, in `acceptance/`. Criteria are amended by appending a dated
amendment, never by editing — an acceptance file is evidence.

That discipline is what found the defects. The sharpest example:
`report.py` reported a 683-character field as **absent from both records**,
because two copies of a path-walking helper had diverged by one regular
expression. No exception, no warning, a real verdict word on a
plausible-looking result. What caught it was a known-answer table written by
hand from the raw JSON *before* the renderer existed. The run disagreed with
the paper, and the paper was right.

The reverse has also happened: a hand-written count in one criteria file said
`SAME 3` above four listed checks, in a column summing to 12 under a printed
total of 13. The code was right and the paper was wrong. **The discipline is
not that the paper is authoritative — it is that the two must agree, and
whichever is wrong gets found by the disagreement.**

Verdicts are written into acceptance records **by the tool**, never retyped
by a human (`record.py`); the human marks pass or fail. Hand transcription
from a screen into a document is a step with no chain of custody, and twice
an acceptance record disagreed with what the tool printed — both times the
record was wrong.

`KNOWN-LIMITATIONS.md` holds **L1–L10**, every one found in use rather than
imagined, including a correction to L1's own stated mechanism.

---

## Known gaps, honestly

- **C12, record-against-itself consistency** — a record can claim TRIPLE
  masking while naming two masked parties, and no between-record comparison
  notices. Not built.
- **Keyed list comparison (L2)** — positional diffing of `locations[]`
  invents differences when a sponsor inserts a site.
- **Word order is treated as meaningless in C5/C6 (L3)** — accepted, with
  disclosure, because the alternative breaks C6.
- **Five copies of `load()`** across the checkers and the renderer are not
  consolidated (L9). The *tool* takes named NCT IDs; the per-checker
  `--selftest` harnesses stay pinned to the orexin fixture on purpose,
  because those runs are the acceptance evidence for S3–S7.
- **No timepoint parser.** A parser that silently mis-parses is a new source
  of confident wrong answers — the exact thing this tool exists to catch.

---

## Licence and provenance of the data

Code: MIT. Trial records: retrieved from the public
[ClinicalTrials.gov REST API v2](https://clinicaltrials.gov/data-api/api),
no authentication, with retrieval times recorded in `retrieval_log.txt`.
