---
name: pcb-design
description: Combined KiCad workflow — use kicad-mcp for live, interactive board inspection/editing in KiCad 9 (move parts, add traces, check nets, see changes appear instantly with undo), and the pcb-autoroute headless pipeline for bulk autorouting and DRC-cleanup (placement generator → Specctra DSN → Freerouting → pcbnew scripting → kicad-cli DRC → Gerbers). Use when asked to design, route, fix, or inspect a KiCad board. Pick the live tools for small interactive edits and inspection; pick the headless pipeline for full-board autorouting or when the GUI isn't open.
---

# PCB design: live editing + headless autorouting

This skill combines two things that solve different problems on the same board and are meant to be used together, not as alternatives:

- **kicad-mcp** (MCP server `kicad`, registered at user scope) — talks to a *running* KiCad 9 instance over its IPC API. Use it for anything interactive: inspecting footprints/nets/connections, nudging or rotating parts, adding a trace, refilling a zone, saving — with full undo, visible instantly in the open GUI.
- **pcb-autoroute pipeline** (`../pcb-autoroute/`, scripts + Freerouting jar) — a headless, scripted pipeline for turning a placed board into a fully-routed, DRC-clean one. No GUI required. This is the tool for "route the whole board" or "why does DRC still show violations," not for single edits.

## When to use which

| Task | Tool |
|---|---|
| "Is net X connected?" / "show me all footprints on the back" | kicad-mcp (live inspection) |
| "Move U3 2mm left and rotate it 90°" | kicad-mcp (live edit) |
| "Route the crystal load caps to Y1" (a couple of nets) | kicad-mcp (live edit, add_trace) |
| "Route the whole board" / "make the PCB" / "fix DRC" | pcb-autoroute pipeline (headless, `scripts/` in that skill) |
| Board isn't open in KiCad, or KiCad isn't running | pcb-autoroute pipeline only (kicad-mcp needs a live connection) |

A common flow: use kicad-mcp to place/arrange parts and eyeball the layout live, then hand off to the pcb-autoroute pipeline for bulk routing + DRC, then reopen in KiCad (kicad-mcp) to inspect the routed result and hand-fix anything DRC still flags.

## kicad-mcp setup notes

- Requires **KiCad 9** with the IPC API server enabled: Preferences → Plugins → KiCad API Server.
- Registered as a user-scoped MCP server (`claude mcp add -s user kicad ...`), installed at `C:\Knight\Project\tools\kicad-mcp`, running under a pinned Python 3.12 venv (`uv run --python 3.12`) — Python 3.14 was the system default but has no prebuilt `pynng` wheel yet (would require cmake to build from source, which isn't installed).
- Connects to KiCad's local IPC socket. On Windows the exact transport differs from the `/tmp/kicad/api.sock` path used on Linux/macOS — if the connection fails, check the KiCad API Server preference pane for the actual endpoint it's listening on.
- Marked experimental by its authors (Netlist-Studio) — sanity-check destructive edits (deletions, whole-net rip-ups) before trusting them blindly, same as with any board edit.
- If KiCad is restarted or you switch projects/boards, calls may briefly fail with `the provided kicad_token did not match this KiCad instance's token` (a stale auth token from a prior KiCad process). It has resolved itself on retry without needing a full Claude Code restart — just retry the call (e.g. `ping`) once or twice before assuming the connection is broken.
- Calls also fail with `no handler available for request of type ... GetOpenDocuments` if KiCad is running but no board is actually open in the **PCB Editor window** itself (project manager alone isn't enough).

## pcb-autoroute pipeline notes

Full details, failure catalogue, and stack-up/placement rules live in `../pcb-autoroute/SKILL.md` — read that before running the pipeline. Key things carried over here:

- Built and verified against **KiCad 8**. It works around KiCad-8-specific gaps (e.g. `kicad-cli --refill-zones` doesn't exist until 9.0, so it fills zones via `pcbnew.ZONE_FILLER` in `kclean.py` instead). If you're now on KiCad 9, some of those workarounds may be unnecessary or may need adjusting — this hasn't been verified on 9 yet. Treat any KiCad-9 run as a first-time trial: watch for behavior changes in the pcbnew scripting API and re-confirm the DRC/Gerber steps still work as expected.
- `kicad-cli pcb drc --severity-all` is the *only* authority on correctness — never trust Freerouting's own violation count or a pcbnew connectivity check.
- Scripts and Freerouting/JRE binaries live in `../pcb-autoroute/scripts/` and `../pcb-autoroute/tools/` — invoke them from there rather than copying them into this skill.
