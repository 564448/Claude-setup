---
description: Loop nkrafa-report-formatter ↔ nkrafa-detail-checker on a report .docx until it is fully NKRAFA-conformant
argument-hint: <path-to-report.docx>
---

Run the NKRAFA report review loop on the file: $ARGUMENTS

## Setup
1. Verify the argument is a path to an existing `.docx` file (Glob/Read to confirm). If no
   file was given or it doesn't exist, ask the user for the correct path and stop.
2. This loop EDITS the given file in place (and its sibling `.pdf`). If the file does not
   already look like an NKRAFA-formatted report (no front matter / chapters), first launch
   `nkrafa-report-formatter` to do the initial conversion into a NEW `<name>_NKRAFA.docx`
   next to it, then run the loop on that new file instead.

## Review loop (maximum 3 rounds)
Repeat:

1. **Check** — launch the `nkrafa-detail-checker` agent (run_in_background: false) with the
   file path. It returns a numbered findings list and a verdict.
2. **Partition the findings** into:
   - **Agent-fixable**: formatting, layout, XML, justification artifacts, split blocks,
     page-number sequence, caption/TOC formatting, spacing rules.
   - **User-only**: content only the user can supply — dotted placeholders (names, dates),
     committee member names, pages the user deliberately removed, wording choices.
     These do NOT count against completion; collect them for the final report.
3. **Exit conditions**: if there are no agent-fixable findings, leave the loop. If this is
   round 3 and findings remain, leave the loop and report them as unresolved.
4. **Fix** — launch the `nkrafa-report-formatter` agent (run_in_background: false) with the
   exact agent-fixable findings list and these instructions: edit THIS file in place
   (loop mode — the no-overwrite rule is waived for this file only), re-export the sibling
   PDF via Word COM, and verify paragraph/section counts are unchanged after every save.
5. Next round.

## Final report to the user
- Rounds run, and what was fixed in each round.
- Remaining user-only items (things they must fill in themselves).
- Any unresolved agent-fixable findings after 3 rounds (with why, if known).
- Verdict: "[DONE] Completely done" only if the checker's last verdict was 100% conformant
  apart from user-only items; otherwise list what still stands in the way.
