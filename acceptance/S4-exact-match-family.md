# S4 acceptance criteria - C1, C3, C4, C8

Written by:  Purnima
Written on:  16 Sep 2026
Code written: NOT YET

Same rule as S3. This is filled in before the checks exist.

---

## Carried forward from S3 - the verdict list was incomplete

S3's acceptance file allowed three verdicts. The code returned four. The
fourth turned up only when the tool was fed a value neither of your two
trials contains:

    UNPARSED       the field is PRESENT, but the value cannot be understood
                   ("N/A", a bare "16" with no unit, "16 Fortnights")

It is a genuinely separate state from NOT REPORTED. Absent means the sponsor
said nothing. Unparsed means the sponsor said something and we cannot read
it. Collapsing them loses the difference between silence and noise.

So the full list from here on is FIVE:

    SAME · DIFFERENT · REVIEW · NOT REPORTED · UNPARSED

---

## The checks

    C1   phase          protocolSection.designModule.phases
    C3   maximum age    protocolSection.eligibilityModule.maximumAge
    C4   sex eligible   protocolSection.eligibilityModule.sex
    C8   arm types      protocolSection.armsInterventionsModule.armGroups[].type

C3 reuses the age reader built in S3. C1, C4 and C8 are controlled
vocabularies - the registry only permits a fixed set of words.

---

## Runs. What must each return, before the code exists?

**Run 1 - the real thing.** Both 14 Sep snapshots, unedited.

    C1 verdict:  SAME   C3 verdict:  SAME
    C4 verdict:  SAME   C8 verdict:  SAME

    For each one, what must the output line SHOW besides the verdict?
      - each of their values and how it is different and whats missing in each


**Run 2 - C8, arms reordered.** B's three arms listed in a different order,
nothing else changed.

    Verdict must be:         SAME
    Why: Order must not matter


**Run 3 - C8, one arm type changed.** One of B's EXPERIMENTAL arms changed
to ACTIVE_COMPARATOR.

    Verdict must be:         DIFFERENT
    Why: All arms must match


**Run 4 - C8, an arm removed.** B has 2 arms, A still has 3.

    Verdict must be:         DIFFERENT
    Must the output show:    how it is different and whats missing in each


**Run 5 - C1, phase list changed.** B's phases changed to
["PHASE2", "PHASE3"] - a real thing, seamless Ph2/3 trials exist.

    Verdict must be:         DIFFERENT
    Why: Phase must match exactly else it is different


**Run 6 - C4, a word outside the vocabulary.** B's sex changed to "Male"
instead of the registry's "MALE".

    Verdict must be:         UNPARSED
    Verdict must NOT be:     DIFFERENT
    Why: May not be a value in the options out of which we are expecting.


---

## The judgment call

C8 compares arm TYPES - placebo, experimental, active comparator. It does
not compare arm labels, so "OVE 1 mg BID" and "ALKS 2680 Dose 1" both count
simply as EXPERIMENTAL.

That means two trials of completely different drugs can return SAME on C8.

    Is that a useful finding, or a misleading one?   it is misleading 

    Because: we must compare the Intervention Name and the architecture associated with the drug name.


    If misleading, what would you change - compare something else, or keep
    the check and change what the output SAYS about it?

    NEITHER. Rejected both options offered, 16 Sep 2026.

    Reasoning: if C8 only establishes a shared structure and says nothing
    about the drugs, then SAME is the wrong word. It is not a weaker answer
    to the same question - it is an answer to a DIFFERENT question, and it
    needs its own measure and its own angle.

    Accepted consequence: the five verdicts (SAME / DIFFERENT / REVIEW /
    NOT REPORTED / UNPARSED) all answer one question - "do these two records
    agree on this field?" That question assumes the field measures the same
    thing in both trials. C8 does not. It describes trial ARCHITECTURE.

    Sharper form of what C8 should ask:  DO THESE TWO TRIALS SHARE A COMMON
    COMPARATOR? That is the precondition for any indirect comparison. Both
    have a placebo arm, so they are connected through placebo and an
    indirect comparison is structurally possible. Had one used only an
    active comparator, they would be disconnected and no indirect comparison
    could be made at all - regardless of how every other check came out.

    This generalises. Not all eleven checks answer the same question:

      COMPARABILITY  C2 C3 C4 (population) . C5 C6 C7 (measurement)
                     -> SAME / DIFFERENT / REVIEW / UNPARSED

      PRECONDITION   C1 (phase) . C8 (common comparator)
                     -> compatible / not compatible

      MATURITY       C9 C10 C11
                     -> present / absent, under the head-start warning

    DECISION: the grouping is deferred to S7, where the report is built and
    where the grouping actually shows up. S4 runs as written. The code is
    correct about the DATA - the arm multisets do match. What is under
    review is the WORD it reports that in. Those are two different things
    and collapsing them would muddle the acceptance record.


---

## After the run

    Did every run return what this file said it must?   Yes

    Anything the runs did not cover:   filled in by Claude, 16 Sep, after
    the run. Four gaps, in order of how much they matter.

    1. C3 WAS NEVER ACTUALLY TESTED. Six runs, six SAME verdicts - and the
       maximumAge field was never once edited. Six identical passes on an
       input that never changed is not evidence of anything. The check is
       not validated, it is just quiet.

    2. No absence case for any of these four. S3 tested a deleted key; S4
       never did. The NOT REPORTED path of C1, C3, C4 and C8 is untested.

    3. No EMPTY LIST case. "armGroups": [] - an arms section present but
       containing nothing - is a different thing from the key being absent,
       and both mean "no arms". Untested.

    4. Every run varies exactly one thing. Real records differ on several
       fields at once. Untested whether the output stays readable then.

    DECISION: gaps 1-3 roll into S6, which is the absence-and-blanks
    session, rather than reopening S4. Gap 4 is cosmetic and waits for S7.


---

## AMENDMENT 1 - 3 Oct 2026. S4 passed with a defect in it.

Appended, not edited. The record above stands as what was agreed and what
happened on 16 Sep.

**S4 was marked PASSED on 16 Sep. It was passing a `vocab_check` that
returned SAME for two trials with `armGroups: []`** - zero arms each -
because `Counter([]) == Counter([])` is True. Demonstrated 3 Oct:

    C8  ARM TYPES                                 SAME
        A   [0]
        B   [0]
        =   Same 0 value(s). Order ignored.

**This is not a mark that was recorded wrongly.** The six S4 runs were run
honestly and every one of them did what this file said it must. The defect
was in the CRITERIA: all six runs fed populated lists. The check was correct
for every input it was ever shown, and the input it was never shown is the
one that breaks it.

**What that says about acceptance criteria generally, and it is the most
useful thing S4 produced:** a passing acceptance run certifies the code
against the cases you thought of. It says nothing about the cases you did
not. The only defence is deliberately constructing inputs the fixture does
not contain - which is exactly what S3's `"16 Fortnights"` did (finding
UNPARSED) and what S6 Run 5 did here. **Both new findings in this repo came
from inputs neither real trial contains.**

**Fixed 3 Oct** in `check_s4.vocab_check`, logged as L5, and
regression-tested by S6 Run 5. C8's verdict on the real fixture is
unchanged: both trials have three populated arms, still SAME.

    S4's verdicts on the real fixture: UNCHANGED, all six.
    S4's status: PASSED, with L5 found and fixed afterwards.
