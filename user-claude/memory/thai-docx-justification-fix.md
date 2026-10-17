---
name: thai-docx-justification-fix
description: How to fix stretched letters / wide word gaps in justified Thai Word documents (NKRAFA reports)
metadata: 
  node_type: memory
  type: reference
  originSessionId: 89d04c41-d3f6-41d7-9016-99ef042f5ed8
  modified: 2026-07-20T08:31:12.587Z
---

For Thai .docx reports (e.g. NKRAFA format), justified Thai+English text misbehaves because Word only breaks lines at spaces when no break points exist inside Thai phrases:
- `thaiDistribute` justification → extreme letter-stretching when a long English word wraps.
- normal justify (`both`) → huge gaps at the few real spaces.

**Working recipe (proven on รายงาน_Neural_Networks_YOLO_NKRAFA_v2.docx, 2026-07):**
1. Insert zero-width spaces (U+200B) at Thai word boundaries with PyThaiNLP `word_tokenize(engine="newmm")` in each run.
2. Enable Word auto-hyphenation in settings.xml (`<w:autoHyphenation/>`, `consecutiveHyphenLimit=2`, `hyphenationZone=360`) so long English words hyphenate.
3. Keep/restore `jc=thaiDistribute` — remaining slack spreads invisibly across the line.

Also: pseudo-code blocks as 1×1 tables need `<w:cantSplit/>` in trPr to avoid page splits; use `keepNext` on headings. Verify via Word COM export to PDF → PyMuPDF render to PNG → Read; regex `(?:[A-Za-z]{1,2} ){3,}` on extracted text detects letter-spread artifacts. Beware: python-docx edits once silently dropped the document tail (last 2 sections) — always verify paragraph/section counts after saving.

**Follow-up bug from the recipe above (found 2026-07-20):** Word's `autoHyphenation` (step 2) doesn't just hyphenate genuinely-long unbreakable words — it also chops short/medium technical terms (6-15 letters) at valid-but-ugly points: `sequence`→`se-/quence`, `linear`→`line-/ar`, `Network`→`Net-/work`, `Detection`→`Detec-/tion`, `Backpropagation`→`Backpropaga-/tion`, `bounding`→`bound-/ing`, `boxes`→`box-/es`. These have a real hyphen (so they don't look like the earlier letter-spread bug) but the user still flagged them — for a formal report, splitting a proper-noun-like technical term across a line break at all is undesirable, correct hyphenation point or not.

There is no OOXML per-run "don't hyphenate this word" flag; the only lever is paragraph-level `<w:suppressAutoHyphens/>`. **Detection method**: export PDF → regex `([A-Za-z]{2,})-\n(\S)` on `page.get_text()` per page finds every hyphenation break; inspect each hit's context and only treat it as a bug if the break isn't at an already-hyphenated compound word (`one-stage`, `real-time`) or inside a bibliography URL (those are fine to break). **Fix**: for each genuine bad-split term, find every paragraph (and table cell paragraph) containing it via python-docx and add `<w:suppressAutoHyphens/>` to that paragraph's `pPr` (`pPr.append(OxmlElement('w:suppressAutoHyphens'))` after `p._p.get_or_add_pPr()`) — this is safe per-paragraph because thaiDistribute only risks letter-stretch for genuinely 14+ char unbreakable words, and pushing a 6-15 char term whole to the next line costs negligible extra stretch. Re-export and re-scan with the same regex to confirm zero bad breaks remain.

**Simpler variant that worked (2026-09-20, CS334 System Analysis report):** for a report with no genuinely-long unbreakable words, ZWSP segmentation + `jc=thaiDistribute` **without** `autoHyphenation` gave clean justified Thai and left SQL/English identifiers intact. Turning hyphenation on there mangled table content (`PRO-/JECTS.project_id`, `US-/ERS.user_id`, `Dia-/gram`, `Lev-/el 1`). Also: when inserting ZWSP, suppress it after opening brackets/quotes and before closing brackets and `,.;:%` — otherwise Word wraps right after `(` (e.g. `TODO (` / newline / `ยังไม่เริ่ม)`).
