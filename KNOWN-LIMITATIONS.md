# Known limitations

Every entry here was found in real use, not invented. A limitations file that
says "none known" is a claim no reviewer believes.

---

## L1 - `lastUpdatePostDate` does not detect every change

**Found** 2026-09-14, in normal use of `resume-check.py`.

`resume-check.py` reported NCT06470828 as CURRENT because its
`lastUpdatePostDateStruct.date` was unchanged at 2026-08-31. The record had in
fact changed: between 2026-09-02 and 2026-09-14 it gained a
`protocolSection.referencesModule.references[0]` entry - a PubMed citation
(PMID 42714024) with `type: DERIVED`.

`lastUpdatePostDate` moves only when the **sponsor** submits a change. The
registry also edits records by itself - auto-linking publications, regenerating
MeSH terms - and does not touch that date when it does.

**Consequence if unfixed:** a tool that trusts `lastUpdatePostDate` alone will
tell you your saved copy is current when it is not. The report it then produces
is internally consistent, fully traceable, and quietly wrong.

**Status: FIXED 2026-09-14.** `resume-check.py` now also compares a SHA-256
fingerprint of `protocolSection`, and reports a sponsor edit and a content
change separately. `derivedSection` is excluded from the fingerprint because the
registry regenerates it constantly and it would cry wolf.

---

## L2 - Comparing lists by position invents differences

**Found** 2026-09-14, diffing the two NCT07455383 snapshots.

The first diff reported **89 changed fields** in
`contactsLocationsModule.locations`, including things like
`locations[11].city: "St Louis" -> "Novi"`. No site moved from Missouri to
Michigan. Alkermes inserted new sites earlier in the list, and every entry after
the insertion point shifted index by one. The diff compared position 11 to
position 11 and reported the shift as a change.

The real change was: **seven sites added** (France x2, Italy, Japan x3,
Wisconsin), two removed.

**Consequence:** any check that compares a list by position will produce a flood
of false differences whenever the list order is not meaningful. In a
comparability report those false positives are worse than useless - they bury
the true findings and train the reader to ignore the output.

**Applies to:** C8 (arm types) above all, and to any future check on locations,
interventions, or outcomes. C8's spec already requires multiset comparison -
order ignored - and the S4 break test exists to prove it. This entry is the
real-world justification for that break test.

**Status: OPEN for the diff tooling.** Not a defect in the 11 checks as
specified, but the diff helper used during development needs a keyed comparison
before it is trusted.

---

## L3 - Word order is treated as meaningless in C5 and C6

**Found** 2026-09-20, by Purnima, reading the S5 Run 5 output.

C5 and C6 compare the *set* of words left after the N1 tidying rule, not
their sequence. So two strings containing identical words in a different
order are called SAME.

Most of the time that is right. "Change from baseline in sleep latency" and
"change in sleep latency from baseline" are the same endpoint written two
ways, and treating them as different would be crying wolf.

**Where it is wrong:** any string whose meaning depends on the order of two
named things.

    "improvement in A compared to B"
    "improvement in B compared to A"

Identical word sets. Opposite claims. This check returns SAME.

**Why the design is still multiset:** the diff the check prints - shared
words, only in A, only in B - is inherently a set operation. Making the
verdict order-sensitive while the displayed evidence is order-blind would
mean the verdict and the evidence answer different questions, and a reader
could not reason from one to the other.

**Mitigation, added the same day:** when a SAME verdict is reached by
multiset while the tidied strings differ in sequence, the output now says
so explicitly and points here. It is disclosed rather than silent.

**Status: OPEN, accepted with disclosure.** Fixing it properly means
deciding when sequence carries meaning in free text, which is the
interpretation authority this tool refuses to claim.


## L4 - a document-presence field attests existence, not completeness

**Found 3 Oct 2026, from the regulation rather than from the data.**

`documentSection.largeDocumentModule.largeDocs[].hasSap` is a boolean. It
says a document labelled Statistical Analysis Plan was posted. It does not
say the document is intact.

42 CFR 11.48(a)(5) expressly permits the responsible party to redact
"any trade secret and/or confidential commercial information" before
submission. A sponsor may therefore satisfy the requirement with a document
whose statistical model is blacked out.

**Consequence for any claim this tool supports:** "Sponsor A disclosed their
statistical analysis plan" is NOT supported by `hasSap: true`. What is
supported is the existence, label, date, size and upload date of a file.

**Status:** OPEN, and permanently so for v0.1 - the tool does not open PDFs.
C11 prints the caveat alongside every document it reports. The question of
how much of a given SAP is legible is answered by a person opening it, which
is exactly where this tool is designed to hand over.


## L5 - two empty lists compared as equal. FIXED 3 Oct 2026.

**Found by writing S6's acceptance criteria, before S6's code existed.**

`check_s4.vocab_check` compares lists as multisets. `Counter([]) ==
Counter([])` is True, so two trials whose `armGroups` is an empty list
returned:

    C8  ARM TYPES                                 SAME
        A   [0]
        B   [0]
        =   Same 0 value(s). Order ignored.

The code announced that it was agreeing about zero values and called it
SAME. No exception, no warning, no bug in any line of it.

**Why it survived S4 acceptance (16 Sep).** S4's six runs all fed populated
lists - reordered, altered, one entry removed. None fed an empty one. The
check was correct for every input it was ever shown.

**Why it matters more than the arms.** The same shape reaches any multiset
comparison in this repo: `whoMasked`, `phases`, `largeDocs[].label`. And it
is the cleanest example in the project of the failure the tool exists to
catch - **clean code, no error, wrong answer** - found by specifying the
test before writing the thing it tests.

**Fix:** an explicit guard ahead of the multiset branch. A list that is
present and empty returns NOT REPORTED with the reason "present but empty",
distinguished in the output from a field that is absent.

**Status:** FIXED. Regression-tested by S6 Run 5, which is symmetric on
purpose - one empty list is easy to catch, two is the case that agreed with
itself.


## L6 - two `dig` implementations, one regex apart. FIXED 3 Oct 2026.

**Found by S6 Run 1, against a known answer written before the code existed.**

The repo had grown two copies of the same path-walking helper:

    check_s4.dig    stripped a bare `[]`, treated `[0]` as part of the key
    check_s5.dig    resolved both, via re.match

`check_s6.py` imported the first. C10 reads

    protocolSection.outcomesModule.primaryOutcomes[0].description

and reported it **ABSENT from both records**. Record A holds 683 characters
of it, including the MMRM model name.

**Why this is the worst failure mode in the project so far.** It produced a
REAL VERDICT WORD - NOT REPORTED - on a PLAUSIBLE-LOOKING result, because B
genuinely is absent and "absent from both" reads as unremarkable. No
exception. No warning. Nothing to notice. A reader would have concluded that
neither sponsor described their method, when one of them described it in
detail and named their statistical model.

**What caught it.** Nothing in the code. The S6 acceptance file recorded
"A 683 chars / B absent" as a known answer, by hand, from the snapshot,
BEFORE check_s6.py existed. The run disagreed with the paper and the paper
was right. That is the entire argument for writing acceptance criteria first,
demonstrated on the single most dangerous bug in the repo.

**This is the S2 lesson recurring inside the tooling.** `[0]` and `[]`
differ by one character and mean opposite things - the loudest comment in
`extract.py`. The same confusion then reappeared in a helper function, in a
different file, written later.

**Fix, two parts:**

1. `check_s4.dig` now resolves `[n]` as well as `[]`, making the two
   implementations equivalent in power.
2. `check_s6.py` carries **system-suitability assertions at import** - a
   known input with a known answer, checked before any record is read. If a
   future change hands the module a weaker helper, it fails loudly instead of
   silently downgrading a verdict. Same discipline as system suitability
   before a bioanalytical run.

**Status:** FIXED. The remaining duplication (two `dig` bodies in two files)
is cosmetic now that both are equivalent and one is asserted; consolidating
them into a shared module is v0.2, deliberately not done 12 days from ship.


## L1 — CORRECTION, 12 Oct 2026. The stated mechanism was wrong.

L1 above records that NCT06470828 gained PMID 42714024 "auto-linked by the
registry as `type: DERIVED`", and that the fix was to fingerprint
`protocolSection` **with `derivedSection` excluded**.

The fix works. **The reason given for it does not.** Diffing the two Takeda
snapshots leaf by leaf, the change is:

    protocolSection.referencesModule.references[0].citation   ABSENT -> present
    protocolSection.referencesModule.references[0].pmid        ABSENT -> 42714024
    protocolSection.referencesModule.references[0].type        ABSENT -> DERIVED

Four leaf differences, **all inside `protocolSection`**. `type: DERIVED` is a
field VALUE describing where the reference came from. It is not
`derivedSection`, which is a different part of the record entirely.

● So the fingerprint caught the change for a reason other than the one
written down. Excluding `derivedSection` did not make the check robust
against registry-generated content — registry-generated references live
inside `protocolSection` and the fingerprint sees them.

**A fix that works for the wrong reason is one refactor away from not
working.** Anyone reading L1 and tidying `resume-check.py` on the strength of
it would have reasoned from a false model.

---

## L7 — `resume-check.py` will cry wolf. FIXED 15 Oct 2026.

Direct consequence of the L1 correction.

`protocolSection.referencesModule` accumulates **registry-generated** PubMed
citations. Every time PubMed auto-links a new paper to NCT06470828, the
fingerprint changes and `resume-check.py` reports **STALE** — for a completed
Phase 3 trial with results posted, that will happen repeatedly and none of it
is a protocol amendment.

● The original design note for the fingerprint said `derivedSection` was
excluded because "the registry regenerates it constantly and it would cry
wolf." The intent was right. The exclusion does not achieve it.

**Why this matters more than its size:** `resume-check.py` is the first
command of every session and the README will tell a stranger to run it. A
check that fires on nothing gets ignored, and then fires on something real
and still gets ignored. **A false-positive source in a staleness check is how
a tool stops being read.**

**Status: FIXED 15 Oct 2026.** `resume-check.py` now prints a `MODULES` line
naming every top-level `protocolSection` module whose contents changed, and
says so explicitly when `referencesModule` is the only one. First live use,
the same day, on NCT07455383: `MODULES contactsLocationsModule,
statusModule` — a real sponsor amendment, legible in two seconds instead of a
23,000-line diff.

● **This heading read OPEN for two days after the code was fixed, including
through the public push.** A document that says a defect is open when it is
closed is the same failure as L1's wrong reason and the course artifact's four
verdict states: the record disagreeing with the thing it describes. Corrected
17 Oct, and noted rather than quietly edited, because the pattern is the
finding.

**The fix:** keep the fingerprint over all of
`protocolSection` — narrowing it risks missing a sponsor edit to references —
and make STALE carry a REASON: which top-level modules changed. A line
reading `STALE: referencesModule only (DERIVED citation added)` is
self-evidently not a protocol amendment, and one reading
`STALE: eligibilityModule, outcomesModule` is. The quantity of noise is
unchanged; its legibility is not.

---

## L8 — the retrieval log's byte count is not the file's byte count. Found 12 Oct 2026.

    retrieval_log.txt   2026-09-14  ...  57613 bytes   NCT06470828
    data/NCT06470828_2026-09-14.json               101421 bytes on disk

Both numbers are correct. They measure different things: the log records the
**API response** as received, and `fetch.py` pretty-prints the JSON before
saving, which nearly doubles it.

● A provenance block that prints one of these and labels it the other is a
wrong number of exactly the kind this tool exists to catch — plausible,
unverifiable at a glance, and off by 76%. S8 names them separately:
`response bytes` and `file bytes`.

**Status: FIXED 15 Oct 2026.** `provenance.py` returns the two as separate
fields and `report.md` prints both rows with a note that they measure
different things. **This entry carried no status line at all until 17 Oct.**


## L9 — the spec's first line was not implemented. Found 14 Oct 2026 by S9.

The artifact specification opens:

> **Input: a set of NCT IDs.**

It was not. For eight sessions the input was *"whichever JSON files happen to
be in `data/`"*. Five copies of `load()` globbed the directory and took the
newest snapshot per ID.

**With one pair in the folder those two things are indistinguishable.** With
two pairs they are not: `sorted(best.items())` would hand `report.py` the two
lowest-numbered NCT IDs — potentially one orexin trial and one trial from a
different disease entirely — and the renderer would produce thirteen
confident verdicts comparing them. Every check would be correct. The
comparison would be meaningless.

● **Found by the session designed to find it.** S9 exists to prove the tool
is domain-agnostic, and the first thing that happens when you try to point it
at a second disease is that you cannot: there is no way to say which two
records you mean. The claim in the spec and the behaviour of the code had
diverged, and only an attempt to use it as specified could show that.

● It also means the `fetch.py` TRIALS list made the **fetcher**
domain-specific while every **check** was domain-agnostic. A stranger reading
`fetch.py` would have been right not to believe the README.

**Fix, 14 Oct:**

1. `fetch.py` takes NCT IDs on the command line; the orexin pair is a
   documented default, not the subject.
2. `report.py` takes `--ids NCT… NCT…`, and **refuses to run** when `data/`
   holds more than two trials and no pair is named. Refusing is the point:
   guessing from filename order is how a tool produces a precise answer to a
   question nobody asked.

**Deliberately NOT fixed before ship:** the five `load()` copies in
`check_c2/s4/s5/s6` and `report.py` are not consolidated. Each checker's
`--selftest` stays pinned to the orexin fixture on purpose — those runs are
the acceptance evidence for S3 through S7, and repointing them three days
before ship would invalidate seven sessions of recorded known answers. The
TOOL takes named IDs; the HARNESSES stay bound to the fixture. Consolidation
is v0.2.


## L10 — provenance was recovered from the display layer. FIXED 15 Oct 2026.

**Found on ship day, by S9, by reading the rendered table on an unfamiliar
pair — not by any test.**

`report.py` built each row's field path by scanning the checker's output
lines for the first one starting `protocolSection` or `documentSection`.
`check_c2` does not print its path in that form, so C2's row rendered as:

    | C2 | minimum age | **SAME** | `(path not reported)` |

while the report's own Provenance section promised *"every verdict traces to
a field path in a dated snapshot"*. For C2 that was **false**, in the
shipping report, in both the orexin and cardiology renders.

● Two things worth keeping from this.

**Provenance must be DECLARED, not RECOVERED.** A field path scraped out of
rendered text is one formatting change away from vanishing — and it vanishes
into a plausible-looking string rather than an error. Every row now declares
its path as data, and the renderer **refuses to write** if any row lacks one.

**It was found by looking at output on data nobody had tuned against.** The
same defect sat in the orexin render the day before and went unseen, because
a familiar table is read for what you expect it to say. S9's purpose was to
prove domain-independence; its actual yield was a false claim in the
provenance layer.


---

## Status summary — added 17 Oct 2026

    L1   FIXED 14 Sep   (stated reason CORRECTED 12 Oct)
    L2   OPEN  by design — diff tooling only; not a defect in the 11 checks
    L3   OPEN  by design — accepted, disclosed in every C5/C6 verdict
    L4   OPEN  permanently for v0.1 — the tool does not open PDFs
    L5   FIXED  3 Oct
    L6   FIXED  3 Oct
    L7   FIXED 15 Oct   (its own heading said OPEN until 17 Oct)
    L8   FIXED 15 Oct   (had no status line until 17 Oct)
    L9   FIXED 14 Oct
    L10  FIXED 15 Oct

**Six fixed. Three open deliberately, with the reasoning published. One was
fixed in code while its own heading said OPEN.**

● **This file is not a defect backlog, and closing L2, L3 and L4 would make
the tool worse.** L3's "fix" reverts C6 to REVIEW and breaks a verdict that
currently works. L4 would require opening PDFs and judging redactions — the
adjudication this tool exists to refuse. L2 is a property of the diff helper,
not of any of the eleven checks.

A reader who finds three limitations stated with their trade-offs has more
reason to trust the eleven verdicts, not less. **The record of what the tool
refuses to do is the asset.** What was actually broken here was the
bookkeeping about the record — twice — which is the same thing that went wrong
five times during the build.
