# S5 acceptance criteria - C5 and C6

    C5 = MAIN MEASUREMENT - what the trial measures
         protocolSection.outcomesModule.primaryOutcomes[0].measure

    C6 = MEASUREMENT TIMING - when it is measured
         protocolSection.outcomesModule.primaryOutcomes[0].timeFrame

Both values for both trials, read by hand on 14 Sep (see field-map.md):

    C5  A  "Change From Baseline to Week 12 in Mean Sleep Latency From the
             4 Maintenance of Wakefulness Test (MWT) Wake Trials"
        B  "Change in mean sleep latency (MSL) on Maintenance of Wakefulness
             Test (MWT) from baseline to Week 12 by dose level"

    C6  A  "Baseline, Week 12"
        B  "Baseline to Week 12"

Written on:  20 Sep 2026
Code written: NOT YET

>>> NEW FORMAT. Claude's proposals are filled in below, each marked
>>> [PROPOSED]. Your job is to STRIKE OUT what you disagree with and write
>>> your own. A proposal you leave standing is YOUR criterion - accepting a
>>> wrong one is on you exactly as if you had written it. Reviewing is not
>>> weaker than authoring; it is how most real specs actually get made.

---

## The problem, concretely

    A timing:  "Baseline, Week 12"      B timing:  "Baseline to Week 12"

Identical in meaning. A tool that flags this will cry wolf until you stop
reading it. But a tool that DECIDES two pieces of free text mean the same
thing is guessing, and guessing is what this project exists to refuse.

The way out is a tidying rule - N1 - published, short, auditable. Applied
before comparison. A stranger reads it and judges for themselves.

---

## Q1. Which words may N1 drop?

[PROPOSED] drop these five:      to · from · through · and · , (comma)
[PROPOSED] do NOT drop:          the · in · of · change · baseline

[PROPOSED] The test: does the word carry information about WHAT was
measured, WHEN, or IN WHOM? If no, it may go.

    "change" fails that test twice over. "Change in X" and "X" are
    different outcomes - change-from-baseline versus absolute value.
    "baseline" names a timepoint. Both must stay.

    "the", "in", "of" would PASS the test - they carry nothing. They are
    still excluded, for a different reason: no case we have seen needs
    them, and every entry spends audit budget.

[PROPOSED] The deeper rule, which matters more than the list: THE LIST
MUST BE THE MEMBERS OF A NAMEABLE CATEGORY, NOT A COLLECTION OF FIXES.
"Words that join two timepoints and carry no timepoint information" is a
rule a reviewer can check. "to and a comma" is a patch, and patches grow.

    Strike out and replace if you disagree: NIL - its perfect



---

## Q2. How long may N1 be, at most?

[PROPOSED] 5 items.

[PROPOSED] Why: the cap is not about correctness, it is about REVIEW. A
five-word list is read in two seconds. A thirty-word list is not read at
all, and one bad entry hides in it forever. The category above happens to
have five members, which is convenient rather than principled - if the
category legitimately grows, the cap moves and is re-justified in writing.

    Strike out and replace if you disagree: NIL - its perfect



---

## Runs

**Run 1 - the real thing.** Both 14 Sep snapshots, unedited.

    [PROPOSED] C5 (main measurement) verdict:    REVIEW
    [PROPOSED] C6 (measurement timing) verdict:  SAME

    [PROPOSED] Why C5 is not allowed to be DIFFERENT: the tool has no
    authority to interpret free text in EITHER direction. If it cannot
    declare two unlike strings to mean the same thing, it equally cannot
    declare them to mean different things.

    [PROPOSED] C5's output must additionally show: both raw strings, the
    shared words, the words only in A, and the words only in B.


**Run 2 - C6 (timing), forced identical.** B's timeFrame set byte-for-byte
to A's.

    [PROPOSED] Verdict:  SAME


**Run 3 - C6 (timing), one digit changed.** B's timeFrame set to
"Baseline to Week 13".

    [PROPOSED] Verdict:  REVIEW

    [PROPOSED] This one will feel wrong, and that is why it is here.
    Week 12 against Week 13 is obviously a real difference and you will
    want DIFFERENT. But the moment the tool is allowed to rule when the
    difference "looks numeric", somebody has to write down when that
    applies - and that rule is the invisible arbitrary threshold we
    refused in Run 4. REVIEW, with a diff showing 12 against 13, puts the
    answer in front of you in half a second. That is the design working,
    not failing.

    Strike out and replace if you disagree:


**Run 4 - C5 (main measurement), unrelated measurement.** B's measure set
to "Change in body weight from baseline to Week 12".

    [PROPOSED] Verdict:       REVIEW
    [PROPOSED] Must NOT be:   DIFFERENT
    [PROPOSED] Why: same reason as Run 1, at the point where being
    confident feels safest. Sleep latency against body weight is obvious
    to a human and invisible to a string comparison.


**Run 5 - N1 overreach.** N1 extended to also drop: 4 · wake · trials ·
by · dose · level. Then C5 re-run.

    [PROPOSED] Verdict becomes: SAME - because every word that
    distinguished the two strings has now been declared ignorable.

    [PROPOSED] What must be visible that tells you the rule went too far:
    THE TWO RAW STRINGS, PRINTED NEXT TO THE VERDICT. A SAME verdict
    sitting beside two visibly different sentences is the alarm. This is
    the entire reason raw strings are non-negotiable in the output - a
    normalisation rule can only be audited if you can see what it threw
    away.


---

## After the run

    Did every run return what this file said it must?   Yes 
    but here Run 5 does not have the two strings printed next to the verdict and I am unsure how the tool is going to react with interpretation of sentences that are different but with similar words.
    Which proposals did you strike out, and why: None


---

## AMENDMENT 1 - 1 Oct 2026

    The original record above is NOT edited. It is evidence of what was
    agreed on 20 Sep and what happened when it was run. This block records a
    change made after the fact, with its reason, the way a protocol amendment
    does. If you ever want to know what the spec said before today, it is
    still readable above.

### Why this amendment exists

Two things in the "After the run" block:

    1. You wrote "Yes" and then described a failure. The answer was NO.
       Run 5 did not print the raw strings next to the verdict, which this
       file required. The code was fixed on 20 Sep; the mark was never
       corrected and the run was never repeated. A "yes, but" in an
       acceptance record is how an audit trail goes soft.

    2. Your second sentence - "I am unsure how the tool is going to react
       with interpretation of sentences that are different but with similar
       words" - is the real finding, and it is a SPEC defect, not a code
       defect. The rule was obeyed exactly. The problem is that the word
       SAME, standing alone, is the same word whether N1 removed one
       connector or ten content words. Run 1's C6 and Run 5's C5 both
       printed SAME. One of those is tidying and one is erasing, and the
       output gave you no way to tell them apart without re-reading both
       sentences yourself every time.

### What changed in the code

A fifth verdict state, and a number.

    SAME        N1 removed nothing that DIFFERED between the two strings.
                Whatever it removed, it removed from both sides. The match
                does not depend on the rule at all.

    SAME (N1)   The match exists only because N1 removed words that
                differed. The output states HOW MANY, by name.

The measurement, exactly: of the words N1 removed, count the ones NOT
matched by the same word removed from the other string. Those are precisely
the words that would have shown as only-in-A or only-in-B had N1 left them
alone. A word dropped from both sides changed no verdict and is not counted.
Punctuation is reported separately and deliberately excluded from the count.

What did NOT change: the tool still has no opinion on whether an erased word
mattered. It reports the price of agreement. You pay or refuse.

### Amended verdicts - these supersede the table above

    Run 1  C5  REVIEW         unchanged
    Run 1  C6  SAME (N1), 1   was SAME. Agreement cost one word: 'to'.
    Run 2  C6  SAME           unchanged - strings identical before N1
    Run 3  C6  REVIEW         unchanged
    Run 4  C5  REVIEW         unchanged
    Run 5  C5  SAME (N1), 10  was SAME. Agreement cost ten words.

### Q3. Does the count belong in the verdict or in the body?

[PROPOSED] In the verdict.

[PROPOSED] Why: this is your own C8 argument applied a second time. On C8
you refused a bare SAME on the grounds that a verdict which answers a
different question needs its own label rather than a footnote. Same defect
here. A caveat in the body is read once, on the day it is written, by the
person who already knows. A caveat in the verdict is read every time anyone
reads any row, including a stranger six months from now who skims the
verdict column and nothing else.

    Strike out and replace if you disagree:


### Q4. 1 against 10 - is the number enough, with no threshold?

[PROPOSED] Yes. No threshold, ever.

[PROPOSED] Why: a threshold ("flag above 3 erasures") is the invisible
arbitrary cut-off this project has refused four times already - on Run 3,
on Run 4, on C4 case-folding, and on the N1 cap. The number carries the
information. The reader supplies the judgement. The moment the tool decides
that 4 is too many, somebody has to defend 4, and nobody can.

    Strike out and replace if you disagree:


### Re-run, 1 Oct 2026

    python3 check_s5.py --selftest

    Run 1  C5  REVIEW   Run 1  C6  SAME (N1)
    Run 2  C6  SAME
    Run 3  C6  REVIEW
    Run 4  C5  REVIEW
    Run 5  C5  SAME (N1)

    Does Run 5 now print both raw strings immediately above the verdict,
    with nothing between them and it?        YES

    Did every run return what the amended table says it must?  YES

    Anything you disagree with:


---

## MACHINE-WRITTEN RESULTS - S5 selftest, 5 runs - 2026-10-03 20:52:21Z

    Written by record.py from the tool's own output. NOT typed by
    hand. The verdict column is the tool's; the bracket is yours.

    Put P or F in each bracket. One mark per line, no summary mark,
    and no 'yes, but' - a line that needs a sentence to explain it
    is an F with a note underneath.

    Run 1  C5  REVIEW      [  P  ]
    Run 1  C6  SAME (N1)   [  P  ]
    Run 2  C6  SAME        [  P  ]
    Run 3  C6  REVIEW      [  P  ]
    Run 4  C5  REVIEW      [  P  ]
    Run 5  C5  SAME (N1)   [  P  ]

    Notes on any F:


<details><summary>full tool output, verbatim</summary>

```
========================================================================
RUN 1 - the real thing, both 14 Sep snapshots unedited
========================================================================
C5  MAIN MEASUREMENT                        REVIEW
    A raw     "Change From Baseline to Week 12 in Mean Sleep Latency From
              the 4 Maintenance of Wakefulness Test (MWT) Wake Trials"
    B raw     "Change in mean sleep latency (MSL) on Maintenance of
              Wakefulness Test (MWT) from baseline to Week 12 by dose level"

    protocolSection.outcomesModule.primaryOutcomes[0].measure
    N1 (5)    'to' . 'from' . 'through' . 'and' . ','
    A tidied  change baseline week 12 in mean sleep latency the 4
              maintenance of wakefulness test (mwt) wake trials
    B tidied  change in mean sleep latency (msl) on maintenance of
              wakefulness test (mwt) baseline week 12 by dose level
    shared    (mwt) . 12 . baseline . change . in . latency . maintenance .
              mean . of . sleep . test . wakefulness . week
    only A    4 . the . trials . wake
    only B    (msl) . by . dose . level . on
    ?   Words differ after N1. This tool does not rule on what free text MEANS,
        in either direction. The difference is listed above; you rule on it.

C6  MEASUREMENT TIMING                   SAME (N1)
    A raw     "Baseline, Week 12"
    B raw     "Baseline to Week 12"

    protocolSection.outcomesModule.primaryOutcomes[0].timeFrame
    N1 (5)    'to' . 'from' . 'through' . 'and' . ','
    A tidied  baseline week 12
    B tidied  baseline week 12
    shared    12 . baseline . week
    only A    (none)
    only B    (none)
    A N1 cut  (none)
    B N1 cut  to
    erased    to
    !   AGREEMENT REQUIRED ERASING 1 WORD THAT DIFFERED - listed above
        as 'erased'. The tool does NOT judge whether those words mattered; it
        cannot, and this is not the place where it starts pretending to. It
        reports the SIZE of the erasure. A small number is tidying. A large
        one is a rule doing work the evidence should be doing. Read the two
        RAW lines at the top and decide which this is.
    o   also removed 1 punctuation mark(s) unevenly. NOT counted above:
        punctuation is orthographic, and counting it would inflate a number
        that is meant to mean 'words of substance thrown away'.

========================================================================
RUN 2 - C6 forced identical - B's timeFrame set byte-for-byte to A's
========================================================================
C6  MEASUREMENT TIMING                        SAME
    A raw     "Baseline, Week 12"
    B raw     "Baseline, Week 12"

    protocolSection.outcomesModule.primaryOutcomes[0].timeFrame
    N1 (5)    'to' . 'from' . 'through' . 'and' . ','
    A tidied  baseline week 12
    B tidied  baseline week 12
    shared    12 . baseline . week
    only A    (none)
    only B    (none)
    A N1 cut  (none)
    B N1 cut  (none)
    erased    (none)
    =   The two strings were IDENTICAL BEFORE N1 was applied. N1 did not manufacture this match.

========================================================================
RUN 3 - C6 one digit changed - B set to "Baseline to Week 13"
========================================================================
C6  MEASUREMENT TIMING                      REVIEW
    A raw     "Baseline, Week 12"
    B raw     "Baseline to Week 13"

    protocolSection.outcomesModule.primaryOutcomes[0].timeFrame
    N1 (5)    'to' . 'from' . 'through' . 'and' . ','
    A tidied  baseline week 12
    B tidied  baseline week 13
    shared    baseline . week
    only A    12
    only B    13
    ?   Words differ after N1. This tool does not rule on what free text MEANS,
        in either direction. The difference is listed above; you rule on it.

========================================================================
RUN 4 - C5 unrelated measurement - B set to body weight
========================================================================
C5  MAIN MEASUREMENT                        REVIEW
    A raw     "Change From Baseline to Week 12 in Mean Sleep Latency From
              the 4 Maintenance of Wakefulness Test (MWT) Wake Trials"
    B raw     "Change in body weight from baseline to Week 12"

    protocolSection.outcomesModule.primaryOutcomes[0].measure
    N1 (5)    'to' . 'from' . 'through' . 'and' . ','
    A tidied  change baseline week 12 in mean sleep latency the 4
              maintenance of wakefulness test (mwt) wake trials
    B tidied  change in body weight baseline week 12
    shared    12 . baseline . change . in . week
    only A    (mwt) . 4 . latency . maintenance . mean . of . sleep . test .
              the . trials . wake . wakefulness
    only B    body . weight
    ?   Words differ after N1. This tool does not rule on what free text MEANS,
        in either direction. The difference is listed above; you rule on it.

========================================================================
RUN 5 - N1 OVERREACH - drop list grown from 5 to 14 entries
========================================================================
C5  MAIN MEASUREMENT                     SAME (N1)
    A raw     "Change From Baseline to Week 12 in Mean Sleep Latency From
              the 4 Maintenance of Wakefulness Test (MWT) Wake Trials"
    B raw     "Change in mean sleep latency (MSL) on Maintenance of
              Wakefulness Test (MWT) from baseline to Week 12 by dose level"

    protocolSection.outcomesModule.primaryOutcomes[0].measure
    N1 (14)   'to' . 'from' . 'through' . 'and' . ',' . 'the' . '4' . 'wake'
              . 'trials' . '(msl)' . 'on' . 'by' . 'dose' . 'level'
    A tidied  change baseline week 12 in mean sleep latency maintenance of
              wakefulness test (mwt)
    B tidied  change in mean sleep latency maintenance of wakefulness test
              (mwt) baseline week 12
    shared    (mwt) . 12 . baseline . change . in . latency . maintenance .
              mean . of . sleep . test . wakefulness . week
    only A    (none)
    only B    (none)
    A N1 cut  4 . from . from . the . to . trials . wake
    B N1 cut  (msl) . by . dose . from . level . on . to
    erased    (msl) . 4 . by . dose . from . level . on . the . trials .
              wake
    !   AGREEMENT REQUIRED ERASING 10 WORDS THAT DIFFERED - listed above
        as 'erased'. The tool does NOT judge whether those words mattered; it
        cannot, and this is not the place where it starts pretending to. It
        reports the SIZE of the erasure. A small number is tidying. A large
        one is a rule doing work the evidence should be doing. Read the two
        RAW lines at the top and decide which this is.
    o   SAME WORDS, DIFFERENT ORDER. This check compares the SET of words,
        not their sequence - word order is being treated as carrying no
        meaning. See KNOWN-LIMITATIONS.md, L3, for when that is wrong.

    ^ Read in this order: the two RAW lines, the verdict, 'erased'.
      The verdict is SAME (N1), not SAME. The parenthesis says the
      match exists ONLY because the rule removed words that differed,
      and the count says how many. Run 1's C6 above reached agreement
      by erasing 1 word. This reached it by erasing an order of
      magnitude more. The bare word SAME hid that difference; a number
      cannot. The tool still never decides whether 'by dose level'
      matters - it states the price of agreement and hands you the
      judgement, which is the only honest division of labour here.

Now mark each run against acceptance/S5-free-text.md.
Or re-run with --record and let the tool write the verdicts for you.
```

</details>
