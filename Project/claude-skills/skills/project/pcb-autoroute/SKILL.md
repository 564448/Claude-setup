---
name: pcb-autoroute
description: Generate, autoroute and DRC-clean a KiCad 8 PCB end-to-end without touching the GUI — placement generator → Specctra DSN with pre-placed via fanout → Freerouting → session import → pcbnew scripting (fill, clean-up, link, stitch) → kicad-cli DRC as the only authority → Gerbers. Use when asked to "route the board", "make the PCB", "fix DRC", or to redo the CanSat carrier. Encodes every failure met on the CanSat board and how to avoid it.
---

# PCB autoroute pipeline (KiCad 8 + Freerouting), lessons included

Reference implementation: `C:\Knight\Project\SPACE\Cansat\hardware2` (Rev C, 40 × 45 mm, 4‑layer, **KiCad DRC 0 violations / 0 unconnected**). Scripts live in `scripts/`, tools in `tools/` next to this file. Read `C:\Knight\Project\SPACE\Cansat\CanSat_PCBA_Components.md` §7–8 for the design history.

## 0. Decide the stack-up FIRST (the one decision that made everything else work)

| Situation | Choice |
|---|---|
| Fine‑pitch parts (LGA/QFN/VSSOP at 0.5 mm) + ≥ 40 nets on ≤ 20 cm² | **4 layers**: In1 = GND plane, In2 = +3V3 plane. Every GND/3V3 pad gets its own via before routing → no pour islands, only signals routed |
| Sparse board, coarse parts | 2 layers with GND pours can work; expect islands around fine‑pitch pads that need hand work |

On 2 layers the CanSat board ended with 2–4 GND pads that **no automation could connect** (pockets sealed by tracks, no via room, ESP32 pads underneath). 4 layers cost a few dollars more and removed the problem entirely. Do not spend hours on 2‑layer GND islands again.

## 1. Placement rules that prevent routing failures

1. **Nothing that needs a via may sit over a module's pin row on the other side** (ESP32 rows, LC29H pad columns, XBee/Teensy through‑holes). Rotate the module so its pins run along the board edges and its empty interior is under the dense cluster.
2. Leave **≥ 1.0 mm** between the pad extents of two back‑side modules (ESP32 ↔ LC29H had a 0.75 mm strip: no via fits there — nothing with a GND/3V3 pad may be placed above it).
3. Through‑hole rows are barriers on **both** sides; a socketed module (XBee) may have low parts (≤ 2.1 mm) under its body, and its courtyard should be only the socket strips.
4. Keep ≥ 0.5 mm courtyard‑to‑courtyard; real library footprints (VSSOP pads reach ±3.2 mm, SOIC‑8 ±4.65 mm, JST vertical ≈ 9.4 × 8.5 mm) are much larger than body sizes — run the placement checker with real courtyards before routing.
5. Give every 0402/0603 GND pad a fanout‑able spot (outward direction free on both layers); QFN side pins that share the exposed pad's net don't need one — put one via **in the EP**.
6. Use JLCPCB rules from the start in the `.kicad_pro`: clearance 0.127, track 0.15, via 0.4/0.2 (route with 0.5/0.25), annular 0.10, hole‑to‑hole 0.25, edge 0.4. The generator writes these; `dsn.write()` regenerates the `.kicad_pro`, so re‑apply if you edit rules by hand.

## 2. Pipeline (each step is a script in `scripts/`; set `CANSAT_OUT=<project dir>` and `CANSAT_TAG=<name>`)

```
gen_kicad2.py --write        # placement + schematic + PCB + embedded footprints; prints courtyard/pad-gap/edge check
dsn.py  (export)             # Specctra DSN: 4 layers, planes, fanout vias as (type protect) wiring, net classes
dsn.py  (run 150–200 passes) # Freerouting 2.4.1 headless (tools/freerouting.jar + tools/jre-25)
dsn.py  (parse_ses + write)  # import: coords are um*10  → /10000 ; fanout re-added from <tag>_fanout.json
kclean.py                    # pcbnew: exact-duplicate vias, merge <0.3 mm same-net vias, edge vias, zone settings, FILL, save
kicad-cli pcb drc --severity-all --format json   # THE authority. Read violations + unconnected_items from JSON
kdump.py → kfinish.py → kapply2.py               # only for nets kicad-cli lists as unconnected (NETS=..., CLR=0.2, SKIPSTITCH=1)
kdelseg.py / kdelnet.py / kdel.py                # surgical removal by coordinates / whole net / DRC-listed dangling items
kicad-cli pcb export gerbers + drill              # 4 copper layers, paste, mask, silk, edge; Excellon; zip with PowerShell
```

Freerouting rotation/mirror facts (verified): front placement angle = KiCad angle; **back placement angle = KiCad angle + 180**, Freerouting mirrors back images about the Y axis. KiCad's own rotation is CCW on screen; back‑side footprints store y‑mirrored pad coordinates (`pad_world()` in `gen_kicad2.py` is the single source of truth — never re‑derive it).

## 3. Failure catalogue → prevention (all of these happened)

| Symptom | Cause | Prevention |
|---|---|---|
| Imported tracks 10× too big | `.ses` `(resolution um 10)` = 10 units/µm | divide by 10 000 |
| Tracks land on the wrong pads of back‑side parts | mirror convention | angle+180 for back, verify with `dsn.verify()` (0 dangling ends) |
| Freerouting "N violations" while KiCad says 0 | it counts foreign vias through its ideal planes / 0.13 mm pad gaps | ignore; trust `kicad-cli` only |
| Vias placed on tracks | parser read 0 tracks from a KiCad‑saved file (multi‑line format) | never parse `.kicad_pcb` with single‑line regex; dump geometry with `kdump.py` (pcbnew) |
| `GetTracks()` un‑iterable after `Remove()` | SWIG | snapshot lists once, use `Delete()` |
| `SetNet()` seemed to fail | it works; the duplicate vias came from re‑adding the same spots twice | keep an `added` set; dedupe with `kclean.py` |
| Hundreds of annular/drill errors | default project rules (0.3 hole / 0.13 annular) | JLC rules in generator (done) |
| My island detector "fixes" places KiCad considers fine, adds violations, never converges | my pour model ≠ KiCad's connectivity; grid rounding at 0.13 mm clearance | never repair GND by geometry model on 2 layers; use planes. For signals use `kfinish.py` only on nets `kicad-cli` lists, with CLR ≥ 0.2 |
| Dangling‑stub clean‑up eats a net segment by segment | each deletion makes the next piece "dangling" | delete stubs once, then re‑route the affected net whole (`kdelnet.py` + `kfinish.py`) |
| Whole‑net rip‑up cascades (+3V3/I²C broken) | ripping big nets to free one pad | rip only nets with ≤ 6 pads, or delete just the blocking segment (`kdelseg.py`) |
| Fanout vias on other‑side pads | clearance checked on one layer | `clear(..., both=True)` for vias; stub checked on its own layer |
| Full fanout (all 0402s) starves routing on 2 layers | 60+ vias in the sensor cluster | on 2 layers fanout only fine‑pitch ICs; on 4 layers fanout everything |
| Pad excluded from netlist because "on the plane" but fanout failed | plane connectivity assumed | keep failed‑fanout pads in the netlist (`FANOUT_FAIL`) |
| Background job from an earlier attempt overwrites the board | forgot to kill it | `taskkill //F //IM java.exe`, check `ps -W` before rebuilding |
| Heredoc `unexpected EOF` | quotes/backslashes inside bash heredocs | write scripts with the Write tool, run them by path |
| `kicad-cli --refill-zones` unknown | KiCad 8.0 flag doesn't exist (9.0 only) | fill with `pcbnew.ZONE_FILLER` in `kclean.py` |
| pcbnew `GetConnectedItems` TypeError / crash | initializer_list binding; `RecalculateRatsnest` crashes | use `BuildConnectivity()` + DRC JSON; don't rely on the connectivity API |
| `lib_footprint_issues` ×61 | `pcbnew` scripts don't load the project lib table | ignore in pcbnew reports; `kicad-cli` resolves the project library |

## 4. Verification standard

Deliver only when `kicad-cli pcb drc --severity-all` reports **0 violations and 0 unconnected**, with schematic parity checked (`--schematic-parity`; PWR_FLAG "missing footprint" and `unconnected-(…)` net names are benign). Keep `drc_kicad.json`, `routing_preview.png`, the Gerber zip and the doc section in the project folder.

## 5. Time budget (hardware2, 62 parts, 90 routed nets)

Generate + fanout + DSN < 1 min · Freerouting 3–5 min (4 layers) / 10–15 min (2 layers) · pcbnew steps seconds each · kicad-cli DRC ≈ 30 s. Budget one Freerouting run per placement change; never iterate GND islands more than twice — change the placement or the stack‑up instead.
