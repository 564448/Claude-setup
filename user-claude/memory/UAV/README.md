---
name: uav-index
description: "Index of UAV memories (drone, GCS, ArduPilot, SITL) — open this first, then read only the files that apply to the task"
metadata:
  node_type: memory
  type: reference
  originSessionId: 5e28ec13-cc72-4d0b-8de5-3757740732cd
  modified: 2026-10-17T09:46:47.044Z
---

This folder holds every memory about UAV work. It keeps only overall working guidelines, not mission details, which change with each mission and can be read from the code.

Update the list below whenever a file in this folder is added, edited or deleted.

- [[uav-work-process]] (`work-process.md`): explain before acting, work in a copy, wait for the go-ahead before touching hardware, push back when evidence disagrees, keep docs up to date
- [[uav-pilot-override]] (`pilot-override.md`): the pilot can change mode at any time; the program must abort by itself when the mode changes
- [[uav-testing]] (`testing.md`): test with a realistic sim and real flight data, say where each result comes from, diff, list what is still untested
- [[uav-sitl-ports]] (`sitl-ports.md`): SITL MAVLink ports: 14000 for the GUI, 15000 for Claude
