---
name: report-format-check
description: Check whether an NKRAFA research report (เอกสารวิจัย) conforms to the required format — margins, fonts, headings, TOC, committee approval page, captions, bibliography. Use when asked to "check report format", "ตรวจรูปแบบรายงาน", or review a report's formatting against the standard.
---

# NKRAFA Research Report (เอกสารวิจัย) Format Specification

This skill checks a report against the reference format of the NKRAFA research document standard (derived from the reference report `C:\Knight\CS\รายงานพี่แซ่บ.docx`). Measurements are given in points/inches with Word twips in parentheses (1" = 1440 twips; font sizes in OOXML are half-points, so `sz=32` = 16pt).

## Workflow

1. **If the target is a `.docx`**: run the automated checker first:
   ```
   python scripts/check_docx.py "<path-to-report>.docx"
   ```
   (script path is relative to this skill's folder). It prints PASS/FAIL per machine-checkable rule.
2. **Manually verify** the rules the script cannot check (marked [manual] below): document section order, caption placement relative to figures/tables, committee-page wording and layout, TOC entries matching actual headings and page numbers, correct use of `(ต่อ)` continuation headings, and — in a rendered PDF — that no heading/pseudocode/table is split across a page boundary (§11), and that no word is torn across a line break by auto-hyphenation (§12).
   Note: §11 rules are stricter than the reference document; check them against the spec, not the reference.
3. **Report**: produce a conformance report listing every rule checked, its status (PASS / ❌ FAIL), and the location (page/section/heading) of each violation. End with a summary of what must be fixed.

---

## 1. Page setup

| Property | Required value |
|---|---|
| Paper | A4 portrait (11906 × 16838 twips) |
| Left margin | 1.5" (2160) |
| Right margin | 1" (1440) |
| Bottom margin | 1" (1440) |
| Top margin | **2" (2880) on chapter/section-opening pages; 1.5" (2160) on continuation pages** — done with separate Word sections |
| Header/footer from edge | 0.5" (720) |
| Default tab stop | 0.5" (720) |

## 2. Font

- Entire document uses **TH SarabunPSK**. Only permitted exception: Cambria Math inside equations.
- Body text: **16pt regular** (`sz=32`). (The reference occasionally squeezes a paragraph to 15pt with negative character spacing to make text fit; 16pt is the rule.)
- Body paragraphs justified with **Thai distributed** justification (`w:jc="thaiDistribute"`).
- Paragraph indentation is done with **tab stops**, not first-line indents. Common tab positions: 450, 540, 1170, 1980 twips.
- [manual] Body text must **never be bold** — bold is reserved for headings/labels/signature lines only.
- [manual] **Every paragraph's first line starts with a tab**, and that tab must land on the **same tab stop for every body paragraph** — pick one indent position and use it consistently throughout the body; don't mix different first-line tab stops paragraph to paragraph.
- [manual] **Sub-topics use numbered headings only** (`3.3.1␣␣ชื่อ`, `3.3.1.1…`, etc.) — never bullets, arrows (→, -, •), or other list markers for sub-topic structure.

## 3. Headings

- **Chapter opening** (new page, 2" top margin):
  - Line 1: `บทที่ N` — centered, **20pt bold**, its own paragraph.
  - Line 2: chapter name — **Heading 1 style: 20pt bold, centered, black**.
  - One blank line before body text begins.
- **Section headings (Heading 2)**: `N.N␣␣ชื่อหัวข้อ` — **18pt bold, left-aligned**. Number and title separated by **two spaces**.
- **Sub-sections (Heading 3)**: `N.N.N␣␣ชื่อ` — **16pt bold, left-aligned** (tab at 540 twips).
- **Front-matter/back-matter headings** (บทคัดย่อ, Abstract, กิตติกรรมประกาศ, สารบัญ, สารบัญตาราง, สารบัญรูป, บรรณานุกรม, ประวัติผู้วิจัย): Heading 1 style — 20pt bold centered.
- **ภาคผนวก divider page**: the single word ภาคผนวก, **32pt bold centered** on its own page.

## 4. Headers / page numbers

- Page number appears **top-right in the header**, TH SarabunPSK **16pt**, preceded by two empty header lines (pushing the number down).
- Front matter (บทคัดย่อ onward): **Thai letters** ก ข ค ง … (skipping ฃ ฅ per convention — reference uses ก ข ค ง ฉ ช).
- Body: **Arabic numerals restarting at 1** on Chapter 1 (`pgNumType start=1`).
- [manual] **No page number shown** on chapter-opening pages (`titlePg`) or on the cover/title pages (empty header).

## 5. Required document order [manual]

1. **ปกนอก (cover page)** — all centered bold: เอกสารวิจัย (22pt) / เรื่อง (20pt) / Thai title (22pt) / โดย (20pt) / author names with rank นักเรียนนายเรืออากาศ (20pt) / สาขา… (20pt) / โรงเรียนนายเรืออากาศนวมินทกษัตริยาธิราช (20pt) / ปีการศึกษา NNNN (20pt).
2. **ปกใน (title page)** — as cover but adds: English title (22pt bold), advisor names with (อาจารย์ที่ปรึกษาหลัก) / (อาจารย์ที่ปรึกษาร่วม) (18pt bold), and the degree statement เอกสารวิจัยฉบับนี้เป็นส่วนหนึ่งของการศึกษาตามหลักสูตร… (18pt bold).
3. **Committee approval page** (see §6).
4. **บทคัดย่อ** (Thai abstract) → **Abstract** (English) → **กิตติกรรมประกาศ** (ends with คณะผู้วิจัย, bold, positioned right).
5. **สารบัญ** → **สารบัญตาราง** → **สารบัญรูป**.
6. **Chapters 1–5**: บทที่ 1 บทนำ / บทที่ 2 แนวคิด ทฤษฎี และงานวิจัยที่เกี่ยวข้อง / บทที่ 3 วิธีดำเนินงานวิจัย / บทที่ 4 ผลการดำเนินงานวิจัย / บทที่ 5 สรุปผล อภิปรายผล และข้อเสนอแนะ.
7. **บรรณานุกรม** → **ภาคผนวก** (divider page, then appendix content) → **ประวัติผู้วิจัย**.

## 6. Committee approval page [manual]

Layout, top to bottom:

1. Report title — **20pt bold** (left/justified, not centered).
2. Approval sentence, 16pt thaiDistribute: เอกสารวิจัยฉบับนี้ได้ผ่านการตรวจสอบและเห็นชอบจากคณะกรรมการของภาควิชา…
3. `เมื่อวันที่ ..................` — dotted line for the date.
4. Director signature block: `น.อ. ..................` (bold) / name in parentheses on next line / position lines (ผู้อำนวยการกองวิชา…).
5. **คณะกรรมการ** — 16pt bold header.
6. Signature lines: rank + dotted line + role — `น.อ. ………… ประธานกรรมการ`, then `น.อ. ………… กรรมการ`, `ร.อ. ………… กรรมการ` — each followed by the name in parentheses on the next line, 16pt regular.
7. **อาจารย์ที่ปรึกษา** — 16pt bold header.
8. Two advisor signature lines (rank + dotted line, bold; name in parentheses beneath, regular).

## 7. Table of Contents

- Heading **สารบัญ** 20pt bold centered; beneath it a right-aligned **หน้า** label (16pt).
- **Level 1 entries** (front matter, บทที่ N …, บรรณานุกรม, ภาคผนวก, ประวัติผู้วิจัย): **16pt bold**, page number at a right-aligned tab at 8296 twips (no dot leader), spacing after 100 twips.
- **Level 2 entries** (`N.N␣␣title`): 16pt regular, indent 220 twips, left tab 720, right tab 8296.
- Continuation pages headed **สารบัญ (ต่อ)** with the หน้า label repeated.
- **สารบัญตาราง / สารบัญรูป**: same pattern; entries `ตารางที่ N.N␣␣caption` / `รูปที่ N.N␣␣caption`, 16pt, right-tab page numbers (~8280).
- [manual] Entries must match the actual headings/captions and page numbers in the body.

## 8. Figures, tables, captions

- **Figure captions below the figure, centered**: `รูปที่ N.N␣␣ชื่อรูป` — 16pt. Numbered per chapter (N = chapter number). In appendices, the chapter number is the appendix's Thai letter: `รูปที่ ก.1`, `ตารางที่ ค.1`.
- **Table captions above the table, left/thaiDistribute**: `ตารางที่ N.N␣␣ชื่อตาราง` — 16pt.
- [manual] **One blank line between an image and its caption**: never let the caption paragraph immediately follow the image paragraph — insert a single empty paragraph between them.
- [manual] A table continuing on the next page repeats its caption with **(ต่อ)** appended.
- Tables use the **Table Grid** style: single ½pt black borders on all cells.

## 9. Bibliography (บรรณานุกรม)

- APA style; **Thai entries first, then English**, each alphabetized.
- 16pt, thaiDistribute justification, **hanging indent 1"** (`left=1440, hanging=1440`).

## 10. Minute details

- Two spaces (`␣␣`) between every number and its title: headings, TOC entries, captions.
- Blank 16–18pt line between a chapter heading block and the first paragraph, and generally one blank line before a new Heading 2.
- Dotted signature/date lines use run-on dots `....` or Thai ellipsis dots `…………`, not underscores.
- Author/advisor names use **two spaces between first and last name** (e.g. ฐาปนัต␣␣บัวภิบาล).
- Page numbers in TOC have **no dot leaders** — plain right-aligned tab.
- Abstract first paragraph may start with a bold heading line; body abstracts are a single thaiDistribute-justified block.

## 11. Images & block layout — STRICTER THAN THE REFERENCE

These rules are deliberate improvements over the reference document (`รายงานพี่แซ่บ.docx` itself violates some of them — do NOT relax a check just because the reference fails it):

- **Images centered and sized to fit**: every image sits in its own paragraph, `jc=center`, and its width must not exceed the text column (8306 twips ≈ 5.77" ≈ 5,274,310 EMU). Prefer noticeably narrower than full column unless detail requires it.
- **Nothing beside an image**: no text — bullet points, topic numbers (`N.N`), labels, or wrapped body text — to the left or right of a picture. Images must be **inline** (`wp:inline`), not floating (`wp:anchor` with text wrapping); the paragraph containing a drawing must contain no other text.
- **Pseudocode blocks and tables must not split across pages**: every table row gets `<w:cantSplit/>` in its `trPr`; pseudocode/equation blocks kept as 1×1 tables likewise. A table too tall for one page repeats its caption with `(ต่อ)` on the next page instead of silently splitting a row.
- **Headings stay with their body**: Heading 1/2/3 styles keep `keepNext`/`keepLines` so a topic heading is never orphaned at the bottom of a page with its body on the next; [manual] verify in the rendered PDF that no heading is the last line of a page.

## 12. No word torn across a line break (auto-hyphenation over-triggering)

The Thai-justification fix (ZWSP at Thai word boundaries + `autoHyphenation` + `thaiDistribute`, see §2) makes Word hyphenate more aggressively than desired: it splits medium-length English/technical terms at grammatically valid but ugly points — `sequence`→`se-/quence`, `linear`→`line-/ar`, `Network`→`Net-/work`, `Detection`→`Detec-/tion`, `Backpropagation`→`Backpropaga-/tion`, `bounding`→`bound-/ing`, `boxes`→`box-/es`. These have a real hyphen (so they don't look like letter-spreading) but still read as broken — a proper-noun-like technical term should never be torn across a line break in a formal report.

- [manual] **Detect** by exporting to PDF and regex-scanning each page's `get_text()` for `([A-Za-z]{2,})-\n(\S)`. Every hit is a candidate; **exclude** two legitimate cases before flagging: (a) the break falls on an already-hyphenated compound word (`one-stage`, `real-time`) — that's just wrapping at its own hyphen, fine; (b) the break is inside a bibliography URL — URLs have no other way to fit and normally break at their own hyphens, fine.
- **Fix**: there is no OOXML per-run "don't hyphenate this word" flag — the only lever is paragraph-level `<w:suppressAutoHyphens/>`. For each genuine bad term, find every paragraph (and table-cell paragraph) containing it and add `<w:suppressAutoHyphens/>` to that paragraph's `pPr`. This is safe per-paragraph: pushing a 6–15 char term whole onto the next line costs only a small amount of extra `thaiDistribute` stretch elsewhere on the line, which is far less noticeable than a torn word. Re-export and re-run the same regex scan to confirm zero bad breaks remain.
