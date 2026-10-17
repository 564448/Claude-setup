---
name: verification-before-completion
description: MANDATORY before saying any task is done, fixed, working, passing or ready, and before committing, pushing, uploading, handing back a file, or writing the end-of-task summary. Load it every time you are about to report success or completion, in any domain. Requires running a fresh check, reading its full output, and ending with a "[Verified]" evidence block; no success claims without evidence.
license: MIT
---

# Verification Before Completion

> Forked 2026-09-27 from [obra/superpowers](https://github.com/obra/superpowers) `verification-before-completion` (MIT License), adapted for non-code work and to pair with `root-cause-debugging`. Edit freely; this copy no longer tracks upstream.

**Rule:** no claim of success without evidence from a check you ran **in this turn**. An earlier run, a "should work", or another agent's report is not evidence.

## The gate: run before any success claim

1. **Identify:** which check would prove the claim? (see below)
2. **Run** it fresh and in full. No partial run, and no reusing old output.
3. **Read** the whole output: exit code, failure/error/warning counts, the actual file or state.
4. **Compare:** does the output really support the claim?
   - **No:** report the real status with the evidence. Don't soften it.
   - **Yes:** make the claim and quote the evidence.

If no check is possible (no tool, no access, it needs a human, e.g. printing or flying the UAV), say so explicitly and state what is still **unverified** and how the user can check it.

## What counts as evidence

**If a loaded domain skill defines its own verification standard (e.g. `pcb-autoroute` §4), that standard is the evidence.** The table below covers everything else.

| Claim | Evidence | Not enough |
|---|---|---|
| Tests pass | Test run in this turn: 0 failed | Earlier run, "should pass" |
| Builds / runs | Build or run exit 0, expected output seen | Linter clean, code "looks right" |
| Bug fixed | The original repro now passes | "Changed the code" |
| Regression test works | Red-green: passes → revert fix → fails → restore → passes | Passes once |
| File / document produced | Reopened the saved output and checked the specific properties | "Applied the changes" |
| Remote or config change | The target itself shows the new state (command on the host, tool loads the config) | Local edit done, copy/write returned OK |
| Subagent finished | Checked its actual changes (diff, files, output) | Agent reported "done" |
| Requirements met | Re-read the request, checked each point | Checks pass |

## Red flags: stop and run the gate

- Words like "should", "probably", "seems to", "looks good" about unchecked work
- Saying "Done!", "Fixed!", "Perfect!" before any check has run
- About to commit, push, upload or hand back a file without a check
- Trusting a subagent's or tool's success message
- A partial check standing in for the full one ("linter passed" for "it builds")
- "It's a tiny change, no need to check"

## Report format

End the completion message (or the end-of-task summary) with:

> **[Verified]**
> - `<check run>` → `<key result, e.g. 34/34 passed, DRC 0 errors>`
> - **Unverified:** `<anything not checked, and why>` (omit if none)

This block is a marker that the skill ran. Never write it without having run the checks it lists.
