# KiCad tooling: live (kicad-mcp) and command line

> Live-editing notes are own material. The automation-surface list is adapted 2026-10-30 from [sequoia-hope/easy_pcb](https://github.com/sequoia-hope/easy_pcb) `.claude/skills/pcb-design/tools/kicad.md` @ 95bfe5e (MIT, © 2026 Sequoia Alexander). Edit freely; this copy no longer tracks upstream.

Check the installed version first (`kicad-cli version`); APIs and file formats differ between 8, 9 and 10. This machine: KiCad **9.0**.

## Automation surfaces

- **`kicad-cli`**: ERC, DRC (`kicad-cli pcb drc --severity-all --format json`), exports (schematic PDF/SVG, gerbers, drill, BOM, CPL, STEP, 3D renders on recent versions). Use it for every check and export, and paste its output into gate files.
- **kicad-mcp** (live, below): inspect and edit a board open in the GUI, with undo.
- **`pcbnew` Python** (KiCad's own interpreter): placement, zones, via arrays, net classes, footprint edits. This is what `../scripts/k*.py` use.
- **File formats**: `.kicad_sch` / `.kicad_pcb` are S-expressions. Parsing them directly is fine for read-only checks. For writes, prefer an API; if editing files directly, use a proper S-expression library, preserve UUIDs, and re-open in KiCad to validate. Never parse with single-line regexes (see the failure catalogue).
- **Custom DRC rules**: `.kicad_dru` file with net class and area conditions. Put every derived rule there with a comment citing its source.
- **Freerouting** for autorouting: see `routing.md` (governed run) and `headless-pipeline.md`.
- **Image converter / bitmap2component** for silk art.
- **JLC**: use the JLC fields (`LCSC`) on symbols and a rotation correction (per-part rotation offset field or the JLCPCB fabrication plugin) for CPL.

## Schematic authoring by script

The coordinates are the design. Plan the layout per block first (a sketch in the gate file: which symbols where, left to right), then place symbols at those positions on the 1.27 mm (50 mil) grid, then wires. Never place symbols in a loop over a list with a fixed x/y step: that is what produces the grid look.

## Board-local footprint edits

Copy the footprint into a project library (`<project>/lib/<project>.pretty`), edit, and re-link the symbol's footprint field in the schematic (schematic remains source of truth). Note it in `decisions.md`.

## kicad-mcp (live editing) setup notes

Use it for anything interactive: inspecting footprints/nets/connections, nudging or rotating parts, adding a trace, refilling a zone, saving, with full undo, visible instantly in the open GUI.

- Requires **KiCad 9** with the IPC API server enabled: Preferences → Plugins → KiCad API Server.
- Registered as a user-scoped MCP server (`claude mcp add -s user kicad ...`), installed at `C:\Knight\Project\tools\kicad-mcp`, running under a pinned Python 3.12 venv (`uv run --python 3.12`). Python 3.14 is the system default but has no prebuilt `pynng` wheel (would need cmake to build from source, which isn't installed).
- Connects to KiCad's local IPC socket. On Windows the transport differs from the `/tmp/kicad/api.sock` path used on Linux/macOS. If the connection fails, check the KiCad API Server preference pane for the actual endpoint.
- Marked experimental by its authors (Netlist-Studio). Sanity-check destructive edits (deletions, whole-net rip-ups) before trusting them.
- After a KiCad restart or a board switch, calls may briefly fail with `the provided kicad_token did not match this KiCad instance's token` (stale auth token). Retry (e.g. `ping`) once or twice before assuming the connection is broken.
- Calls also fail with `no handler available for request of type ... GetOpenDocuments` if KiCad is running but no board is open in the **PCB Editor window** itself (the project manager alone isn't enough).
