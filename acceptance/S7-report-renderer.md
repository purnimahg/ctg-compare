# S7 acceptance criteria - the report renderer

    Written:      4 Oct 2026
    Code written: NOT YET

    Produces:  report.py  ->  report.md

    This is the first session whose output is read by SOMEONE ELSE. Everything
    before it produced evidence for you. S7 produces the artifact a stranger
    opens, and the failure mode changes accordingly: up to now a wrong number
    could reach a verdict. From here a CORRECT set of verdicts can still
    produce a wrong CONCLUSION, through ordering, omission or emphasis.

>>> Claude's proposals are marked [PROPOSED]. STRIKE OUT what you disagree
>>> with. A proposal you leave standing is YOUR criterion.
>>>
>>> You left all nine slots blank on S6 and all nine proposals were adopted
>>> unexamined. They happened to survive. Two of them should not have - Run 6
>>> and Run 1's C11 predictions both needed amending within hours. Striking
>>> nothing is a result; it is not automatically the right one.

---

## Q1. Who reads it, and how long is it?

[PROPOSED] A stranger with sixty seconds who must decide ONE thing: **can
these two trials be compared, and where can they not?**

[PROPOSED] One page of report. The seven-hundred-line evidence trail stays
where it already is - the per-check output - and the report LINKS to it by
field path, never reproduces it.

[PROPOSED] Why the constraint is a design tool and not a cosmetic one: at one
page you cannot print everything, so you have to decide what matters, and
that decision is the actual intellectual content of this session. A report
that prints all thirteen comparisons at equal weight has made no decision
and pushed the work back onto the reader.

    Strike out and replace if you disagree:


---

## Q2. What order?

[PROPOSED] **PRECONDITION FIRST.** Then Maturity. Then Comparability.

[PROPOSED] Why, and this is your own C8 argument reaching its conclusion: if
C1 and C8 say the two trials do not share a phase or a comparator structure,
then every comparability verdict below is **conditional on a comparison that
may not be meaningful**. Printing "C2 DIFFERENT" above "C1 DIFFERENT" invites
the reader to compare minimum ages between a Phase 2 and a Phase 3 trial - a
precise answer to a question that should not have been asked.

[PROPOSED] Maturity second, before Comparability, for the same reason one
level down: a reader who does not yet know that one record has posted results
and the other has not will misread every NOT REPORTED underneath.

    Strike out and replace if you disagree:


---

## Q3. Eleven checks or thirteen comparisons?

The course document says the counts must sum to 11. They no longer can. C7
split into C7a/C7b in S6 and C11 into C11a/C11b, so there are **11 checks
producing 13 comparisons**.

[PROPOSED] The report prints BOTH numbers, labelled, in the same line:
`11 checks / 13 comparisons`.

[PROPOSED] Why this is not pedantry: a report that says "11 checks" above a
table of 13 rows is printing a wrong number. It is small, it is arithmetic,
and it is exactly the kind of thing a reader notices and then distrusts the
rest of the document for. **The first number a stranger can verify by
counting is the one that decides whether they believe the others.**

[PROPOSED] And the renderer must compute both from the data, never from a
literal. A hard-coded 13 is wrong the moment C12 arrives.

    Strike out and replace if you disagree:


---

## Q4. The verdict legend - written or generated?

There are now SEVEN verdict states:

    SAME · SAME (N1) · DIFFERENT · REVIEW ·
    NOT REPORTED · NOT REPORTED (M) · UNPARSED

[PROPOSED] **GENERATED from the constants in the code.** Never typed into the
report template.

[PROPOSED] Why: a hand-written legend is the same defect class as a
hand-typed verdict, and this repo has now been bitten by that four times -
the 20 Sep "yes, but", the 3 Oct SAME/SAME (N1) transcription, the course
artifact still showing four states when there are seven, and checking a
criterion against a run title instead of the output. A legend that drifts out
of step with the code is a document that lies about the tool that produced
it.

[PROPOSED] The test, which is Run 4 below: add a verdict state to the code
and the legend must change WITHOUT anyone editing the report template.

    Strike out and replace if you disagree:


---

## Q5. What must the report REFUSE to say?

[PROPOSED] Any sentence asserting an overall conclusion. Specifically
forbidden: that the two trials ARE comparable, are NOT comparable, that one
sponsor is more or less transparent, or any scoring, grading or ranking of
either record.

[PROPOSED] What it MAY say, because these are mechanical facts and not
judgements:

    - how many comparisons fall in each verdict state
    - which preconditions hold and which do not
    - how many NOT REPORTED verdicts carry (M), and the lifecycle inputs
    - for each SAME (N1), the count of differing words erased
    - where the public record stops

[PROPOSED] The distinction, stated so a stranger can hold the tool to it:
**counting is not concluding.** "4 of 13 comparisons are NOT REPORTED, 3 of
them confounded by record maturity" is a count. "These trials are broadly
comparable" is a conclusion, and the tool has no standing to reach it.

[PROPOSED] ● And it is the harder discipline, because the conclusion is what
a reader wants and what would make the tool feel more useful. Refusing it is
the whole reason the tool is worth anything: a reader can check a count. They
cannot check a judgement, and if they could, they would not need the tool.

    Strike out and replace if you disagree:


---

## Q6. Where does the maturity banner go?

[PROPOSED] Second block, immediately under the counts, above all three
category sections. Unconditional - it prints even when it does not fire, with
the word `silent`.

[PROPOSED] Why it prints when silent: an absent banner and a silent banner
look identical to a reader, and only one of them means "this was checked".
Same reasoning as printing M1's non-membership reasons rather than omitting
them.

    Strike out and replace if you disagree:


---

## Runs

**Run 1 - render the real fixture.** Both 14 Sep snapshots.

    [PROPOSED] report.md is produced, one page, with these counts:

        11 checks / 13 comparisons
        SAME               3     C1, C3, C4, C8
        SAME (N1)          1     C6
        DIFFERENT          3     C2, C7a, C7b
        REVIEW             1     C5
        NOT REPORTED       1     C10
        NOT REPORTED (M)   3     C9, C11a, C11b
        UNPARSED           0
                          --
                          13

    [PROPOSED] Counts written out BY HAND above, from the S3-S6 acceptance
    records, before report.py exists. If the renderer disagrees with this
    block, one of them is wrong and the paper gets checked first - that is
    what caught L6.

    [PROPOSED] Preconditions section must report C1 SAME and C8 SAME, and
    must carry C8's structural note: the SAME describes shared architecture,
    not shared drugs.

**Run 2 - the arithmetic.**

    [PROPOSED] Every one of the 13 comparisons appears EXACTLY ONCE across the
    three category sections. The category counts sum to 13. Both assertions
    enforced in code, not checked by eye.
    [PROPOSED] Why in code: counting thirteen rows by eye across three
    sections is a transcription task, and this repo's record on transcription
    tasks is four for four against.

**Run 3 - precondition failure.** B's `designModule.phases` set to
`["PHASE2"]`.

    [PROPOSED] C1 becomes DIFFERENT. The report must LEAD with the
    precondition failure and state explicitly that the comparability section
    below is conditional on a comparison that may not be meaningful.
    [PROPOSED] It must NOT suppress the comparability section, and must NOT
    rank or score the result. Flag the condition; print the evidence.

**Run 4 - legend drift.** A new verdict constant added to the code and
returned by one check.

    [PROPOSED] The new state appears in the legend and in the counts with NO
    edit to the report template.
    [PROPOSED] Must NOT be: silently dropped from the legend, or silently
    excluded from the total so the counts still sum to 13.
    [PROPOSED] ● The second failure is the dangerous one - a total that still
    adds up is a total nobody questions.

**Run 5 - the refusal test.** Scan the rendered report for forbidden
sentences.

    [PROPOSED] The report contains no assertion of overall comparability, no
    transparency comparison between sponsors, and no score or grade. Checked
    mechanically against a published list of forbidden phrasings, and the
    list is printed in the README so a stranger can audit the refusal rather
    than take it on trust.

**Run 6 - the empty report.** The renderer handed zero check results.

    [PROPOSED] It FAILS LOUDLY and writes nothing.
    [PROPOSED] Must NOT be: a clean, well-formatted report with an empty
    table and counts of zero.
    [PROPOSED] ● This is the project's own failure shape arriving at the
    report layer. A report that renders perfectly and says nothing is the
    most plausible-looking wrong answer the tool could produce - no error, no
    warning, correct formatting, and a reader who concludes the two trials
    had nothing to compare. Same family as `Same 0 value(s)` in L5 and
    `absent from both` in L6, one level up.

---

## After the run

    python3 report.py --selftest --record

Then mark P or F in each bracket of the machine-written block it appends.
One mark per line. No summary mark. A line needing a sentence is an F with
the sentence underneath.

**Check the evidence line, not the run title.** On S6 a criterion was
confirmed against the words "THE EMPTY-LIST TRAP" - the heading - rather than
against `PRESENT BUT EMPTY in A, B`, the line the code produced. The heading
would have read the same if the verdict had been wrong. A pass criterion
satisfiable by the test's own title verifies nothing.


---

## AMENDMENT 1 - 4 Oct 2026. The Run 1 count block was wrong. Claude wrote it.

Appended, not edited. The original block above stands as written, because it
is the evidence.

### The error

    SAME               3     C1, C3, C4, C8      <- a count of 3 against
                                                    FOUR listed checks
    ...
                      --
                      13                         <- the column sums to 12

Two wrong numbers in nine lines: `SAME` should be 4, and the printed total of
13 does not match the sum of its own column.

### Corrected, from the acceptance records rather than from memory

Every value below is read out of a P-marked acceptance record, not recomputed:

    SAME               4     C1, C3, C4, C8    S4 record line 46-47, S6 block
    SAME (N1)          1     C6                S5 machine block
    DIFFERENT          3     C2, C7a, C7b      S3 record, S6 block
    REVIEW             1     C5                S5 machine block
    NOT REPORTED       1     C10               S6 block
    NOT REPORTED (M)   3     C9, C11a, C11b    S6 block
    UNPARSED           0
                      --
                      13    = 11 checks (C3 appears in both S4 and S6
                                          and is counted ONCE)

Category split, which must also sum to 13:

    PRECONDITION    2    C1, C8
    MATURITY        4    C9, C10, C11a, C11b
    COMPARABILITY   7    C2, C3, C4, C5, C6, C7a, C7b
                   --
                   13

### Why this one matters more than its size

● The total was RIGHT. The component was wrong. **A total that still adds up
is a total nobody questions** - which is written, in those words, in Run 4
of this same file, about forty lines below a column that does not add up.
Writing the rule did not stop me breaking it one screen earlier.

● It was wrong in the block whose entire stated purpose is to be the
independent paper reference that catches the code - the mechanism that found
L6. A corrupted reference standard does not announce itself; it silently
certifies whatever the code returns. If `report.py` had come back with
`SAME 3`, this block would have passed it.

● And it survived a read. ○ *"I've read the S7-report-renderer.md and
saved."* All six strike-out slots blank, the arithmetic uncaught. ● That is
not a reprimand - four listed items against the numeral 3 is genuinely hard
to see, which is the whole point. **It is the fifth instance in this build of
the same failure: reading a document and checking the label rather than the
arithmetic.** The lesson is not "look harder". It is that any number a human
is expected to verify by eye needs the machine to verify it too.

### Consequence for the code - a new criterion

    [PROPOSED] report.py ASSERTS its own arithmetic at render time:
    every comparison appears exactly once, the verdict counts sum to the
    total, and the category counts sum to the same total. On any mismatch it
    FAILS LOUDLY and writes nothing.

    [PROPOSED] This is now the only defence that works. Run 2 already
    required it of the renderer. This amendment records WHY: the human
    reference standard was corrupted on first writing, by the person who
    wrote the rule about it, and it took a third party - the arithmetic
    itself - to catch.

    Strike out and replace if you disagree:


    Did report.py's counts match the corrected block above?  Yes


---

## MACHINE-WRITTEN RESULTS - S7 selftest, 6 runs - 2026-10-04 21:01:27Z

    Written by record.py from the tool's own output. NOT typed by
    hand. The verdict column is the tool's; the bracket is yours.

    Put P or F in each bracket. One mark per line, no summary mark,
    and no 'yes, but' - a line that needs a sentence to explain it
    is an F with a note underneath.

    Run 1  counts  SAME=4 total=13              [  P  ]
    Run 2  arith  refused duplicate            [  P  ]
    Run 3  precond  warned, not suppressed       [  P  ]
    Run 4  legend  refused unknown verdict      [  P  ]
    Run 5  refusal  clean                        [  P  ]
    Run 5  refusal-guard  refused planted conclusion   [  P  ]
    Run 6  empty  refused empty                [  P  ]

    Notes on any F:


<details><summary>full tool output, verbatim</summary>

```
========================================================================
RUN 1 - render the real fixture
========================================================================
    11 checks / 13 comparisons
    SAME               4
    SAME (N1)          1
    DIFFERENT          3
    REVIEW             1
    NOT REPORTED       1
    NOT REPORTED (M)   3
    UNPARSED           0
                       --
                       13
    PRECONDITION       2
    MATURITY           4
    COMPARABILITY      7

    report.md written, 124 lines
    Compare the block above to AMENDMENT 1 in the acceptance file.

========================================================================
RUN 2 - the arithmetic guard - a duplicated comparison
========================================================================
    refused: Comparison(s) appear more than once: ['C1']

========================================================================
RUN 3 - precondition failure - B phases set to ["PHASE2"]
========================================================================
    C1 verdict: DIFFERENT
    comparability section carries the conditional warning: True
    comparability rows still printed: 7

========================================================================
RUN 4 - legend drift - a check returns a verdict the legend lacks
========================================================================
    refused: Verdict(s) ['PROBABLY FINE'] emitted but absent from the generated legend. They would be printed without explanation, or...

========================================================================
RUN 5 - the refusal test
========================================================================
    rendered report contains none of the 19 forbidden phrasings
    and the guard itself works:
    refused a planted sentence asserting comparability

========================================================================
RUN 6 - the empty report - renderer handed zero results
========================================================================
    refused: Zero comparisons. A report that renders cleanly with an empty table and counts of zero is the most plausible-looking wrong answer this tool could prod...

Mark each line against acceptance/S7-report-renderer.md.
```

</details>
