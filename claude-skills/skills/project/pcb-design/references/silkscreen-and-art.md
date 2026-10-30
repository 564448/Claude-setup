# Phase 9: silkscreen and art

> Adapted 2026-10-30 from [sequoia-hope/easy_pcb](https://github.com/sequoia-hope/easy_pcb) `.claude/skills/pcb-design/references/silkscreen-and-art.md` @ 95bfe5e (MIT, © 2026 Sequoia Alexander). Edit freely; this copy no longer tracks upstream.

Silkscreen is the board's user interface. Someone holding the board should know what it is, how to power it, and what every connector does, without the schematic.

## Board identity (required)

- Board name; revision and date (e.g. "rev B 2026-10")
- **Open source**: repo URL and license (e.g. "CERN-OHL-S")
- **Work**: internal part number, company per policy; no public URLs
- Optional: author, a small QR code to the repo or docs

## Connectors (required, every one)

Each gets a reasoned label next to it: **function** ("MOTOR", "CAN", "USB", "BATT IN"), **polarity / pinout** ("+" "−", signal names, pin 1 marker), **ratings** ("12–48 V DC", "60 V MAX", "3.3 V LOGIC"), and **warnings** where relevant ("NO REVERSE POLARITY PROTECTION"). Decide the wording in a table in the gate file first (connector, label text, reason), then place.

## Designators

Policy from `brief.md`: **all** (every part), **selective** (connectors, ICs, test points, jumpers, LEDs, adjustable parts), or **none** (small hobby boards; keep connector, LED and test point labels and generate an assembly drawing with designators on a fab layer).

Every shown designator is: adjacent to its own part and clearly associated; **not under any part**, including its own; **not crossed by vias or pads** (silk over exposed copper gets clipped by the fab); at most two rotations on the board (0° and 90°), consistent within a block; a consistent size (default 0.8–1.0 mm height, ≥ 0.15 mm line width; check JLC minimums).

## Overlaps: zero tolerance

No silk-to-silk, silk-to-pad or silk-to-via overlap, and no silk over the board edge. If two footprint outlines collide, **edit a board-local copy of the footprint** to trim the outline (see `kicad-tools.md`). Polarity indicators (diodes, electrolytics, LEDs) and pin 1 on every IC and connector must remain visible after trimming.

## Art

Every board gets a little art in the art zone from `brief.md`.
- User-supplied (SVG/PNG): convert with the KiCad Image Converter at the reserved size.
- Claude-drafted: propose 2–3 small line-art concepts related to the board's purpose; the user picks.
- Consider exposed copper (ENIG looks great), copper + mask openings, or silk on copper for contrast.
- Same overlap rules; stay out of keepouts and away from sensitive nets (exposed copper art is not grounded unless intended).

## Checks

No silk-check script exists yet. Check against the actual rendered text outline (not the text anchor): silk-silk overlap, silk over pads/vias/exposed copper, silk near the board edge, designator under a courtyard (including its own), designator whose nearest courtyard isn't its own part, text below minimum height/width, connector without a label, missing board identity. `kicad-cli pcb drc` with silk checks set to error covers part of this.

## Gate checklist (phase 9)

- [ ] Connector label table with reasoning
- [ ] Board identity present
- [ ] Silk checks pass (output pasted)
- [ ] Top and bottom silk renders reviewed
- [ ] Art placed and approved
- [ ] User reviewed the silk render
