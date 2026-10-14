# Field map - read by hand

Read by:      Purnima
Date read:    2026-09-14
Source files: data/NCT06470828_2026-09-14.json   (A - Takeda)
              data/NCT07455383_2026-09-14.json   (B - Alkermes)

              ^ USE THE 2026-09-14 FILES. The 2026-09-02 copies are also in
                data/ and are kept on purpose, but they are out of date:
                Alkermes amended their record on 2026-09-03.

## Rules

1. Read every value below out of the JSON files with your OWN EYES.
   Do not run code to fill this in. That is the entire point of this step.
2. Then open both trials on the ClinicalTrials.gov website and confirm the
   same value appears there. Tick the box only if it does.
3. If a field is NOT PRESENT in the file, write the word ABSENT.
   Never leave a cell blank. A blank cell cannot be told apart from a cell
   you skipped - and that exact ambiguity is the bug this whole tool exists
   to prevent. Start as you mean to go on.
4. Copy values exactly as written, including quotes and capitals.
   "16 Years" - not 16, not "16 years".

## How to read the files

VS Code:  File > Open Folder > ctg-compare, then open data/ and click a file.
          Cmd+F to search for the field name in the right-hand column below.
          The little arrows in the left margin fold sections closed - use them
          to collapse protocolSection and walk down the tree one level at a time.

The dotted path is a set of folders to open, left to right.
protocolSection.eligibilityModule.minimumAge means: open protocolSection,
then eligibilityModule, then read minimumAge.

---

C1 . PHASE
    path: protocolSection.designModule.phases
    A = PHASE3
    B = PHASE3
    website agrees?   A [YES]   B [YES]


C2 . MINIMUM AGE
    path: protocolSection.eligibilityModule.minimumAge
    A = 16 Years
    B = 18 Years
    website agrees?   A [YES]   B [YES]


C3 . MAXIMUM AGE
    path: protocolSection.eligibilityModule.maximumAge
    A = 70 Years
    B = 70 Years
    website agrees?   A [YES]   B [YES]


C4 . SEX ELIGIBLE
    path: protocolSection.eligibilityModule.sex
    A = ALL
    B = ALL
    website agrees?   A [YES]   B [YES]


C5 . MAIN MEASUREMENT
    path: protocolSection.outcomesModule.primaryOutcomes[0].measure
    How many primary outcomes does each trial have?   A = 1   B = 1
    A = Change From Baseline to Week 12 in Mean Sleep Latency From the 4 Maintenance of Wakefulness Test (MWT) Wake Trials
    B = Change in mean sleep latency (MSL) on Maintenance of Wakefulness Test (MWT) from baseline to Week 12 by dose level
    website agrees?   A [YES]   B [YES]


C6 . MEASUREMENT TIMING
    path: protocolSection.outcomesModule.primaryOutcomes[0].timeFrame
    A = Baseline, Week 12
    B = Baseline to Week 12
    website agrees?   A [YES]   B [YES]


C7 . BLINDING
    path: protocolSection.designModule.designInfo.maskingInfo.masking
          protocolSection.designModule.designInfo.maskingInfo.whoMasked
    A masking = DOUBLE
    A whoMasked = PARTICIPANT, INVESTIGATOR
    B masking = TRIPLE
    B whoMasked = PARTICIPANT, CARE_PROVIDER, INVESTIGATOR
    website agrees?   A [YES]   B [YES]


C8 . ARM TYPES
    path: protocolSection.armsInterventionsModule.armGroups[].type
    How many arms does each trial have?   A = 3   B = 3
    Now list that many "type" values, comma separated, in the order they
    appear. Count first, then list. The count is the check on the list.
    A = PLACEBO_COMPARATOR, EXPERIMENTAL, EXPERIMENTAL
    B = PLACEBO_COMPARATOR, EXPERIMENTAL, EXPERIMENTAL
    website agrees?   A [YES]   B [YES]

    [2026-09-14 re-read. First pass recorded one arm type per trial.
     Both trials have MORE THAN ONE arm. A has 3. B has 3. Go and read
     all of them. Superseded answer, kept for the record:
        A = PLACEBO_COMPARATOR
        B = PLACEBO_COMPARATOR ]


C9 . RESULTS POSTED
    path: protocolSection.statusModule.resultsFirstPostDateStruct.date
    A = 2026-08-31
    B = ABSENT
    website agrees?   A [YES]   B [YES]


C10 . MEASUREMENT METHOD DESCRIBED
    path: protocolSection.outcomesModule.primaryOutcomes[0].description
    Is there a description field at all? If yes, write PRESENT and paste the
    first 15 words. If no, write ABSENT.
    A = PRESENT The MWT evaluates a person's ability to remain awake under soporific conditions for a defined period of time.
    B = ABSENT
    website agrees?   A [YES]   B [YES]


C11 . PROTOCOL / STATISTICS PLAN DOCUMENTS
    path: documentSection.largeDocumentModule.largeDocs[]
    NOTE: documentSection is at the TOP level, not inside protocolSection.
    How many documents does each trial have?   A = 2   B = 0
    Now list that many, label and date, semicolon separated. Or ABSENT.
    A = Study Protocol and 2024-10-23 ; Statistical Analysis Plan and 2025-05-26
    B = ABSENT
    website agrees?   A [YES]   B [YES]

    [2026-09-14 re-read. First pass recorded one document for A.
     A has 2. The second one is the more interesting of the two.
     Superseded answer, kept for the record:
        A = Study Protocol , 2024-10-23
        B = ABSENT ]

---

## Anything that surprised you

(Write it down even if it seems trivial. This is the only session where you
read these records with fresh eyes, and you will not get that back.)

On 14 Sep, 9 of your 11 answers were exact on the first pass. Two were not.
Answer these three in one line each. Two minutes. Guessing is fine - the
point is that the guess is written down BEFORE the code runs, not after.

HINT: scroll up and look at the "path:" line of all 11 checks. Look at the
square brackets. Some have [0] in them, some have [] with nothing inside,
some have no brackets at all. Those are three different instructions.


1. The two I got wrong on the first pass were C8 and C11.
   What made them harder than the other nine:
    - they were in multiple 'objects' (within {}) in one 'array' (within []) in json, which I overlooked the ordered list by ignoring the other objects of the array and just noting down the first object's key-value pair.

2. Reading the 11 paths above, the ones written with EMPTY square brackets
   [] are: None
    # the two paths C8 and C11 - have a [] which denotes all objects within whereas all the others have [0] meaning there is just one object within.

3. So my prediction: when the code runs in S2, it is most likely to be
   wrong on C8, C9, C10 and C11 because 1 - in C8 and C11 there are multiple objects and 2 - A and B do not have a match in C9, C10 and C10 where B has ABSENT values for the keys.

   And I would find that out by checking the ordered list for the number of objects present in the list and then going through each object for the values.


(After S2 runs we come back and see whether the prediction held.)



