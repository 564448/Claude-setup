# Phase 10: sync and release

> Adapted 2026-10-30 from [sequoia-hope/easy_pcb](https://github.com/sequoia-hope/easy_pcb) `.claude/skills/pcb-design/references/sync-and-release.md` @ 95bfe5e (MIT, © 2026 Sequoia Alexander). Edit freely; this copy no longer tracks upstream.

## Schematic is the source of truth

Values, footprints, MPNs and supplier part numbers are changed **only in the schematic**, then pushed to the PCB (KiCad: Update PCB from Schematic). Never edit them in the PCB editor. Never edit the BOM by hand.

## Sync check (from phase 6 on, at every gate)

For every reference designator, compare schematic, PCB and generated BOM/CPL: present in all three (no orphans); value; footprint (library ID, and for board-local edits that the base footprint matches); MPN, manufacturer, LCSC/supplier PN; DNP flag. Any mismatch fails. Also confirm every BOM part still resolves to an in-stock part. `kicad-cli pcb drc --schematic-parity` covers footprint/net parity; the field comparison has no script yet.

## Release outputs

- Gerbers + drill (JLC's KiCad settings; the CanSat export commands are in `headless-pipeline.md` §3)
- BOM in fab format; CPL / pick-and-place
- Schematic PDF; assembly drawing PDF (top/bottom, with designators even if hidden on silk)
- 3D STEP
- the `design/` folder with gates and decisions
- git tag `<board>-rev<X>`

## CPL rotation check

Rotation and origin offsets between library footprints and JLC's part orientation are a classic silent failure. Apply a rotation correction (per-part offset field or the JLCPCB fabrication plugin), then render the CPL over the board image and verify pin 1 and polarity for **every** polarized part and IC. Paste the list.

## Gerber review

Render the gerbers layer by layer in a viewer separate from the CAD tool (gerbv / tracespace / KiCad Gerber viewer): outline closed, drills present, mask openings correct, paste on SMD pads only, silk not clipped, no missing pours.

## Final independent review

Fresh context, given: `intent.md`, all `parts/*.md`, schematic PDF, `nets.csv`, `stackup.md`, all renders, DRC/ERC/sync outputs and gate files. It answers: would you send this to fab? What is the highest-risk thing on this board? Anything in `intent.md` not met?

## Bring-up plan

`design/bringup.md`: power-up sequence with current limit, what to measure at each test point and the expected value, isolation jumpers to open first, firmware smoke test.

## Gate checklist (phase 10)

- [ ] All earlier gates current (not stale)
- [ ] Sync check passes
- [ ] DRC/ERC re-run on final files: clean
- [ ] Stock re-checked
- [ ] CPL rotation verified for every polarized part
- [ ] Gerbers reviewed in a separate viewer
- [ ] Final independent review: no blocking findings
- [ ] Bring-up plan written
- [ ] Git tagged
- [ ] **User approves release**
