# S3 acceptance criteria - C2, minimum age

Written by:  Purnima
Written on:  15 Sep 2026
Code written: NOT YET

This file is filled in BEFORE the check exists. That is the point. Same as
system suitability going on before the samples, and for the same reason: a
criterion written after you have seen the output is not a criterion, it is a
description.

---

## The check

C2 reads `protocolSection.eligibilityModule.minimumAge` from two trials and
returns one verdict.

Allowed verdicts (REVIEW does not apply - this is not free text):

    SAME           both records carry it, values agree
    DIFFERENT      both carry it, values do not agree
    NOT REPORTED   at least one record does not carry it

---

## Four runs. Write what the check MUST return, before it exists.

**Run 1 - the real thing.** Both 14 Sep snapshots, unedited.

    A value is:              16 Years
    B value is:              18 Years
    Verdict must be:         DIFFERENT
    And must report:         How different - the arithmetic difference between the two after converting them to comparible values.


**Run 2 - forced match.** Copy of B with minimumAge edited to "16 Years".

    Verdict must be:         SAME
    Why:                     Values are now the same after editing


**Run 3 - THE TRAP.** Copy of B with minimumAge edited to "16 Months".

    Verdict must be:         DIFFERENT
    Verdict must NOT be:     SAME
    Why:                     Must be able to convert months to years and then compare.

    Think about this one before answering. A naive way to read "16 Years" is
    to grab the number and ignore the rest. Do that, and "16 Months" also
    gives you 16.


**Run 4 - absence.** Copy of B with the minimumAge key deleted entirely.

    Verdict must be:         NOT REPORTED
    Must NOT do:             DIFFERENT


---

## One judgment call, and it is yours

Trials genuinely do state minimum ages in months - paediatric studies do it
routinely. So "16 Months" is not malformed data. It is a real, valid entry
meaning something a little over one year.

Given that, which of these should the check do, and why?

    (a) refuse anything not written in years, and report an error
    (b) convert months to years, then compare the numbers
    (c) compare only when the units already match, otherwise NOT REPORTED

    My answer:  (b) convert months to years, then compare the numbers

    Because: For sustainability and accomodating varying source information, conversion followed by comparison is better.


    What this decision costs me if I get it wrong: The comparison project's reliability is tainted if this goes wrong.

Run 1 — the output must show, for both trials, the raw string as written and what it was read as in years.
Run 3 — A must read as 16.00 years, B must read as 1.33 years.

---

## After the run

    Did every run return what this file said it must?   Yes
    Anything the four runs did not cover:
    
    AMENDMENT - 16 Sep 2026, after the run.

A fifth verdict state exists that this file did not anticipate:

    UNPARSED   the field is PRESENT but the value cannot be read
               ("N/A", a bare "16" with no unit, "16 Fortnights")

Distinct from NOT REPORTED. Absent means the sponsor said nothing.
Unparsed means the sponsor said something and we cannot read it.

Why my four runs missed it: both my trials write clean "NN Years", so
every case I could imagine came from the fixture I already had. This
state only appears when the tool is fed something neither trial contains.

Consequence: as originally written, this file would have passed a tool
that crashed on "N/A", or one that guessed 16 from a bare "16".

    --- B = 'N/A' ---
C2  MINIMUM AGE                                    UNPARSED
    protocolSection.eligibilityModule.minimumAge
    A   "16 Years"               read as 16.00 years
    B   "N/A"                    NOT READ: could not read 'N/A' as an age
    ?   A value is present but could not be read as an age. Not guessed, not compared. A human must look.

--- B = '16' ---
C2  MINIMUM AGE                                    UNPARSED
    protocolSection.eligibilityModule.minimumAge
    A   "16 Years"               read as 16.00 years
    B   "16"                     NOT READ: could not read '16' as an age
    ?   A value is present but could not be read as an age. Not guessed, not compared. A human must look.

--- B = '16 Fortnights' ---
C2  MINIMUM AGE                                    UNPARSED
    protocolSection.eligibilityModule.minimumAge
    A   "16 Years"               read as 16.00 years
    B   "16 Fortnights"          NOT READ: could not read '16 Fortnights' as an age
    ?   A value is present but could not be read as an age. Not guessed, not compared. A human must look.

--- B = '18 Days' ---
C2  MINIMUM AGE                                   DIFFERENT
    protocolSection.eligibilityModule.minimumAge
    A   "16 Years"               read as 16.00 years
    B   "18 Days"                read as 0.05 years
    >   A enrols from 15.95 years older. The two trials do not cover the same ages.
