# S9 and S11 acceptance record — written AFTER the fact, and labelled as such

    Written:   15 Oct 2026, after the runs
    Status:    SHIPPED — pushed to github.com/purnimahg/ctg-compare

**This file breaks the rule every other acceptance file in this repo keeps.**
S3 through S8 had criteria written and dated before their code existed. S9
and S11 ran on ship day, criteria and code together, and this record was
written afterwards. Saying so is the only honest option: an acceptance record
backdated to look prospective would be worth less than no record at all.

What makes it still usable: S9's known answers did not come from me. The two
trials were chosen by the operator from clinicaltrials.gov against four
stated conditions, with no prior inspection by the person who wrote the code.
That is weaker than a pre-written known-answer table and stronger than a
self-chosen demo.

---

## S9 — domain independence

**Criteria, as stated before the fetch:** a different disease area, both
Phase 3 interventional, one with results posted and one without, both with a
primary outcome measure and time frame. Chosen by the operator, not by Claude.

**Pair chosen:**

    A  NCT02924727  PARADISE-MI    ARNI vs ACEi post-MI, 5,669 participants
                                   results posted 2023-06-22
    B  NCT04023552  Lp(a)HORIZON   pelacarsen, 8,323 participants
                                   no results; primary completion 2026-07-16

**Result: 13 verdicts, zero code changes.**

    SAME 3 · SAME (N1) 0 · DIFFERENT 3 · REVIEW 3 ·
    NOT REPORTED 4 · NOT REPORTED (M) 0 · UNPARSED 0      total 13
    PRECONDITION 2 · MATURITY 4 · COMPARABILITY 7         total 13

**P** — domain independence demonstrated.

### What S9 actually produced, which was not the domain proof

**L9 — the specification's first line was not implemented.** *"Input: a set of
NCT IDs."* For eight sessions the input was whichever files were in `data/`.
With one pair those are indistinguishable; with two the glob would have
compared one orexin trial against one cardiology trial and reported thirteen
confident verdicts about it. Found by trying to use the tool as specified.
FIXED: `--ids`, and a refusal when more than two trials are present and none
are named.

**L10 — provenance was recovered from the display layer.** C2's row read
`(path not reported)` while the report promised every verdict traces to a
field path. Found by reading the rendered table on an unfamiliar pair — the
same defect had been sitting in the orexin render the previous day, unseen,
because a familiar table is read for what you expect it to say. FIXED: every
row declares its path as data, and the renderer refuses to write if one does
not.

**`NOT REPORTED (M) = 0`, and this is the strongest result in the file.**
B's primary completion date had PASSED (2026-07-16, ACTUAL) with no results
posted. The guard therefore withheld `(M)` — it will not excuse that absence
on maturity grounds — and equally refused to accuse. It printed both dates
and pointed at 42 CFR 11.44.

● The orexin fixture could not have produced this. There, B's clock had not
started, so `(M)` was earned on every maturity check. This pair is the guard
distinguishing *"too early to expect results"* from *"results are late"* —
which is the line between a true and a false sentence about a sponsor, and
the entire reason the guard exists. S6 Run 6 was constructed to prove the
guard could turn off. A real 8,323-patient trial turned it off, for the right
reason, on ship day.

---

## S11 — README, stranger test, public

**Fresh clone into /tmp, rendered, diffed against the working copy:**

    5c5
    < Rendered 2026-10-15 12:23:39Z
    > Rendered 2026-10-15 12:22:32Z

**One line. The render timestamp — the exclusion named in the README in
advance.** The reproducibility claim is tested, not asserted. **P**

**Also found by the stranger test, before any stranger arrived:** the L9
refusal added the previous day broke the README's own first command.
`python3 report.py` now correctly refuses, because `data/` holds four trials.
Caught by running the instruction as written. The quickstart names the pair;
the selftest is pinned to the orexin fixture so S3–S7's recorded known
answers cannot silently repoint.

**Staleness, checked against the live registry on ship day:** NCT07455383 is
**STALE** — sponsor edited it 2026-10-07, after the 2026-09-14 snapshot;
modules changed `contactsLocationsModule, statusModule`. Per S8 Q5 the
snapshot was **kept** and the report says so by name. Not re-fetched: every
acceptance record in this directory is evidence against the 14 Sep snapshots.

**S10 — not run as a session.** Converted to public issues by decision on 12
Oct. `KNOWN-LIMITATIONS.md` holds L1–L10, every one found in use, three of
them on 3 Oct and three on 15 Oct, including a correction to L1's own stated
mechanism. ● A repo with ten honestly logged limitations is better evidence
of adversarial testing than a session asserting it happened.

---

## Ship record

    git  967fca2   S1–S8
         2add2fa   S8 provenance, S9 domain proof, S11 README; L7–L10
    pushed 15 Oct 2026, 44 objects, 173.57 KiB
    31 files · 11 checks · 13 comparisons · 7 verdict states · L1–L10
