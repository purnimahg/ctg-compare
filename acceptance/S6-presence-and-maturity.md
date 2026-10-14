# S6 acceptance criteria - presence, documents, and the maturity guard

    Written:      3 Oct 2026
    Code written: NOT YET

    Checks in this session:

      C3   maximum age          protocolSection.eligibilityModule.maximumAge
      C7a  masking level        protocolSection.designModule.designInfo
                                  .maskingInfo.masking
      C7b  who was masked       ...maskingInfo.whoMasked                  [list]
      C9   results posted       protocolSection.statusModule
                                  .resultsFirstPostDateStruct.date
      C10  method described     protocolSection.outcomesModule
                                  .primaryOutcomes[0].description
      C11a document labels      documentSection.largeDocumentModule
                                  .largeDocs[].label                      [list]
      C11b document dates       documentSection.largeDocumentModule
                                  .largeDocs[].date                       [list]

      guard  hasResults                        <- TOP LEVEL of the record
             protocolSection.statusModule.overallStatus

    TWO NOTATION TRAPS, both one character from being wrong, both the same
    family as the [0]/[] lesson from S2:

      1. C11 lives under documentSection, NOT protocolSection. Every other
         check in this repo starts protocolSection. This one does not.
      2. hasResults is at the TOP LEVEL - record["hasResults"] - not inside
         protocolSection. Writing protocolSection.hasResults returns None
         silently and the guard never fires. Nothing errors.

>>> Claude's proposals are below, marked [PROPOSED]. STRIKE OUT what you
>>> disagree with and write your own. A proposal you leave standing is YOUR
>>> criterion. Reviewing is not weaker than authoring.

---

## Known answers, read off the 14 Sep snapshots BEFORE any code runs

                              A · NCT06470828        B · NCT07455383
    C3   maximum age          70 Years               70 Years
    C7a  masking              DOUBLE                 TRIPLE
    C7b  whoMasked            PARTICIPANT,           PARTICIPANT,
                              INVESTIGATOR           CARE_PROVIDER,
                                                     INVESTIGATOR
    C9   results posted       2026-08-31             absent
    C10  description          683 chars              absent
    C11a document labels      Study Protocol,        absent
                              Statistical Analysis
                              Plan
    C11b document dates       2024-10-23,            absent
                              2025-05-26
    hasResults                true                   false
    overallStatus             COMPLETED              RECRUITING

Controlled vocabularies, case NOT folded, same discipline as S4:

    MASKING    NONE · SINGLE · DOUBLE · TRIPLE · QUADRUPLE
    WHO_MASKED PARTICIPANT · CARE_PROVIDER · INVESTIGATOR ·
               OUTCOMES_ASSESSOR

---

## Q1. The maturity guard: does it change the verdict, or annotate it?

[PROPOSED] BOTH, and they say different things. Two separate mechanisms, not
one.

    1. A REPORT-LEVEL BANNER, unconditional and purely factual. It states
       each record's hasResults, overallStatus and results-posting date, and
       nothing else. It makes no claim about why any field is missing. It
       fires whenever the two records disagree on hasResults.

    2. A PER-VERDICT TAG, (M), applied ONLY to fields on a published list
       called M1 - see Q2.

[PROPOSED] Why both: the banner is a fact about the two records and belongs
once, at the top, where nobody can miss it. The tag is a claim about a
specific absence, and a claim needs to be earned field by field. Collapsing
them means either shouting the confounder on every row, or burying it.

[PROPOSED] And the tag means CONFOUNDED, not EXCUSED. (M) says "this absence
has a second possible explanation." It does not say "this absence is fine."

    Strike out and replace if you disagree:


---

## Q2. M1 - which fields may carry the (M) tag?

[PROPOSED] ONLY fields that CANNOT logically exist before results are
posted. On this fixture that is exactly one:

    M1 = [ protocolSection.statusModule.resultsFirstPostDateStruct.date ]

[PROPOSED] And - this is the part that matters more than the list - the tool
PRINTS ITS NON-MEMBERSHIP REASONING for the near misses:

    C10  description      NOT in M1. This field is available at
                          registration. Many sponsors fill it only when
                          posting results, but they are not required to
                          wait. Its absence is therefore NOT explained by
                          record maturity, and the tool will not say it is.

[PROPOSED] Why so short a list: the same reason N1 is capped at five. A
generous M1 excuses absences, and excusing absences is the single most
destructive thing this tool could do - it is the difference between "B has
not disclosed this" and "B has not disclosed this YET", and only one of
those two sentences is supported by a registry field.

[PROPOSED] The principle, stated so a stranger can hold the tool to it:
THE ONLY ABSENCE THIS TOOL WILL EXCUSE ON MATURITY GROUNDS IS ONE THAT IS
LOGICALLY IMPOSSIBLE OTHERWISE.

    Strike out and replace if you disagree:


---

## Q3. C11 documents - in M1 or not? THIS ONE IS UNVERIFIED AND IS YOURS.

The question: **does ClinicalTrials.gov permit a sponsor to post a protocol
or SAP document BEFORE posting results?**

    If YES  - B's absent documents are a disclosure choice. Not in M1.
    If NO   - B could not have posted them. In M1.

I do not know the answer and will not guess it into the spec. It decides
whether the report's reader is entitled to think less of Alkermes.

**Go read, then tell me:** ClinicalTrials.gov's own submission documentation
and the FDAAA 801 / Final Rule requirements. Search terms:
`ClinicalTrials.gov submit study documents protocol SAP`,
`FDAAA 801 final rule statistical analysis plan submission results`,
`42 CFR 11.48 document submission`. Primary source, not a summary.

Answer: C11 is in M1.

[PROPOSED] Until you have verified it, C11 is NOT in M1, and the tool prints
the undecided state explicitly rather than picking a side:

    C11a/C11b  NOT REPORTED
      A posted 2 documents (2024-10-23, 2025-05-26). B posted none.
      B has not posted results. Whether the registry permits document
      posting before results determines whether this is a disclosure
      difference or a timing artefact. UNVERIFIED - see M1 notes.

[PROPOSED] Why this is the right placeholder rather than a coin flip: it is
the one output that cannot mislead in either direction, and it names the
single fact that would resolve it. That sentence - marking exactly where the
public record stops and what you would have to know to go further - is the
thing this whole repo exists to demonstrate.

    HER ANSWER, 3 Oct 2026, from primary sources:

      42 CFR 11.48 is titled "What constitutes clinical trial RESULTS
      information?" and 11.48(a) binds only for trials "for which clinical
      trial results information must be submitted under 11.42".
      11.48(a)(5) places the protocol and SAP inside that list. The
      ClinicalTrials.gov guidance adds: "The protocol and, if separate, the
      SAP are to be posted WITH OTHER CLINICAL TRIAL RESULTS, in accordance
      with 42 CFR 11.52." (81 FR 65002)

      => Documents are a RESULTS-information element, not a registration
         element. The regulatory pathway by which a document reaches the
         registry IS the results submission. A record with no results has
         no route by which documents would appear.

      => C11 goes INTO M1.

    RESIDUAL, stated rather than hidden: the text establishes what is
    REQUIRED and WHEN POSTED. It does not say voluntary earlier upload is
    FORBIDDEN. "B could not have posted them" is one step past the source.
    The claim the tool will make is the narrower one above. UNVERIFIED
    whether a pre-results voluntary pathway exists; if it does, it is rare
    enough that absence is uninformative either way.

    Strike out and replace if you disagree:

C11 is in M1.

---

## Q4. C7 - one check or two? And is whoMasked a set or a sequence?

[PROPOSED] TWO checks, C7a and C7b, reported independently.
[PROPOSED] whoMasked compared as a MULTISET, order-insensitive - the C8
precedent, and for the same reason: the displayed diff is a set operation.

[PROPOSED] Why two and not one: masking level and masked parties can
DISAGREE, and a single merged verdict would hide it. Run 7 constructs that
case on purpose.

    Strike out and replace if you disagree:


---

## Q5. An empty list - `armGroups: []` - what verdict?

[PROPOSED] NOT REPORTED, with the reason printed as "field present but
empty". Never SAME. Never a crash.

[PROPOSED] Why this is the dangerous one, and why it gets its own run:
**two empty lists compare as equal multisets.** `[] == []` is True. A C8
implementation that is correct for every real input returns SAME for two
trials that have declared no arms at all - a confident agreement about
nothing, produced by code with no bug in it. This is the exact failure this
project exists to catch, and it is one line of guard.

[PROPOSED] Not UNPARSED: the field is present and perfectly readable. It
says zero. Zero values is not noise, it is nothing to compare.

    Strike out and replace if you disagree:


---

## Q6. C12 internal consistency - build it now, or log it?

The check: does `masking` agree with the LENGTH of `whoMasked`? DOUBLE with
two parties is consistent. DOUBLE with three parties is a record that
contradicts itself, and no between-record comparison would ever notice.

[PROPOSED] LOG IT as C12, scope v0.2. Do not build it in S6.

[PROPOSED] Why log rather than build: 12 days to ship, and this is a new
CATEGORY of check - record-against-itself rather than record-against-record.
It needs its own acceptance thinking, not a bolt-on. It is also, on its
merits, one of the more interesting things in the backlog: "which numbers in
this readout deserve belief" is answered partly by whether a record is
self-consistent, and no existing comparability tool asks.

    Strike out and replace if you disagree:


---

## Runs

Each run varies ONE parameter. Where a parameter is logically coupled to a
second field, both move together and the coupling is stated - pretending
otherwise would be the real DoE violation.

**Run 1 - the real thing.** Both 14 Sep snapshots, unedited.

    [PROPOSED] C3    SAME              70.00 vs 70.00 years, both shown
    [PROPOSED] C7a   DIFFERENT         DOUBLE vs TRIPLE
    [PROPOSED] C7b   DIFFERENT         only in B: CARE_PROVIDER
    [PROPOSED] C9    NOT REPORTED (M)  absent from B; in M1
    [PROPOSED] C10   NOT REPORTED      NOT tagged (M), with the reason printed
    [PROPOSED] C11a  NOT REPORTED      undecided block from Q3
    [PROPOSED] C11b  NOT REPORTED      undecided block from Q3
    [PROPOSED] banner FIRES            hasResults true vs false

    [PROPOSED] C3 must additionally show the PARSED YEARS for both, not just
    the raw strings - the S3 lesson. A converter that multiplied instead of
    dividing would print SAME here and pass unnoticed, because both values
    are identical.

**Run 2 - C3 unit trap.** B's maximumAge set to `"840 Months"`.

    [PROPOSED] Verdict: SAME, with 70.00 and 70.00 both displayed.
    [PROPOSED] Why it is here: C3 was specified in S4 and never actually
    exercised. This is also the proof that `to_years` is imported from
    check_c2.py rather than reimplemented - if C3 has its own copy of the
    conversion, this run is where they drift apart.

**Run 3 - C3 absent.** B's maximumAge deleted.

    [PROPOSED] Verdict: NOT REPORTED, and NOT tagged (M) - maximumAge is
    available at registration.

**Run 4 - C1 absent.** A's `designModule.phases` deleted.

    [PROPOSED] Verdict: NOT REPORTED. Never SAME. Closes the S4 gap: the
    exact-match family was never tested against a missing field.

**Run 5 - the empty-list trap.** BOTH records' `armGroups` set to `[]`.

    [PROPOSED] Verdict: NOT REPORTED, reason "field present but empty".
    [PROPOSED] Must NOT be: SAME. Must not crash.
    [PROPOSED] Symmetric on purpose - one empty list is easy, two is the
    case where naive code agrees with itself. See Q5.

**Run 6 - the guard switched off.** B's `hasResults` set to true AND
`resultsFirstPostDateStruct.date` set to `"2026-09-01"`. Coupled: a record
cannot have results posted without a posting date.

    [PROPOSED] banner  SILENT         both records now have results
    [PROPOSED] C9      DIFFERENT      2026-08-31 vs 2026-09-01
    [PROPOSED] C10     NOT REPORTED   and now with NO maturity escape at
                                      all - B has posted results and still
                                      describes no method. The absence has
                                      become a disclosure fact.
    [PROPOSED] Why this run matters most: it is the only one that proves the
    guard can turn OFF. A guard that always fires is indistinguishable from
    a guard that is hard-coded, and it would quietly excuse every absence in
    every future comparison.

**Run 7 - C7 made internally inconsistent.** A's `masking` set to
`"TRIPLE"`, whoMasked left at its real two entries.

    [PROPOSED] C7a   SAME        TRIPLE vs TRIPLE
    [PROPOSED] C7b   DIFFERENT   only in B: CARE_PROVIDER
    [PROPOSED] Neither sub-check notices that A now claims TRIPLE masking
    while naming two masked parties. That blind spot is the point of the
    run, and it is the argument for C12 in Q6. A merged C7 would have
    printed one verdict here and hidden both halves.

---

## After the run

Run it with the recorder so you type no verdicts:

    python3 check_s6.py --selftest --record

Then mark P or F in each bracket of the machine-written block it appends.
One mark per line. No summary mark. A line needing a sentence is an F with
the sentence underneath.


---

## AMENDMENT 1 - 3 Oct 2026. Consequences of Q3.

Appended, not edited. Q1, Q2 and Run 1 above said M1 held one field. Her
reading of 42 CFR 11.48 changed that, and changed two other things with it.

### 1. M1 gains C11

    M1 = [ protocolSection.statusModule.resultsFirstPostDateStruct.date,
           documentSection.largeDocumentModule.largeDocs[].label,
           documentSection.largeDocumentModule.largeDocs[].date ]

C10 stays OUT, unchanged. The description field is a registration-time
element; nothing in 11.48 makes it results-bound. That distinction survives
contact with the source, which is the first time a proposal in this repo
has been tested against a regulation rather than against a fixture.

### 2. The guard keys on the WRONG FIELD. Corrected.

As specified, the guard fires on `hasResults` disagreeing. That is not the
question. 11.48 creates a results obligation triggered by the PRIMARY
COMPLETION DATE; `hasResults: false` means something completely different
depending on where that date sits.

    A  primaryCompletionDate  2025-06-03  ACTUAL     obligation live;
                                                     results posted
                                                     2026-08-31, documents
                                                     uploaded 2026-06-02
    B  primaryCompletionDate  2027-05     ESTIMATED  the clock has NOT
                                                     STARTED

So B's missing documents are not "has not got round to it". There is no
obligation yet and no pathway yet. A trial that completed two years ago and
posted nothing is a different animal entirely, and `hasResults: false` is
the same two words for both.

    [PROPOSED] The guard reads primaryCompletionDateStruct.date AND .type,
    and the banner states both records' dates and types. The (M) tag is
    earned when a record's primary completion date has not passed, or has
    passed too recently for the submission deadline to have run.

    [PROPOSED] It does NOT compute the deadline. That is a legal
    determination with exceptions (extensions, certifications, delayed
    posting). The tool prints the date, the type, and today's date, and
    stops. Same refusal as everywhere else.

    Strike out and replace if you disagree:


### 3. The third cause of absence - closed by fields already mapped

Q3 offered two branches: disclosure choice, or timing artefact. 11.48(a)
supplies a third it did not consider - the obligation binds only on
"applicable clinical trials", and a trial that is not an ACT owes nothing.
Absence then means neither opacity nor timing.

On this fixture that branch CLOSES, from the record:

    A  isFdaRegulatedDrug true   15 US sites of 53, 11 countries
    B  isFdaRegulatedDrug true   22 US sites of 42,  9 countries

    [PROPOSED] The guard prints oversightModule.isFdaRegulatedDrug and the
    US site count for each record, so the reader can see the third branch
    was checked rather than overlooked. Not a new C-number - part of the
    guard. The eleven checks stay eleven.

    [PROPOSED] It states the inputs, not the conclusion. "Applicable
    clinical trial" is a defined legal term with more conditions than two
    fields. The tool shows what bears on it and does not rule.

    Strike out and replace if you disagree:


### 4. New caveat - `hasSap: true` does not mean the SAP is readable

11.48(a)(5) expressly permits the responsible party to redact trade secret
and confidential commercial information before submission.

So the field attests EXISTENCE, not COMPLETENESS. "Takeda disclosed their
statistical analysis plan" is not supported by `hasSap: true`. What is
supported is "a document labelled Statistical Analysis Plan, dated
2025-05-26, 1.46 MB, was posted on 2026-06-02." Whether the model inside it
is legible is a question only someone who opens it can answer.

    [PROPOSED] C11 prints the redaction caveat whenever it reports a
    document as present. Logged as L4 in KNOWN-LIMITATIONS.md.

    Strike out and replace if you disagree:


### Amended Run 1 verdicts - these supersede Run 1 above

    C11a  NOT REPORTED (M)   was NOT REPORTED. Now in M1.
    C11b  NOT REPORTED (M)   was NOT REPORTED. Now in M1.
    banner FIRES, and states primary completion dates with their types,
           isFdaRegulatedDrug, and US site counts - not just hasResults.

Everything else in Run 1 is unchanged.


---

## AMENDMENT 2 - 3 Oct 2026. Run 6 as specified was wrong. Twice over.

Appended, not edited. Written while building the code, before the acceptance
run was marked.

### What happened

Run 6 exists to prove the maturity guard can turn OFF. As specified above it
moved TWO fields on record B:

    hasResults                 -> true
    resultsFirstPostDate       -> 2026-09-01

and left `primaryCompletionDate` at **2027-05, ESTIMATED**. That produces a
record that **cannot exist**: results posted in September 2026 for a trial
that does not reach primary completion until May 2027.

The guard refused it. C11a came back **NOT REPORTED (M)** - still excused on
maturity grounds - which is the exact opposite of what the run exists to
demonstrate.

### Why the code was right and the criteria were wrong

The guard is keyed on the primary completion date, because that is what
42 CFR 11.48 keys the obligation on. It was handed a record whose completion
date had not passed, so it reported that no obligation had been triggered.
Correct, on the inputs it was given.

**The defect was in the run's design.** Its own note said coupled factors must
move together - and then got the coupling wrong. The coupling is THREE fields,
not two: a record cannot post results before reaching primary completion.

### Two changes

1. **Run 6 now moves three fields:** `hasResults`,
   `primaryCompletionDateStruct` (-> 2026-04-30, ACTUAL) and
   `resultsFirstPostDateStruct`. Stated in the run header as three.

2. **`m_verdict` now tests "has this record posted results?" BEFORE it looks
   at any date**, because that supersedes the date entirely. A record that has
   posted results had the submission pathway available; if an M1 field is
   still absent, maturity explains nothing. This is the strongest
   no-excuse case there is and it was previously unreachable in the code.

### Amended Run 6 verdicts

    banner  SILENT            both records now have results
    C9      DIFFERENT         2026-08-31 vs 2026-09-01
    C10     NOT REPORTED      never in M1; unchanged
    C11a    NOT REPORTED      (M) TAG GONE - B posted results, pathway
                              existed, documents still absent

### What this is worth, beyond Run 6

● A guard that can only be proven to fire is not a guard. This is the second
time in two sessions that the valuable run was the one trying to switch
something OFF - and the first time the tool rejected a test fixture for being
physically impossible. The run was written to test the code. The code tested
the run back.

    Did the amended Run 6 return what this block says it must?  Yes


---

## MACHINE-WRITTEN RESULTS - S6 selftest, 7 runs - 2026-10-03 22:37:39Z

    Written by record.py from the tool's own output. NOT typed by
    hand. The verdict column is the tool's; the bracket is yours.

    Put P or F in each bracket. One mark per line, no summary mark,
    and no 'yes, but' - a line that needs a sentence to explain it
    is an F with a note underneath.

    Run 1  C3  SAME               [  P  ]
    Run 1  C7a  DIFFERENT          [  P  ]
    Run 1  C7b  DIFFERENT          [  P  ]
    Run 1  C9  NOT REPORTED (M)   [  P  ]
    Run 1  C10  NOT REPORTED       [  P  ]
    Run 1  C11a  NOT REPORTED (M)   [  P  ]
    Run 1  C11b  NOT REPORTED (M)   [  P  ]
    Run 2  C3  SAME               [  P  ]
    Run 3  C3  NOT REPORTED       [  P  ]
    Run 4  C1  NOT REPORTED       [  P  ]
    Run 5  C8  NOT REPORTED       [  P  ]
    Run 6  C9  DIFFERENT          [  P  ]
    Run 6  C10  NOT REPORTED       [ P  ]
    Run 6  C11a  NOT REPORTED       [  P  ]
    Run 7  C7a  SAME               [  P  ]
    Run 7  C7b  DIFFERENT          [  P  ]

    Notes on any F: Nil


<details><summary>full tool output, verbatim</summary>

```
========================================================================
RUN 1 - the real thing, both 14 Sep snapshots unedited
========================================================================
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
MATURITY GUARD - FIRED   (today: 2026-10-03)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  The two records are at DIFFERENT LIFECYCLE STAGES. Every NOT
  REPORTED below may reflect that rather than sponsor disclosure
  practice. This banner states facts about the records and makes
  no claim about the cause of any absence.

                        A                           B                           
  hasResults            True                        False                       
  overallStatus         COMPLETED                   RECRUITING                  
  primary completion    2025-06-03                  2027-05                     
    ...date type        ACTUAL                      ESTIMATED                   
    ...passed?          True                        False                       
    ...days elapsed     487                         -240                        
  results posted        2026-08-31                  None                        
  isFdaRegulatedDrug    True                        True                        
  US sites / total      15 / 53                     22 / 42                     

  The third cause of absence, checked rather than overlooked: the
  11.48 obligation binds only on an 'applicable clinical trial'. A
  trial that is not one owes nothing, and absence would mean neither
  opacity nor timing. isFdaRegulatedDrug and US site counts are
  printed above because they bear on it. 'Applicable clinical trial'
  is a defined legal term with more conditions than two fields, so
  this tool states the inputs and does not rule.

  M1 (maturity-dependent fields, 3):
    documentSection.largeDocumentModule.largeDocs[].date
    documentSection.largeDocumentModule.largeDocs[].label
    protocolSection.statusModule.resultsFirstPostDateStruct.date

C3  MAXIMUM AGE                               SAME
    protocolSection.eligibilityModule.maximumAge
    A   "70 Years"             read as 70.00 years
    B   "70 Years"             read as 70.00 years
    =   Both read as 70.00 years.

C7a  MASKING LEVEL                        DIFFERENT
    protocolSection.designModule.designInfo.maskingInfo.masking
    A   "DOUBLE"
    B   "TRIPLE"
    >   A is 'DOUBLE', B is 'TRIPLE'.

C7b  WHO WAS MASKED                       DIFFERENT
    protocolSection.designModule.designInfo.maskingInfo.whoMasked
    A   [2] PARTICIPANT, INVESTIGATOR
    B   [3] PARTICIPANT, CARE_PROVIDER, INVESTIGATOR
    >   counts A=2  B=3
        in B but not A: CARE_PROVIDER x1

C9  RESULTS POSTED                NOT REPORTED (M)
    protocolSection.statusModule.resultsFirstPostDateStruct.date
    A   "2026-08-31"
    B   -- field absent --
    o   absent from B. Absent is not equal.
    o   in M1 - this field cannot exist before results are posted.
        B: primary completion 2027-05 (ESTIMATED) has NOT passed. No results
            obligation triggered as of 2026-10-03. Absence has no other available cause.
    M   TAGGED (M). This means CONFOUNDED, not EXCUSED - the absence has a
        second available explanation. It does not mean the absence is fine.

C10  METHOD DESCRIBED                  NOT REPORTED
    protocolSection.outcomesModule.primaryOutcomes[0].description
    A   683 chars
    B   -- field absent --
    o   absent from B. Absent is not equal.
    o   NOT tagged (M). This field is not in M1:
        `description` is available at REGISTRATION. Many sponsors fill it only when posting
        results, but nothing requires them to wait. Its absence is therefore NOT
        explained by record maturity, and this tool will not say it is.
    .   PRESENCE ONLY. This check does not adjudicate what the text MEANS - that is
        C5/C6's machinery and rule N1. Both present and non-identical returns REVIEW.

C11a  DOCUMENT LABELS               NOT REPORTED (M)
    documentSection.largeDocumentModule.largeDocs[].label
    A   [2] Study Protocol, Statistical Analysis Plan
    B   -- field absent --
    o   absent from B. Absent is not equal.
    o   in M1 - this field cannot exist before results are posted.
        B: primary completion 2027-05 (ESTIMATED) has NOT passed. No results
            obligation triggered as of 2026-10-03. Absence has no other available cause.
    M   TAGGED (M). This means CONFOUNDED, not EXCUSED - the absence has a
        second available explanation. It does not mean the absence is fine.
    .   A document-presence field attests EXISTENCE, not COMPLETENESS. 42 CFR 11.48(a)(5)
        permits redacting trade secret and confidential commercial information before
        submission, so `hasSap: true` does not mean the statistical model is legible.
        See KNOWN-LIMITATIONS.md, L4.

C11b  DOCUMENT DATES                NOT REPORTED (M)
    documentSection.largeDocumentModule.largeDocs[].date
    A   [2] 2024-10-23, 2025-05-26
    B   -- field absent --
    o   absent from B. Absent is not equal.
    o   in M1 - this field cannot exist before results are posted.
        B: primary completion 2027-05 (ESTIMATED) has NOT passed. No results
            obligation triggered as of 2026-10-03. Absence has no other available cause.
    M   TAGGED (M). This means CONFOUNDED, not EXCUSED - the absence has a
        second available explanation. It does not mean the absence is fine.
    .   A document-presence field attests EXISTENCE, not COMPLETENESS. 42 CFR 11.48(a)(5)
        permits redacting trade secret and confidential commercial information before
        submission, so `hasSap: true` does not mean the statistical model is legible.
        See KNOWN-LIMITATIONS.md, L4.

========================================================================
RUN 2 - C3 unit trap - B maximumAge set to "840 Months" (= 70 years)
========================================================================
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
MATURITY GUARD - FIRED   (today: 2026-10-03)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  The two records are at DIFFERENT LIFECYCLE STAGES. Every NOT
  REPORTED below may reflect that rather than sponsor disclosure
  practice. This banner states facts about the records and makes
  no claim about the cause of any absence.

                        A                           B                           
  hasResults            True                        False                       
  overallStatus         COMPLETED                   RECRUITING                  
  primary completion    2025-06-03                  2027-05                     
    ...date type        ACTUAL                      ESTIMATED                   
    ...passed?          True                        False                       
    ...days elapsed     487                         -240                        
  results posted        2026-08-31                  None                        
  isFdaRegulatedDrug    True                        True                        
  US sites / total      15 / 53                     22 / 42                     

  The third cause of absence, checked rather than overlooked: the
  11.48 obligation binds only on an 'applicable clinical trial'. A
  trial that is not one owes nothing, and absence would mean neither
  opacity nor timing. isFdaRegulatedDrug and US site counts are
  printed above because they bear on it. 'Applicable clinical trial'
  is a defined legal term with more conditions than two fields, so
  this tool states the inputs and does not rule.

  M1 (maturity-dependent fields, 3):
    documentSection.largeDocumentModule.largeDocs[].date
    documentSection.largeDocumentModule.largeDocs[].label
    protocolSection.statusModule.resultsFirstPostDateStruct.date

C3  MAXIMUM AGE                               SAME
    protocolSection.eligibilityModule.maximumAge
    A   "70 Years"             read as 70.00 years
    B   "840 Months"           read as 70.00 years
    =   Both read as 70.00 years.

    ^ SAME here also proves to_years is IMPORTED from check_c2.py
      rather than reimplemented. If C3 had its own copy of the
      conversion, this is the run where the two would drift.

========================================================================
RUN 3 - C3 absent - B maximumAge deleted
========================================================================
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
MATURITY GUARD - FIRED   (today: 2026-10-03)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  The two records are at DIFFERENT LIFECYCLE STAGES. Every NOT
  REPORTED below may reflect that rather than sponsor disclosure
  practice. This banner states facts about the records and makes
  no claim about the cause of any absence.

                        A                           B                           
  hasResults            True                        False                       
  overallStatus         COMPLETED                   RECRUITING                  
  primary completion    2025-06-03                  2027-05                     
    ...date type        ACTUAL                      ESTIMATED                   
    ...passed?          True                        False                       
    ...days elapsed     487                         -240                        
  results posted        2026-08-31                  None                        
  isFdaRegulatedDrug    True                        True                        
  US sites / total      15 / 53                     22 / 42                     

  The third cause of absence, checked rather than overlooked: the
  11.48 obligation binds only on an 'applicable clinical trial'. A
  trial that is not one owes nothing, and absence would mean neither
  opacity nor timing. isFdaRegulatedDrug and US site counts are
  printed above because they bear on it. 'Applicable clinical trial'
  is a defined legal term with more conditions than two fields, so
  this tool states the inputs and does not rule.

  M1 (maturity-dependent fields, 3):
    documentSection.largeDocumentModule.largeDocs[].date
    documentSection.largeDocumentModule.largeDocs[].label
    protocolSection.statusModule.resultsFirstPostDateStruct.date

C3  MAXIMUM AGE                       NOT REPORTED
    protocolSection.eligibilityModule.maximumAge
    A   "70 Years"             read as 70.00 years
    B   -- field absent --     NOT READ: field absent
    o   absent. Absent is not equal.

========================================================================
RUN 4 - C1 absent - A designModule.phases deleted (S4 gap closed)
========================================================================
C1  PHASE                             NOT REPORTED
    protocolSection.designModule.phases
    A   -- field absent --
    B   [1] PHASE3
    o   absent from A. Absent is not equal.

========================================================================
RUN 5 - THE EMPTY-LIST TRAP - BOTH records' armGroups set to []
========================================================================
C8  ARM TYPES                         NOT REPORTED
    protocolSection.armsInterventionsModule.armGroups[].type
    A   [0] 
    B   [0] 
    o   PRESENT BUT EMPTY in A, B. The field exists and declares zero values.
        Zero values is not noise - it is nothing to compare. [] == [] is True, so
        without this guard the multiset branch returns SAME. Found 3 Oct 2026 by
        S6 Run 5, in code that passed S4 acceptance on 16 Sep. Logged L5.

    ^ Symmetric ON PURPOSE. One empty list is easy to catch; two is
      the case that agrees with itself. Before the 3 Oct guard this
      printed SAME, with the line 'Same 0 value(s). Order ignored.'
      Clean code, no error, wrong answer - found by writing this
      criterion before the code it tests. Logged L5.

========================================================================
RUN 6 - THE GUARD SWITCHED OFF - B given posted results (THREE coupled fields)
========================================================================
------------------------------------------------------------------------
MATURITY GUARD - silent   (today: 2026-10-03)
------------------------------------------------------------------------
  Both records agree on hasResults. No lifecycle confound from
  this input. Absences below are not explained by it.

                        A                           B                           
  hasResults            True                        True                        
  overallStatus         COMPLETED                   RECRUITING                  
  primary completion    2025-06-03                  2026-04-30                  
    ...date type        ACTUAL                      ACTUAL                      
    ...passed?          True                        True                        
    ...days elapsed     487                         156                         
  results posted        2026-08-31                  2026-09-01                  
  isFdaRegulatedDrug    True                        True                        
  US sites / total      15 / 53                     22 / 42                     

  The third cause of absence, checked rather than overlooked: the
  11.48 obligation binds only on an 'applicable clinical trial'. A
  trial that is not one owes nothing, and absence would mean neither
  opacity nor timing. isFdaRegulatedDrug and US site counts are
  printed above because they bear on it. 'Applicable clinical trial'
  is a defined legal term with more conditions than two fields, so
  this tool states the inputs and does not rule.

  M1 (maturity-dependent fields, 3):
    documentSection.largeDocumentModule.largeDocs[].date
    documentSection.largeDocumentModule.largeDocs[].label
    protocolSection.statusModule.resultsFirstPostDateStruct.date

C9  RESULTS POSTED                       DIFFERENT
    protocolSection.statusModule.resultsFirstPostDateStruct.date
    A   "2026-08-31"
    B   "2026-09-01"
    >   A is '2026-08-31', B is '2026-09-01'.

C10  METHOD DESCRIBED                  NOT REPORTED
    protocolSection.outcomesModule.primaryOutcomes[0].description
    A   683 chars
    B   -- field absent --
    o   absent from B. Absent is not equal.
    o   NOT tagged (M). This field is not in M1:
        `description` is available at REGISTRATION. Many sponsors fill it only when posting
        results, but nothing requires them to wait. Its absence is therefore NOT
        explained by record maturity, and this tool will not say it is.
    .   PRESENCE ONLY. This check does not adjudicate what the text MEANS - that is
        C5/C6's machinery and rule N1. Both present and non-identical returns REVIEW.

C11a  DOCUMENT LABELS                   NOT REPORTED
    documentSection.largeDocumentModule.largeDocs[].label
    A   [2] Study Protocol, Statistical Analysis Plan
    B   -- field absent --
    o   absent from B. Absent is not equal.
    o   in M1 - this field cannot exist before results are posted.
        B: HAS posted results (2026-09-01). The submission pathway for
            this field existed and the field is still absent. Record maturity
            explains nothing here.
    o   NOT tagged (M): at least one record's absence is not accounted for by
        an untriggered obligation. Read the dates above and rule yourself.
    .   A document-presence field attests EXISTENCE, not COMPLETENESS. 42 CFR 11.48(a)(5)
        permits redacting trade secret and confidential commercial information before
        submission, so `hasSap: true` does not mean the statistical model is legible.
        See KNOWN-LIMITATIONS.md, L4.

    ^ The only run that proves the guard can turn OFF. A guard that
      always fires is indistinguishable from one that is hard-coded,
      and would quietly excuse every absence in every comparison.
      C11a has lost its (M) tag: B posted results, so the pathway
      existed, and the documents are still absent. The absence has
      become a disclosure fact rather than a timing artefact.
      THREE fields moved together - hasResults, primaryCompletion
      and resultsFirstPost - because a record cannot post results
      before reaching primary completion. Coupled factors are
      varied together AND the coupling is stated. Getting that
      coupling wrong is what the first version of this run did,
      and the tool caught it by refusing the impossible record.

========================================================================
RUN 7 - C7 made internally inconsistent - A masking set to "TRIPLE"
========================================================================
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
MATURITY GUARD - FIRED   (today: 2026-10-03)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  The two records are at DIFFERENT LIFECYCLE STAGES. Every NOT
  REPORTED below may reflect that rather than sponsor disclosure
  practice. This banner states facts about the records and makes
  no claim about the cause of any absence.

                        A                           B                           
  hasResults            True                        False                       
  overallStatus         COMPLETED                   RECRUITING                  
  primary completion    2025-06-03                  2027-05                     
    ...date type        ACTUAL                      ESTIMATED                   
    ...passed?          True                        False                       
    ...days elapsed     487                         -240                        
  results posted        2026-08-31                  None                        
  isFdaRegulatedDrug    True                        True                        
  US sites / total      15 / 53                     22 / 42                     

  The third cause of absence, checked rather than overlooked: the
  11.48 obligation binds only on an 'applicable clinical trial'. A
  trial that is not one owes nothing, and absence would mean neither
  opacity nor timing. isFdaRegulatedDrug and US site counts are
  printed above because they bear on it. 'Applicable clinical trial'
  is a defined legal term with more conditions than two fields, so
  this tool states the inputs and does not rule.

  M1 (maturity-dependent fields, 3):
    documentSection.largeDocumentModule.largeDocs[].date
    documentSection.largeDocumentModule.largeDocs[].label
    protocolSection.statusModule.resultsFirstPostDateStruct.date

C7a  MASKING LEVEL                             SAME
    protocolSection.designModule.designInfo.maskingInfo.masking
    A   "TRIPLE"
    B   "TRIPLE"
    =   Both are 'TRIPLE'.

C7b  WHO WAS MASKED                       DIFFERENT
    protocolSection.designModule.designInfo.maskingInfo.whoMasked
    A   [2] PARTICIPANT, INVESTIGATOR
    B   [3] PARTICIPANT, CARE_PROVIDER, INVESTIGATOR
    >   counts A=2  B=3
        in B but not A: CARE_PROVIDER x1

    ^ A now claims TRIPLE masking while naming TWO masked parties.
      Neither sub-check notices. That blind spot is the point of the
      run and the argument for C12 (record-against-itself), logged
      for v0.2. A merged C7 would have printed one verdict here and
      hidden both halves.

Now mark each run against acceptance/S6-presence-and-maturity.md,
or re-run with --record and let the tool write the verdicts.
```

</details>
