"""Automated format checker for NKRAFA research reports (เอกสารวิจัย).

Usage: python check_docx.py <report.docx>

Checks the machine-verifiable rules from SKILL.md against the docx XML and
prints PASS/FAIL per rule. Rules that need visual/manual judgment (caption
placement, TOC page-number accuracy, signature-page layout) are NOT checked
here — see the Workflow section of SKILL.md.
"""
import re
import sys
import zipfile
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

PASS, FAIL, WARN = "PASS", "FAIL", "WARN"
results = []


def check(status, rule, detail=""):
    results.append((status, rule, detail))


def para_text(p):
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))


def main(path):
    with zipfile.ZipFile(path) as z:
        doc = z.read("word/document.xml").decode("utf-8")
        styles = z.read("word/styles.xml").decode("utf-8")
        try:
            settings = z.read("word/settings.xml").decode("utf-8")
        except KeyError:
            settings = ""

    # ---- 1. Page setup ----
    sects = re.findall(r"<w:sectPr.*?</w:sectPr>", doc, re.S)
    if not sects:
        check(FAIL, "Page setup", "no sectPr found")
    bad = []
    for i, s in enumerate(sects, 1):
        sz = re.search(r'<w:pgSz w:w="(\d+)" w:h="(\d+)"', s)
        if not sz or (sz.group(1), sz.group(2)) != ("11906", "16838"):
            bad.append(f"section {i}: page size not A4 portrait")
        m = re.search(
            r'<w:pgMar w:top="(\d+)" w:right="(\d+)" w:bottom="(\d+)" w:left="(\d+)"', s
        )
        if not m:
            bad.append(f"section {i}: no margins")
            continue
        top, right, bottom, left = m.groups()
        if top not in ("2160", "2880"):
            bad.append(f"section {i}: top margin {top} (expected 2160 or 2880 twips)")
        if right != "1440":
            bad.append(f"section {i}: right margin {right} (expected 1440 = 1\")")
        if bottom != "1440":
            bad.append(f"section {i}: bottom margin {bottom} (expected 1440 = 1\")")
        if left != "2160":
            bad.append(f"section {i}: left margin {left} (expected 2160 = 1.5\")")
    check(FAIL if bad else PASS,
          f"Page size A4 + margins L1.5\"/R1\"/B1\"/T1.5-2\" across {len(sects)} sections",
          "; ".join(bad))

    if '<w:pgNumType w:start="1"/>' in doc:
        check(PASS, "Body page numbering restarts at 1 (pgNumType start=1)")
    else:
        check(FAIL, "Body page numbering restarts at 1", "no pgNumType start=1 found")

    tab = re.search(r'<w:defaultTabStop w:val="(\d+)"/>', settings)
    if tab and tab.group(1) == "720":
        check(PASS, 'Default tab stop 0.5" (720 twips)')
    else:
        check(WARN, 'Default tab stop 0.5"', f"found {tab.group(1) if tab else 'none'}")

    # ---- 2. Fonts ----
    fonts = Counter(re.findall(r'w:ascii="([^"]+)"', doc))
    other = {f: n for f, n in fonts.items() if f not in ("TH SarabunPSK", "Cambria Math")}
    if other:
        check(FAIL, "All fonts TH SarabunPSK (Cambria Math allowed for equations)",
              f"other fonts used: {other}")
    else:
        check(PASS, "All fonts TH SarabunPSK (Cambria Math allowed for equations)",
              f"{fonts.get('TH SarabunPSK', 0)} runs")

    sizes = Counter(re.findall(r'<w:sz w:val="(\d+)"', doc))
    dominant = sizes.most_common(1)[0][0] if sizes else None
    if dominant == "32":
        check(PASS, "Dominant body size 16pt (sz=32)")
    else:
        check(FAIL, "Dominant body size 16pt",
              f"dominant size is sz={dominant} ({int(dominant)/2 if dominant else '?'}pt)")

    # ---- 3. Heading styles ----
    h1 = re.search(r'<w:style [^>]*w:styleId="Heading1">.*?</w:style>', styles, re.S)
    if h1:
        s = h1.group()
        ok = ('w:val="40"' in s and "<w:b/>" in s and 'w:val="center"' in s
              and "TH SarabunPSK" in s)
        check(PASS if ok else FAIL, "Heading 1 style: TH SarabunPSK 20pt bold centered",
              "" if ok else "style properties differ from spec")
    else:
        check(FAIL, "Heading 1 style defined", "no Heading1 style")

    h2 = re.search(r'<w:style [^>]*w:styleId="Heading2">.*?</w:style>', styles, re.S)
    if h2:
        s = h2.group()
        ok = 'w:val="36"' in s and "<w:b/>" in s and "TH SarabunPSK" in s
        check(PASS if ok else FAIL, "Heading 2 style: TH SarabunPSK 18pt bold",
              "" if ok else "style properties differ from spec")
    else:
        check(FAIL, "Heading 2 style defined", "no Heading2 style")

    toc1 = re.search(r'<w:style [^>]*w:styleId="TOC1">.*?</w:style>', styles, re.S)
    if toc1:
        s = toc1.group()
        ok = "<w:b/>" in s and 'w:val="32"' in s and 'w:val="right" w:pos="8296"' in s
        check(PASS if ok else WARN, "TOC level 1 style: 16pt bold, right tab at 8296",
              "" if ok else "style properties differ from spec")
    else:
        check(WARN, "TOC level 1 style defined", "no TOC1 style (TOC may be manual)")

    # ---- 4. Paragraph-level checks ----
    paras = re.findall(r"<w:p[ >].*?</w:p>", doc, re.S)
    texts = [para_text(p).strip() for p in paras]

    n_thai = doc.count('w:val="thaiDistribute"')
    check(PASS if n_thai > 50 else FAIL,
          "Body paragraphs use Thai distributed justification",
          f"{n_thai} thaiDistribute paragraphs")

    # Heading numbering: N.N + two spaces (Heading2 paragraphs)
    bad_h2 = []
    for p, t in zip(paras, texts):
        if '<w:pStyle w:val="Heading2"/>' in p and t:
            if not re.match(r"^\d+\.\d+  \S", t):
                bad_h2.append(t[:40])
    check(FAIL if bad_h2 else PASS,
          "Section headings numbered 'N.N␣␣title' (two spaces)",
          "; ".join(bad_h2[:5]))

    # ---- 5. Required headings present and in order ----
    required = ["บทคัดย่อ", "Abstract", "กิตติกรรมประกาศ", "สารบัญ",
                "บทที่ 1", "บทที่ 2", "บทที่ 3", "บทที่ 4", "บทที่ 5",
                "บรรณานุกรม", "ภาคผนวก", "ประวัติผู้วิจัย"]
    full = "\n".join(texts)
    pos, missing, out_of_order = -1, [], []
    for r in required:
        i = full.find(r, pos + 1)
        if i == -1:
            if r in full:
                out_of_order.append(r)
            else:
                missing.append(r)
        else:
            pos = i
    if missing:
        check(FAIL, "Required sections present", "missing: " + ", ".join(missing))
    elif out_of_order:
        check(FAIL, "Required sections in order", "out of order: " + ", ".join(out_of_order))
    else:
        check(PASS, "Required sections present and in order",
              "บทคัดย่อ → Abstract → กิตติกรรมประกาศ → สารบัญ → บทที่ 1-5 → บรรณานุกรม → ภาคผนวก → ประวัติผู้วิจัย")

    # Committee approval page markers
    markers = ["คณะกรรมการ", "ประธานกรรมการ", "อาจารย์ที่ปรึกษา"]
    miss = [m for m in markers if m not in full]
    check(FAIL if miss else PASS, "Committee approval page markers present",
          ("missing: " + ", ".join(miss)) if miss else "คณะกรรมการ / ประธานกรรมการ / อาจารย์ที่ปรึกษา")

    # ---- 6. Captions ----
    figs = [t for t in texts if t.startswith("รูปที่")]
    tbls = [t for t in texts if t.startswith("ตารางที่")]
    bad_cap, one_space = [], []
    for t in figs + tbls:
        if re.match(r"^(รูปที่|ตารางที่) (\d+|[ก-ฮ])\.\d+  \S", t):
            continue
        if re.match(r"^(รูปที่|ตารางที่) (\d+|[ก-ฮ])\.\d+ \S", t):
            one_space.append(t[:40])
        else:
            bad_cap.append(t[:40])
    check(FAIL if bad_cap else PASS,
          f"Captions follow 'รูปที่/ตารางที่ N.N␣␣name' (ก.N in appendix) — {len(figs)} figure, {len(tbls)} table",
          "; ".join(bad_cap[:5]))
    if one_space:
        check(WARN, "Captions with single space after number (should be two)",
              "; ".join(one_space[:5]))

    # ---- 7. Images & block layout (SKILL.md §11 — stricter than the reference) ----
    TEXT_WIDTH_EMU = 5274310  # 8306 twips text column
    draw_paras = [p for p in paras if "<w:drawing" in p]
    beside, uncentered, too_wide = [], [], []
    for p in draw_paras:
        t = para_text(p).strip()
        label = t[:35] if t else "(image paragraph)"
        if t:
            beside.append(label)
        jc = re.search(r'<w:jc w:val="(\w+)"', p)
        if not jc or jc.group(1) != "center":
            uncentered.append(label)
        if any(int(cx) > TEXT_WIDTH_EMU
               for cx in re.findall(r'<wp:extent cx="(\d+)"', p)):
            too_wide.append(label)
    check(FAIL if beside else PASS,
          f"No text beside images ({len(draw_paras)} image paragraphs)",
          "; ".join(beside[:5]))
    check(FAIL if uncentered else PASS, "Images centered (jc=center)",
          "; ".join(uncentered[:5]))
    check(FAIL if too_wide else PASS,
          "Images fit within text column (≤ 5.77\" wide)",
          "; ".join(too_wide[:5]))
    n_anchor = doc.count("<wp:anchor")
    check(FAIL if n_anchor else PASS,
          "Images inline (wp:inline), not floating (wp:anchor)",
          f"{n_anchor} floating images" if n_anchor else "")

    n_rows = len(re.findall(r"<w:tr[ >]", doc))
    n_cantsplit = doc.count("<w:cantSplit/>")
    if n_rows == 0:
        check(PASS, "Table rows protected from page splits (cantSplit)", "no tables")
    elif n_cantsplit >= n_rows:
        check(PASS, "Table rows protected from page splits (cantSplit)",
              f"{n_cantsplit}/{n_rows} rows")
    else:
        check(FAIL, "Table rows protected from page splits (cantSplit)",
              f"only {n_cantsplit}/{n_rows} rows have <w:cantSplit/>")

    missing_keep = [sid for sid in ("Heading1", "Heading2", "Heading3")
                    if (m := re.search(r'w:styleId="' + sid + r'">.*?</w:style>',
                                       styles, re.S))
                    and "<w:keepNext/>" not in m.group()]
    check(FAIL if missing_keep else PASS,
          "Heading styles keep with body (keepNext)",
          "missing keepNext: " + ", ".join(missing_keep) if missing_keep else "")

    # ---- 8. Bibliography hanging indent ----
    n_hang = doc.count('w:left="1440" w:hanging="1440"')
    check(PASS if n_hang >= 3 else WARN,
          'Bibliography entries use 1" hanging indent',
          f"{n_hang} paragraphs with left=1440 hanging=1440")

    # ---- report ----
    icons = {PASS: "PASS", FAIL: "❌ FAIL", WARN: "⚠️ WARN"}
    print(f"Format check: {path}\n" + "=" * 60)
    for status, rule, detail in results:
        line = f"{icons[status]}  {rule}"
        if detail:
            line += f"\n         {detail}"
        print(line)
    n_fail = sum(1 for s, _, _ in results if s == FAIL)
    n_warn = sum(1 for s, _, _ in results if s == WARN)
    print("=" * 60)
    print(f"{len(results)} checks: {len(results)-n_fail-n_warn} passed, {n_fail} failed, {n_warn} warnings")
    return 1 if n_fail else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_docx.py <report.docx>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
