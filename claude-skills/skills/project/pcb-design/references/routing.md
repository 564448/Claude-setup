# Phase 7: routing

> Order and autorouter-governance ideas adapted 2026-10-30 from [sequoia-hope/easy_pcb](https://github.com/sequoia-hope/easy_pcb) `.claude/skills/pcb-design/references/routing.md` @ 95bfe5e (MIT, © 2026 Sequoia Alexander); Windows commands and the pipeline/DRC steps are own material. Edit freely; this copy no longer tracks upstream.

Claude is bad at hand-routing long traces by picking coordinates. Route in this order and let tools do as much as possible.

## Order

1. **Planes and pours.** GND plane (L2 on 4-layer), power planes/pours, POWER_HI copper as zones, not traces. Set zone priorities and clearances.
2. **Via arrays** for every net with a via count from `nets.csv`: stitch power pours between layers where current transfers, with the computed count. Arrays, not single vias. On a plane board, give every GND/3V3 pad its own fanout via before routing (see `headless-pipeline.md`).
3. **Short critical connections by hand, only when short.** Gate drive, crystal, shunt Kelvin sense, switch node: a few mm thanks to placement. Do these live with kicad-mcp `create_track` (undoable) or in the GUI.
4. **Differential and impedance-controlled pairs** with the interactive/diff-pair router; one layer over solid reference; length match per rules.
5. **Autorouter for everything else** (Freerouting) with the full net-class rules loaded. Lock what steps 1–4 routed first so the autorouter can't disturb it. Run it governed (below). The proven end-to-end procedure is in `headless-pipeline.md` §3.
6. **Cleanup**: remove autorouter artifacts (acute angles, unnecessary vias, long detours), re-pour zones (`kclean.py`).
7. **Ground stitching vias** around the board edge, between ground pours, and around RF/sensitive areas.

## Running the autorouter without hurting the host

Freerouting takes the whole machine by default (`-mt` = cores − 1, no memory or time bound). Every run is governed, including "just a quick test".

- **One run at a time.** Never launch variants in parallel; queue them.
- **Low priority**, **at most half the cores** (`-mt`, use `1` without a measured reason), a **heap cap** (`-Xmx4g`), and a **wall-clock budget** (start at 10 minutes; raise only if it timed out while still making progress).
- **Good enough is done:** stop at 0 unrouted and a clean DRC. Don't burn passes chasing via counts.
- If a run hits its budget, report it with the unrouted count. Don't silently retry with bigger limits; the fix is usually placement, rules or layer count, not more compute.

PowerShell:

```powershell
$p = Start-Process -FilePath $java -NoNewWindow -PassThru -ArgumentList '-Xmx4g','-jar','freerouting.jar','-de','board.dsn','-do','board.ses','-mp','100','-mt','1'
$p.PriorityClass = 'BelowNormal'
if (-not $p.WaitForExit(600000)) { $p.Kill(); 'Freerouting hit the 10 min budget' }
```

`scripts/dsn.py` `run()` is already governed with these defaults: below-normal priority, `-mt 1`, `-Xmx4g`, 600 s timeout (kills the process and returns False, so nothing is imported). Override with `FR_THREADS`, `FR_HEAP`, `FR_TIMEOUT` or the `run()` arguments, and only raise them on a measured reason. The PowerShell snippet above is for running Freerouting by hand.

## Rules of thumb

- Every signal has a continuous reference plane under it. No high-speed or SE_HS trace crosses a plane split. If a layer change is needed, put a ground via next to the signal via.
- Keep the area of high di/dt loops minimal; return current flows directly under the trace on the plane.
- No traces under switch nodes on the adjacent layer except ground.
- Analog and Kelvin sense lines as tight pairs, away from switching copper.
- Thermal reliefs off for POWER_HI connections, on for hand-soldered pins and big ground pads that need to be solderable.
- Teardrops on (where supported).

## Checks

- `kicad-cli pcb drc --severity-all`: **0 errors, 0 unrouted** (this is the authority, not Freerouting's own count). Paste the report.
- Schematic parity: 0 differences.
- Every DRC warning explained in the gate file, or fixed.
- Current capacity: for each POWER/POWER_HI net, the narrowest copper neck and the via count at each layer transition meet the `nets.csv` derived values (by hand or ad hoc script; none exists yet).
- Plane integrity: report splits/slots in the GND plane and any DIFF_HS/SE_HS trace crossing one.
- Visual review on per-layer copper renders.

## Gate checklist (phase 7)

- [ ] DRC 0 errors, 0 unrouted (pasted)
- [ ] Parity 0 differences
- [ ] Current capacity check passes
- [ ] Plane integrity check passes
- [ ] Every warning explained
- [ ] Per-layer renders reviewed
