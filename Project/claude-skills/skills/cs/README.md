# CS skills

Project scope: linked into `C:\Knight\.claude\skills`.

- **[report-format-check](./report-format-check/SKILL.md)**: checks an NKRAFA research report (เอกสารวิจัย) `.docx` against the required format: margins, fonts, headings, TOC, committee approval page, captions, and bibliography. The checker is `scripts/check_docx.py`, run with `PYTHONIOENCODING=utf-8`. Triggers on "check report format" / "ตรวจรูปแบบรายงาน".

## How the NKRAFA tooling fits together

The spec + checker above is shared by two agents in `C:\Knight\.claude\agents\`:
- `nkrafa-report-formatter`: applies the full pipeline (structure, fonts, page numbering, Thai justification fix).
- `nkrafa-detail-checker`: read-only. It hunts for tiny deviations such as spacing artifacts, split blocks, the page-number sequence, captions, and TOC mismatches.

The `/Review_NKRAFA_report` command (`C:\Knight\.claude\commands\`) is the orchestrator. It alternates formatter (fix) and checker (find) until nothing is left to fix. `report-format-check` alone is the lighter one-off spec check.
