---
name: uav-pilot-override
description: UAV safety rule — the pilot holds the RC and may change mode at any time; the program must never take the mode back and must abort by itself when the mode changes
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5e28ec13-cc72-4d0b-8de5-3757740732cd
  modified: 2026-10-17T09:46:54.056Z
---

The pilot holds the RC and may change mode at any time. The program (GCS or on board) must never switch the mode back against the pilot.
If the mode changes away from the one the program is using (e.g. the pilot switches to POSHOLD / ALT_HOLD / STABILIZE), abort at once and send no further movement commands.

**Why:** the program normally flies on its own, but in an emergency the pilot must be able to take the aircraft back immediately without the program fighting back.

**How to apply:** every piece of code that sets a mode or commands movement must check the current mode before each command, and there must be a test for the pilot taking over (see [[uav-testing]]).
