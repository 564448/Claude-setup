# Phase 8: simulation and signal integrity

> Adapted 2026-10-30 from [sequoia-hope/easy_pcb](https://github.com/sequoia-hope/easy_pcb) `.claude/skills/pcb-design/references/simulation.md` @ 95bfe5e (MIT, © 2026 Sequoia Alexander). Edit freely; this copy no longer tracks upstream.

Simulate what is likely to fail or hard to fix later, not every net. Triggers come from `nets.csv`; a judgment pass adds anything the triggers miss.

## Triggers

| Situation | Simulation |
|-----------|-----------|
| Any DIFF_HS or SE_HS above a length threshold | impedance + crosstalk (2D field solver on the actual cross-section; 2.5D/3D for vias and breakouts if > ~1 GHz content) |
| RF | antenna match and pattern (openEMS), matching network in circuit sim |
| SWITCH_HI near ANALOG/CLOCK | coupling estimate: spacing, overlap length, mutual capacitance/inductance |
| POWER_HI with a tight drop budget | DC IR drop / current density (no built-in KiCad tool; script or openEMS DC) |
| Switching converter, control loop, filters | SPICE (ngspice) with vendor models: loop stability, startup, transient |
| Motor bridge | SPICE of the bridge with parasitics from layout: ringing, gate drive, dead time |
| Thermal hot spots | spreadsheet estimate first; FEM only if marginal |

## Aggressor / victim check

List every pair of nets where one is an aggressor class (SWITCH, SWITCH_HI, CLOCK, DIFF_HS, SE_HS) and the other a victim class (ANALOG, ANALOG_DIFF, CLOCK, RF, sensitive SIGNAL) with segments running parallel within a spacing threshold (default 3× trace height above plane) for more than a length threshold, on the same or adjacent layers. Each finding is fixed, simulated, or waived with reasoning. No script exists yet; a `kdump.py`-based geometry pass can produce it.

## Tooling (open source first)

ngspice (circuit), openEMS (RF, via transitions, antenna), a 2D field solver for cross-sections. Check what is installed before planning a sim (`ngspice` is not guaranteed on this machine).

## Output

`design/sim/<name>/`: the question being answered, setup, input files, results (PNG plots), conclusion, and what changed in the design.

## Gate checklist (phase 8)

- [ ] Trigger list generated from `nets.csv` (pasted)
- [ ] SI/EMC judgment pass added anything missed
- [ ] Each triggered item has a result or a waiver in `decisions.md`
- [ ] Aggressor/victim check run, findings resolved
- [ ] Design changes from sims fed back (stale gates re-run)
