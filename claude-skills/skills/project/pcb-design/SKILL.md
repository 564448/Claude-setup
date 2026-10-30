---
name: pcb-design
description: Full KiCad PCB lifecycle in one skill — requirements, part selection with datasheet audit, schematic, net classes, layout brief, stackup and rules, placement, routing (live editing via kicad-mcp in KiCad 9, or the headless placement → Specctra DSN → Freerouting → pcbnew → kicad-cli DRC → Gerbers pipeline), simulation, silkscreen, release. Phases end at gates with real tool output as evidence. Use when asked to design, start, route, fix DRC, inspect, review or release a KiCad board, "route the board", "make the PCB", or redo the CanSat carrier. Encodes every failure met on the CanSat board.
license: Own work plus MIT-licensed portions from sequoia-hope/easy_pcb (see LICENSE-easy_pcb.txt)
---

# PCB design: from requirements to fab files

> Own material (live editing, headless pipeline, failure catalogue) plus the phase/gate workflow adapted 2026-10-30 from [sequoia-hope/easy_pcb](https://github.com/sequoia-hope/easy_pcb) `.claude/skills/pcb-design/SKILL.md` @ 95bfe5e (MIT, © 2026 Sequoia Alexander; see `LICENSE-easy_pcb.txt`). Edit freely; this copy no longer tracks upstream.

The goal is a board a senior engineer would sign off on: a schematic that reads like a person drew it, a layout that follows the physics, every part checked against its datasheet, and DRC that is genuinely clean.

The work runs in **phases**. Each phase ends at a **gate**: a file in `design/gates/` with the phase checklist, the evidence for each item (command output, calculation, render) and the review findings. **A phase is not done until its gate file exists with real evidence.** "Done" without a gate file is a failure. Never write "passed" for a check you did not run.

Use the whole lifecycle for a new board. For an existing board (inspect, fix DRC, re-route, release), enter at the matching phase, and skip phases the user did not ask for.

## Before anything else

1. Read `LESSONS.md` in this folder (rules the user has had to correct).
2. Run `kicad-cli version`; read `references/kicad-tools.md`. This machine has KiCad 9.0; the headless pipeline was built on 8 (see its header).
3. Is the project **open source** (personal boards, repo URL on silkscreen) or **work/confidential** (internal part number, nothing public)? It changes silkscreen and what may leave the machine.
4. Look for an existing `design/` folder and gate files, and resume from the last passed gate instead of starting over.
5. Projects live under the work root's `Project/` folder (CLAUDE.md filing rule); ask if unsure which.

## Project layout

```
<project>/
  design/
    intent.md        phase 0     parts/        phase 1 (one audit file per part or group)
    architecture.md  phase 1     datasheets/   the PDFs actually read
    nets.csv         phase 3     brief.md      phase 4
    stackup.md       phase 5     sim/          phase 8 (one folder per simulation)
    decisions.md     running log: decision, reasoning, alternatives, date
    gates/phaseN.md  gate checklists with evidence and review findings
    bringup.md       phase 10
  hw/<board>/<variant>/    the KiCad project for each board variant
```

## Phases

| # | Phase | Key output | Gate | User sign-off? | Read |
|---|-------|-----------|------|----------------|------|
| 0 | Design intent | `intent.md` | Every requirement has a number or an explicit "don't care" | **Yes** | `intent-and-brief.md` |
| 1 | Architecture and parts | block diagram, `parts/*.md` | Every part audited against its datasheet; calculations done; sourcing confirmed | No | `datasheet-audit.md` |
| 2 | Schematic | schematic | ERC clean, style checks, every part cross-checked against its audit, visual review | No | `schematic-style.md` |
| 3 | Net classification | `nets.csv` | Every net classified with a reason | Glance | `net-classes.md` |
| 4 | Mechanical and layout brief | `brief.md` | Outline, holes, connectors, sides, layers, density, art zone decided | **Yes** | `intent-and-brief.md` |
| 5 | Stackup and rules | `stackup.md`, rules in tool | Every net class has rules; every rule is sourced | No | `stackup-and-rules.md` |
| 6 | Placement | placed board | Placement checks pass; visual review on render | Review render | `placement.md` |
| 7 | Routing | routed board | `kicad-cli` DRC 0 violations / 0 unconnected, parity clean, every warning explained | No | `routing.md`, `headless-pipeline.md` |
| 8 | Simulation and SI | `sim/` | Every triggered simulation has a result or a written waiver | No | `simulation.md` |
| 9 | Silkscreen and art | finished silk | Zero overlaps, all connectors labeled, board identity present | Review render | `silkscreen-and-art.md` |
| 10 | Release | fab outputs | Sync check, CPL rotation check, gerber review, final review | **Yes** | `sync-and-release.md` |

All files are in `references/`; read a phase's file **when you start that phase**, not all at once. Load a domain file only when the board has that circuit: `domains/motor-drive.md`, `domains/io-protection.md` (any off-board connector), `domains/high-speed.md`.

## At every gate

1. Run the phase's checks and paste the actual output into the gate file.
2. Export renders for anything visual (`kicad-cli` schematic SVG/PDF, per-layer copper, 3D).
3. Review it independently (see `references/review-protocol.md`). **Subagent reviewers only if the user has allowed subagents**; otherwise do a separate re-derivation pass and write "not independently reviewed" in the gate file.
4. Fix findings, or dispute them in `decisions.md`. Re-review if anything significant changed.
5. If the phase needs user sign-off, stop and say exactly what you need decided.

## Iterating

Going backward is normal. When an upstream artifact changes (a part swap, a new net, a moved connector), list the downstream gates it invalidates, mark them stale in their gate files and re-run them. Never patch downstream to hide an upstream change. Experiments get their own **variant** folder under `hw/<board>/`; never overwrite a variant the user has looked at.

## Which tool for which task

| Task | Tool |
|---|---|
| "Is net X connected?" / "show me all footprints on the back" | kicad-mcp (live inspection) |
| "Move U3 2 mm left and rotate it 90°" | kicad-mcp (live edit, undoable) |
| "Route the crystal load caps to Y1" (a few short nets) | kicad-mcp `create_track` |
| "Route the whole board" / "make the PCB" / "fix DRC" | headless pipeline (`references/headless-pipeline.md`) |
| KiCad isn't running, or the board isn't open in the PCB Editor | headless pipeline / `kicad-cli` only |
| ERC, DRC, parity, exports | `kicad-cli` (always the authority) |

A common flow: place and arrange parts live with kicad-mcp, hand off to the pipeline for bulk routing + DRC, reopen in KiCad to inspect the result and hand-fix what DRC still flags. Setup and troubleshooting for kicad-mcp: `references/kicad-tools.md`.

## Hard rules

- **`kicad-cli pcb drc --severity-all` is the only authority** on layout correctness. Never trust Freerouting's own violation count or a pcbnew connectivity check.
- **The schematic is the only source of truth** for values, footprints, MPNs and supplier part numbers. Change it there, push to the PCB, run the sync check.
- **No part without its datasheet opened.** If it can't be fetched, stop and ask the user to attach it. Never fill in a part's requirements from memory.
- **No programmatic-looking schematics**: no grids of symbols, no global labels standing in for wires within a sheet, no passives detached from what they serve (`schematic-style.md`).
- **No passives in a row.** Every passive sits with the part it serves (`placement.md`).
- **Don't hand-route long traces by coordinates.** Power goes in pours and planes, critical nets are kept short by placement, everything else goes to the autorouter with full net-class rules. Short critical nets by hand are fine.
- **Autorouter runs are governed** (priority, threads, heap, timeout; `routing.md`).
- **Via counts come from calculation**, never one via on a net whose current needs more.
- **Never suppress or waive a DRC/ERC error silently.** Every waiver goes in `decisions.md` with a reason.
- **Zero silkscreen overlaps.** Fix colliding footprint silk with a board-local footprint edit.
- **Log every non-obvious decision** in `decisions.md` as it happens.
- **Check scripts mostly don't exist yet.** The sync, silk, placement, net and style "checks" in the references are done by hand or with ad hoc pcbnew/`kdump.py`/S-expression scripts until someone writes them. Say which you actually ran.

## When the user corrects you

Add the correction to `LESSONS.md` as a concrete rule (what was wrong, what to do instead) in the same turn.
