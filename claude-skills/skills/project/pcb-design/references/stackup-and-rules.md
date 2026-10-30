# Phase 5: stackup and design rules

> Adapted 2026-10-30 from [sequoia-hope/easy_pcb](https://github.com/sequoia-hope/easy_pcb) `.claude/skills/pcb-design/references/stackup-and-rules.md` @ 95bfe5e (MIT, © 2026 Sequoia Alexander). Edit freely; this copy no longer tracks upstream.

## Stackup

Default to JLCPCB standard impedance-controlled stackups. **Look up the current JLC stackup and capability pages at the start of the phase**: offerings and limits change. Record the source URL and date in `stackup.md`.

Defaults unless `brief.md` says otherwise:
- **2 layer**: 1.6 mm, 1 oz. Only for simple, slow boards with coarse parts.
- **4 layer**: JLC04161H-7628 (or current equivalent), 1 oz outer / 0.5 oz inner. L1 signal + parts, L2 solid GND, L3 power / signal, L4 signal. Never split L2. For fine-pitch boards with many nets, use In1 = GND and In2 = +3V3 planes (the CanSat choice, see `headless-pipeline.md` §1).
- **6 layer** for many high-speed signals or dense BGAs: S / GND / S / PWR / GND / S.
- Heavy copper (2 oz outer) for high-current boards, accepting coarser minimums.

`stackup.md` records each layer: copper weight, dielectric thickness, Er and role.

## Impedance

For every impedance target in `nets.csv`, compute trace width and spacing for the actual stackup with JLC's impedance calculator or a field solver (KiCad calculator, or a 2D solver script). Record width/gap per layer per target. Common: 50 Ω SE, 90 Ω USB diff, 100 Ω Ethernet/LVDS diff.

## Fab limits (JLCPCB, verify current values)

Record from JLC's capabilities page: min trace/space per copper weight, min via drill and annular ring, min hole-to-hole, copper-to-edge, silkscreen min width and height, soldermask dam, min drill for plated slots, castellation rules. Set these as the **board-level minimums** in the tool. Add a margin (e.g. design to 0.15 mm trace/space even if 0.1 mm is allowed) unless density demands otherwise, and log the choice. The values already proven on the CanSat board are in `headless-pipeline.md` §2 item 6.

## Rule set

Every class in `nets.csv` becomes a net class in the tool with: track width (min / preferred / max), clearance, via size and drill, diff pair width and gap (if diff).

Plus custom rules (`.kicad_dru`) for:
- HV creepage between HV nets and everything else
- copper pour thermal relief (none on POWER_HI, thermals on hand-soldered parts)
- courtyard overlap, silk to pad, silk to board edge, silk to silk
- diff pair skew and length matching tolerance
- keepouts from `brief.md`

**Every rule cites its source**: a row in `nets.csv`, a fab limit, or a standard. Rules without a source are deleted or justified in `decisions.md`.

## DRC severities

Turn every check that matters to **error**, not warning: unconnected items, clearance, courtyard overlap, silk over pad, silk overlap, track width, annular ring, hole clearance, footprint vs library mismatch, schematic parity. Leaving important checks as warnings is how bad boards ship.

## Gate checklist (phase 5)

- [ ] `stackup.md` with source and date
- [ ] Impedance widths computed per target
- [ ] Fab minimums entered as board constraints
- [ ] Every net class from `nets.csv` exists in the tool with values matching derived widths
- [ ] Custom rules written and each one sourced
- [ ] DRC severities set (list pasted)
- [ ] DRC on the empty/placed board produces no rule-definition errors
