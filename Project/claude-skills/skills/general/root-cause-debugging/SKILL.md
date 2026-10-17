---
name: root-cause-debugging
description: MANDATORY at the start of any debugging work, before proposing any fix. Load it whenever the user reports a bug, says something is broken, failing, throwing, flaky or "not working", pastes an error, stack trace or log, a test/build/DRC fails, or a previous fix did not work, in any language, tool or domain (code, hardware, PCB, documents). Disciplined loop: recite the marker, reproduce, map the fail path and its knobs, rank and try to falsify hypotheses, keep a ledger of every run, fix one thing, and stop to rethink after three failed fixes.
license: MIT
---

# Root-Cause Debugging

> Written 2026-09-27. Ideas combined from obra/superpowers `systematic-debugging` (MIT) and thananon/9arm-skills `debug-mantra` (no license, so no text was copied; only the ideas are reused).

**Rule:** no fix before you can say *what* breaks and *why*. A fix aimed at a symptom counts as a failure, even if the symptom goes away.

## Recite first: verbatim, once, at the top of your first debugging reply

> **[root-cause-debugging]**
> 1. **Reproduce first.** No reliable repro, no hypothesis.
> 2. **Map the fail path.** Debugger → knobs one at a time → compare with what works → tagged probes.
> 3. **Try to kill the hypothesis.** Rank several; run the disproof first.
> 4. **Log every run.** The answer must fit the whole ledger.
> 5. **One fix at the root.** Three failed fixes means stop and rethink.

- Recite it **once per debugging session**, word for word. Don't paraphrase, shorten or translate it, even when replying in another language.
- Don't recite it again mid-session. If a new, unrelated bug starts later, recite it once more.
- If the user says "skip the recital", skip it but still follow every step.
- The recital is a marker that the skill is loaded. It doesn't replace the steps below.

Work the five steps in order. Keep a **ledger** from the first run (step 4). It is your memory for the session.

## 1. Reproduce

Get a repro you can run before anything else.

- **Reliable:** save it as something runnable, like a failing test, script, CLI call or DRC command, with exact inputs and environment. Aim for a fast (seconds), deterministic pass/fail signal. Pin seeds, time and inputs where you can.
- **Flaky:** it isn't debuggable yet. Raise the failure rate first: loop it, add load, run in parallel, narrow timing windows. Around 50% is workable; 1% is not.
- **None:** stop. Tell the user plainly and ask for what you need (logs, the file, env access, permission to instrument). Do not start hypothesising.

While setting up, collect the cheap evidence:
- Read the whole error, warnings and stack trace. Note files, lines and codes.
- **What changed recently?** git diff/log, new dependencies, config, tool versions, hardware or environment differences.

## 2. Map the fail path

Find *where* reality departs from what you expect. Escalate only when the previous tactic can't reach the bug:

1. **Debugger:** if one can reach the failure site, use it before touching anything else.
2. **Trace + knobs:** follow the path end to end and list every knob that can change the outcome, such as config flags, env vars, inputs, branch conditions, timing, concurrency, build or tool options. Flip **one knob at a time**.
3. **Compare with something that works:** a similar working case in the same codebase, the last good commit, or a reference implementation (read it fully, don't skim). List every difference, even ones that "can't matter".
4. **Instrument:** log what enters and leaves each component boundary (e.g. placement → DSN → router → pcbnew → DRC). Tag every probe with one unique prefix like `[DBG-7c1e]` so a single grep removes them all at the end.

If the bad value shows up deep in a call chain, trace it **backwards** caller by caller until you reach where it originates. Fix there, not where it surfaces.

## 3. Hypothesise, then try to kill it

- Write **3–5 ranked hypotheses**, each as "X causes it because Y". One hypothesis anchors you on the first plausible idea.
- For the top one, walk it end to end: does it explain *every* symptom?
- Design the cleanest **disproof** and run that first. A hypothesis that survives a real attempt to kill it is worth fixing.
- If you don't understand something, say "I don't understand X". Don't paper over it.

## 4. Keep the ledger

After every run, add one line:

| # | Changed | Result | Rules in / out |
|---|---|---|---|

- A new hypothesis must agree with **every** row, not just the latest. If any row contradicts it, it's wrong or incomplete.
- When unsure, design the **single experiment** whose result settles the question, and run that instead of nearby variations.
- Show the ledger to the user when reporting progress.

## 5. Fix and confirm

1. Make sure the repro from step 1 fails for the reason you identified.
2. Make **one** change at the root cause. No bundled refactors or "while I'm here" edits.
3. Re-run the repro (it passes) and the surrounding checks (nothing else broke). Report with the actual output. If the `verification-before-completion` skill exists, follow it.
4. Remove every `[DBG-…]` probe (grep for the prefix) unless the user wants to keep them.

**If the fix doesn't work:** add it to the ledger and go back to step 2 with the new evidence. Don't stack another fix on top.

**After 3 failed fixes, stop.** Especially when each fix shows a new problem somewhere else, this points to a wrong design or assumption, not a wrong hypothesis. Explain what you've learned and discuss the approach with the user before fix #4.

**Genuinely external cause** (environment, timing, third-party): record what was ruled out, add sensible handling (retry, timeout, clear error) and logging for next time. Be sceptical first, because most "no root cause" results are an unfinished investigation.

## Stop signs: go back to the step you skipped

- "Quick fix now, investigate later" / "let's just try X"
- Changing several things before one run
- "It's probably X" without a disproof attempt
- Proposing fixes before a reliable repro exists
- "One more try" after two or more failed fixes
- The user asks "is that actually happening?", "stop guessing", or "are we stuck?"
