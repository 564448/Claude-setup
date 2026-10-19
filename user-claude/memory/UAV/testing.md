---
name: uav-testing
description: "How to test UAV work — sim with GPS error, video latency and wind, plus real flight video or logs; say where results come from, diff, list what is untested"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5e28ec13-cc72-4d0b-8de5-3757740732cd
  modified: 2026-10-17T09:46:57.535Z
---

- **Test after every change:**
  - The simulation must model real conditions: GPS error or drift, delayed video, wind gusts.
  - Also test against video or logs from real flights.
  - When SITL is available, test in SITL (see [[uav-sitl-ports]]).
- **Say where each result comes from:** simulation, real video, log or SITL.
- **Diff after editing:** confirm only the intended files changed and the backups were not touched.
- **List what is still untested:** especially real flight, and values tuned only in simulation.

**Why:** results from a simulation without errors were much better than real flights, e.g. real GPS caused duplicate targets and 2–3 m offsets, so the user needs to know how much each result can be trusted.

**How to apply:** before reporting any UAV task as done, together with [[uav-work-process]].
