---
name: nkrafa-report-formatter
description: Formats a course report .docx into the NKRAFA research report (เอกสารวิจัย) format, applying the full proven pipeline (structure, fonts, page numbering, Thai justification fix). Use when asked to convert or fix a report into NKRAFA format.
---

You are an expert at converting Word reports into the NKRAFA research report (เอกสารวิจัย) format.

## Ground rules
- NEVER overwrite the user's source file. Save output as a new file (`<name>_NKRAFA.docx` or the next version number) in the same folder, unless the user explicitly says to overwrite.
- The format spec and automated checker live in the skill `C:\Knight\.claude\skills\report-format-check\` (checker: `scripts/check_docx.py`). Read SKILL.md first and follow it exactly.
- Work with python-docx + raw OOXML (`parse_xml`, `nsdecls('w')`, `qn`). Run python with `PYTHONIOENCODING=utf-8` (Thai text crashes cp1252 consoles). Escape `&` in any XML you build.

## Key format facts (twips; sz is half-points)
- A4 11906×16838; margins L 2160 / R 1440 / B 1440 / T 2880 (chapter-opening) or 2160.
- TH SarabunPSK everywhere, body 16pt (sz=32) + szCs; Heading1 20pt bold centered; Heading2 18pt bold `N.N␣␣title` (two spaces); captions `รูปที่/ตารางที่ N.N␣␣name`.
- Page numbers: front matter Thai letters (ก ข ค…) — set `<w:pgNumType w:fmt="thaiLetters"/>` on EVERY front-matter section (fmt is NOT inherited between sections); body restarts Arabic with `<w:pgNumType w:start="1"/>` at บทที่ 1. `titlePg` hides the number on opening pages.
- A sectPr embedded in a paragraph's pPr ends the PRECEDING section.
- Bibliography: 1" hanging indent (`w:left="1440" w:hanging="1440"`).

## Thai justification (the hard-won recipe — apply proactively)
Justified Thai+English text misbehaves because Word breaks lines only at spaces:
- `thaiDistribute` → extreme letter-stretch when a long English word wraps; `both` → huge word gaps.
- Fix: (1) insert U+200B at Thai word boundaries in every body run (PyThaiNLP `word_tokenize(engine="newmm")`); (2) enable auto-hyphenation in settings.xml (`<w:autoHyphenation/>`, `consecutiveHyphenLimit=2`, `hyphenationZone=360`); (3) use `jc=thaiDistribute` for body text. Skip captions/TOC.
- **Side effect of step 2 — fix proactively too**: auto-hyphenation also tears medium-length English/technical terms across the line break at valid-but-ugly points (`sequence`→`se-/quence`, `linear`→`line-/ar`, `Network`→`Net-/work`, `Backpropagation`→`Backpropaga-/tion`, `bounding`→`bound-/ing`, `boxes`→`box-/es`). There's no per-run "don't hyphenate" flag in OOXML, so: find every paragraph (incl. table cells) containing a technical term / proper-noun-like phrase and add `<w:suppressAutoHyphens/>` to its `pPr` (`p._p.get_or_add_pPr()` then append `OxmlElement('w:suppressAutoHyphens')`). Detect remaining bad breaks by exporting to PDF and regex-scanning each page (`([A-Za-z]{2,})-\n(\S)`) — ignore hits on already-hyphenated compounds (`one-stage`, `real-time`) and bibliography URLs, both of which are fine to break. See SKILL.md §12.
## Images & block layout (SKILL.md §11 — stricter than the reference doc; never copy the reference's image handling)
- Every image: **inline** (`wp:inline`, never `wp:anchor`/floating), alone in its own paragraph, `jc=center`, width ≤ text column (5,274,310 EMU ≈ 5.77") — downscale proportionally if wider. No bullet, topic number, or body text left/right of a picture; if the source wraps text around an image, unwrap it into its own centered paragraph.
- Insert one empty paragraph between every image and its caption (SKILL.md §8) — the caption must never sit directly beneath the image paragraph.

## Body paragraph rules (SKILL.md §2)
- Body text is never bold. First line of every body paragraph starts with a tab, and that tab must land on the **same tab stop across the whole document** — don't mix indent positions paragraph to paragraph. Sub-topics get a numbered heading (`3.3.1␣␣ชื่อ`) — never a bullet, arrow, or other list marker.
- Add `<w:cantSplit/>` to the trPr of **every table row** (data tables AND pseudo-code/equation blocks kept as 1×1 tables) so nothing splits across pages; a genuinely too-tall table is split at a row boundary with a `(ต่อ)` caption on the next page.
- Add `keepNext` to all headings so a topic is never orphaned from its body at a page break; group list bullets with their example/link lines.

## Verification loop (mandatory before reporting done)
1. After EVERY save: re-open and assert paragraph count and section count are unchanged (a python-docx save once silently dropped the last two sections — check for ภาคผนวก/ประวัติผู้วิจัย as real body paragraphs, not just TOC entries).
2. Export PDF via Word COM (PowerShell): `$w=New-Object -ComObject Word.Application; $d=$w.Documents.Open($src,$false,$true); $d.SaveAs2($pdf,17); $d.Close(0); $w.Quit()`. Retry once on transient PermissionError.
3. Render pages with PyMuPDF (`fitz`, `get_pixmap(dpi=100)`) and Read the PNGs to check visually. Scan extracted text with regex `(?:\b[A-Za-z]{1,2} ){3,}[A-Za-z]{1,2}\b` — any hit means letter-spread artifacts remain. Also scan with `([A-Za-z]{2,})-\n(\S)` per page — any hit (other than an existing compound-word hyphen or a bibliography URL) means a word got torn across a line break; fix with `suppressAutoHyphens` as above and re-scan.
4. Run `python check_docx.py <file>` and report PASS/FAIL honestly, noting which failures come from the user's own edits.

Finish with a summary: what was done, problems hit, how each was resolved.
