# S8 acceptance criteria - provenance

    Written:      12 Oct 2026
    Code written: NOT YET
    Ships in:     3 days

    Produces:
      1. a PROVENANCE block in report.md
      2. provenance.json  - a manifest written at FETCH time, not render time
      3. resume-check.py reporting WHICH modules changed (fixes L7)
      4. git initialised, .gitignore correct, first commit, first push

    Why this session is not optional. PUBLISHED, by your own definition, is
    "public repo, runnable by a stranger, every claim traceable to source
    field + retrieval date." S8 is the clause after the second comma. Without
    it the repo contains thirteen verdicts and no way for a reader to tell
    which bytes produced them.

>>> Claude's proposals are marked [PROPOSED]. STRIKE OUT what you disagree
>>> with. A proposal left standing is YOUR criterion.
>>>
>>> On S7 you left all six slots blank and the one thing that needed
>>> catching - a count of 3 against four listed checks - went through. The
>>> arithmetic in this file is the part to check, not the prose.

---

## Known answers, read off the files on 12 Oct BEFORE any code exists

Both shipping snapshots are dated **2026-09-14**:

                              A · NCT06470828      B · NCT07455383
    file bytes on disk        101,421              23,120
    sha256(file)[:12]         94b4173acf06         d052ce3b83e5
    protocolSection fp[:12]   eafee41b7c33         ec68dfcd1377
    lastUpdatePostDate        2026-08-31           2026-09-03
    studyFirstPostDate        2024-06-24           2026-03-06
    retrieved (UTC)           2026-09-14T11:15:22  2026-09-14T11:15:22
    response bytes (log)      57,613               14,574

---

## Q1. Which facts, and what are they called?

[PROPOSED] Per record, seven: NCT ID · snapshot file name · retrieval
timestamp UTC · response bytes · file bytes · sha256 of the file ·
protocolSection fingerprint. Plus the record's own `lastUpdatePostDate`.

[PROPOSED] **`response bytes` and `file bytes` are named separately and
never merged.** The log says 57,613 for A; the file on disk is 101,421. Both
correct - one is the API response, the other is after `fetch.py`
pretty-prints it. A provenance block printing one under the other's label is
off by 76%, looks entirely plausible, and cannot be checked at a glance.
That is L8, and it is the precise failure this tool exists to catch, found in
the tool's own audit trail.

    Strike out and replace if you disagree:


---

## Q2. Every line, or once per record?

The course document says provenance goes "on every line". That was written
before there were 13 rows and 7 facts per record.

[PROPOSED] **Per-record facts ONCE, in a provenance block. Field path on
every row** - which report.md already does.

[PROPOSED] Why this is a deliberate deviation and not a shortcut: the
retrieval timestamp is identical for all 13 rows, so printing it 13 times
adds 13 lines and zero information, and a one-page report has no room for
noise that cannot change. What varies per row is the field path, and that is
already there.

[PROPOSED] This is a **change to the plan of record**, flagged rather than
slipped in. If you disagree, the course document wins and I build it
per-line.

    Strike out and replace if you disagree:


---

## Q3. What can this repo NOT verify, and does it say so?

[PROPOSED] It cannot verify the four existing snapshots retroactively.

[PROPOSED] Why: `provenance.json` records a fingerprint **at fetch time**,
from the bytes as received. The four snapshots in `data/` were fetched on 2
and 14 Sep, before that file existed. Computing their fingerprints now reads
them from the files themselves - so the manifest would agree with the files
by construction, and prove nothing. **A checksum you generate from the thing
you are checking is decoration.**

[PROPOSED] So the provenance block states, for each snapshot, whether its
fingerprint was recorded at fetch time or computed later, and the four
shipping snapshots are marked `computed post hoc - not independently
verified`. Tamper detection begins with the next fetch.

[PROPOSED] ● This is the most defensible thing in the session and the most
tempting to skip. Writing the fingerprints into a manifest today and calling
it provenance would look identical to a reader and be worth nothing. Saying
so costs one column and is the only version a stranger can trust.

    Strike out and replace if you disagree:


---

## Q4. Reproducibility - what exactly is the claim?

[PROPOSED] A stranger who clones the repo and runs `python3 report.py` gets
`report.md` **byte-identical except for one line**: the render timestamp.

[PROPOSED] The excluded line is named in the README, and the claim is tested
(Run 2) rather than asserted. "Reproducible" with an unstated exclusion is
how a reproducibility claim becomes false without anyone noticing.

    Strike out and replace if you disagree:


---

## Q5. The snapshots will be 31 days old at ship. What does the report say?

[PROPOSED] It prints the age in days next to each snapshot, computed at
render time, and it does NOT re-fetch.

[PROPOSED] Plus one thing you do on ship day: run `resume-check.py` and
record the result in the repo. If a record has changed, the report says so
and the snapshot stays - a dated snapshot that no longer matches the registry
is still a valid object of study, as long as the report says it is stale
rather than pretending it is current.

[PROPOSED] Why not re-fetch on ship day: every acceptance record in this
repo is evidence against the 14 Sep snapshots. Re-fetching invalidates all
seven sessions' known answers three days before ship.

    Strike out and replace if you disagree:


---

## Q6. resume-check.py cries wolf. Fix it how? (L7)

[PROPOSED] Keep the fingerprint over all of `protocolSection` - narrowing it
risks missing a sponsor edit - and make STALE carry a REASON: the list of
top-level modules whose contents changed.

    STALE: referencesModule          <- registry auto-linked a paper
    STALE: eligibilityModule, outcomesModule   <- a real amendment

[PROPOSED] Why not exclude `referencesModule`: a sponsor can also edit
references, and that is a real change. The noise is not reduced; it is made
legible, which is the only safe direction. A check that fires on nothing gets
ignored, then fires on something real and is still ignored.

    Strike out and replace if you disagree:


---

## Q7. What goes into git?

[PROPOSED] IN: every `.py`, every `.md`, `fields.csv`, `retrieval_log.txt`,
`provenance.json`, and **all four snapshots in `data/`**.
[PROPOSED] OUT: `__pycache__/`, `*.pyc`, `.DS_Store`.

[PROPOSED] Why the snapshots go in, at ~245 KB: they are the fixture. A
stranger cannot run this repo without them, because the network path is
exactly what they may not have. Committing the data is what makes the
reproducibility claim in Q4 possible at all.

    Strike out and replace if you disagree:


---

## Runs

**Run 1 - render with provenance.** Both 14 Sep snapshots.

    [PROPOSED] Every value in the known-answer table above appears in
    report.md, correctly labelled, with `response bytes` and `file bytes`
    distinct.
    [PROPOSED] Both snapshots marked `computed post hoc`.
    [PROPOSED] Age in days printed and equal to (render date - 2026-09-14).

**Run 2 - the reproducibility claim.** Render twice, diff the two files.

    [PROPOSED] Exactly ONE line differs: the render timestamp.
    [PROPOSED] Must NOT be: zero lines (the timestamp is not being written)
    or more than one (something else is non-deterministic, and a report that
    changes between runs cannot be cited).

**Run 3 - tamper.** One byte of B's snapshot altered.

    [PROPOSED] The file sha256 and the protocolSection fingerprint both
    change, and the report prints the changed values.
    [PROPOSED] It does NOT claim to have detected tampering - it cannot,
    for these four snapshots, and Q3 says so in the report itself. What the
    run proves is that the fingerprint is sensitive to one byte, which is
    what makes it worth recording going forward.

**Run 4 - resume-check reason.** The 02 Sep and 14 Sep Takeda snapshots.

    [PROPOSED] Reports STALE with reason `referencesModule`, and nothing
    else.
    [PROPOSED] Known answer, diffed by hand on 12 Oct: exactly 4 leaf
    changes, all under `protocolSection.referencesModule.references[0]` -
    citation, pmid, and type=DERIVED. `lastUpdatePostDate` is 2026-08-31 in
    BOTH. The date did not move; the record did.

**Run 5 - missing provenance.** `retrieval_log.txt` renamed away.

    [PROPOSED] The render FAILS LOUDLY and writes nothing.
    [PROPOSED] Must NOT be: a report with the provenance block omitted, or
    with blanks in it. An unprovenanced report that still renders is this
    project's own failure shape at the last layer - correct verdicts, no
    chain of custody, and nothing on the page to say so.

---

## After the run

    python3 report.py --selftest --record

Mark P or F per line. No summary mark. Check the arithmetic and the labels,
not the prose.
