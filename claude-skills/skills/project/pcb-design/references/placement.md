# Phase 6: placement

> Adapted 2026-10-30 from [sequoia-hope/easy_pcb](https://github.com/sequoia-hope/easy_pcb) `.claude/skills/pcb-design/references/placement.md` @ 95bfe5e (MIT, © 2026 Sequoia Alexander). Edit freely; this copy no longer tracks upstream.

Placement determines most of the board's quality. Good placement makes routing nearly automatic; bad placement can't be fixed by routing. Also read `headless-pipeline.md` §2 (via-room and pad-gap rules learned on CanSat) before placing a dense board.

## Order

1. **Fixed items** from `brief.md`: outline, mounting holes, connectors, keepouts, art zone. Lock them.
2. **Blocks in floorplan order**: work from connectors inward, following power and signal flow. Place each block as a unit before moving to the next.
3. **Within a block, critical loops first**:
   - switching power stages: input cap, switch, diode/low-side FET and ground return as one tight loop; then inductor, then output caps; feedback divider near the FB pin, away from the switch node
   - half-bridges: high-side and low-side FETs, bulk and ceramic caps across the bridge, shunt, all in the tightest possible loop
   - gate drivers right beside their FETs
   - crystals right at the oscillator pins
4. **ICs** in their block region, oriented so their pins face what they connect to.
5. **Supporting passives with their pins**: decoupling caps at each power pin (smallest value closest), pull-ups at their pins, termination resistors at the driver (series) or receiver (parallel).
6. **Test points and debug features.**
7. **Silkscreen space**: leave room for designators and connector labels now, not after routing.

**Follow the datasheet's layout guidelines** from each `parts/*.md`. If the datasheet shows a recommended layout, reproduce it.

## Rules

- **Never** place passives in a row, a grid, or any arrangement that is about tidiness rather than function. Every passive belongs to a pin.
- Align parts within a block where it costs nothing (a neat row of decoupling caps along an IC edge is fine), but function wins over neatness.
- Consistent orientation for polarized parts within a block helps assembly inspection.
- Keep switching nodes and high-dV/dt copper away from analog, clocks and board edges.
- Keep the ground return path in mind for every high-current loop: where does the current come back?
- Hot parts: spread out, near copper area and thermal vias, away from electrolytics and temperature-sensitive parts.
- Hand-soldered or reworked parts need clearance around them.
- Fiducials if assembly needs them (JLC generally doesn't for standard assembly, check).

## Checks

No placement-check script exists yet for new boards (the CanSat generator prints a courtyard/pad-gap/edge check). Check by hand, with `kdump.py`/pcbnew, or with `kicad-cli pcb drc`:
- passives clustered on a line or grid unrelated to their connected IC
- decoupling cap farther than ~3 mm from the nearest power pin on its net
- crystal and load caps far from oscillator pins
- courtyard overlaps, parts outside the board or in keepouts
- ratsnest length (total and per net) as a quality score when comparing variants
- loop area of SWITCH/SWITCH_HI loops from `nets.csv`

## Visual review

Render top/bottom 2D and 3D (`kicad-cli pcb render`) with the ratsnest visible. The reviewer answers:
1. Does each block sit together, near its connectors, in a sensible flow?
2. Is every passive with the part it serves?
3. Are the critical loops tight?
4. Is noisy separated from sensitive?
5. Is there room for routing, vias and silkscreen?
6. Would an experienced layout engineer place it like this?

## Gate checklist (phase 6)

- [ ] Fixed items match `brief.md` and are locked
- [ ] Placement checks done (output pasted)
- [ ] Datasheet layout guidelines followed per part (list)
- [ ] Visual review passed
- [ ] User reviewed the placement render
