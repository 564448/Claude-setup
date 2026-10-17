# My Claude Skills & Agents — CS / NKRAFA Report Tooling

These are the skills and agents I have available in Claude Code that exist specifically to support the NKRAFA เอกสารวิจัย (research report) coursework pipeline.

## Skills

### `report-format-check`
Checks whether an NKRAFA research report `.docx` conforms to the required format: margins, fonts, headings, table of contents, committee approval page, captions, bibliography. Triggered by "check report format" / "ตรวจรูปแบบรายงาน" or a request to review formatting against the standard.

### `Review_NKRAFA_report`
Runs a closed loop between the `nkrafa-report-formatter` agent and the `nkrafa-detail-checker` agent on a report `.docx`, repeating fix → check cycles until the report is fully NKRAFA-conformant.

### `upload-to-github`
Preps a coursework project folder for GitHub and uploads it: static code checks, README generation, `.gitignore` + `LICENSE` (checking upstream licenses when the code is derived from another project), then pushes to a new or existing repo via `gh`. Always confirms before the actual push.

### `andrej-karpathy-skills:karpathy-guidelines`
Behavioral guidelines to reduce common LLM coding mistakes, derived from Andrej Karpathy's observations. **Mandatory: use this skill any time a program/code is being written.** Surfaces assumptions, keeps changes minimal and surgical, and defines verifiable success criteria before/after coding.

### `emilkowalski/skills` (installed via `npx skills@latest add`)
UI/animation "taste" skills from Emil Kowalski (Vercel/Linear, creator of Sonner/Vaul), installed at the root of `C:\Knight` (`.agents\skills\`). Covers `animate`, `animation-vocabulary`, `apple-design`, `emil-design-eng`, `find-animation-opportunities`, `improve-animations`, `pick-ui-library`, `prototype`, `review-animations` — see full breakdown in [`Project/skills-and-agents/README.md`](../../Project/skills-and-agents/README.md).

## Agents

### `nkrafa-report-formatter`
Formats a course report `.docx` into the full NKRAFA research report format — structure, fonts, page numbering, and Thai text-justification fixes — applying a proven pipeline end to end.

### `nkrafa-detail-checker`
Meticulously inspects an already-formatted NKRAFA report for tiny deviations from spec and from the reference look: spacing artifacts, split blocks, page-number sequence, caption details, TOC mismatches. Read-only — reports findings, does not fix them itself.

## How they fit together

`Review_NKRAFA_report` is the orchestrator: it alternates the formatter agent (fixes) and the checker agent (finds remaining issues) until the checker reports nothing left to fix. `report-format-check` is the standalone, lighter-weight version for a one-off spec check without the full fix loop.
