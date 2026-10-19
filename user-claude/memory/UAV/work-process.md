---
name: uav-work-process
description: "How to work with the user on UAV tasks — explain before acting, work in a copy, wait before touching hardware, push back, keep docs up to date"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5e28ec13-cc72-4d0b-8de5-3757740732cd
  modified: 2026-10-17T09:46:51.211Z
---

- **Explain before acting:** when the user says "read it but don't do it yet" or "explain so we agree", summarize the task and the method first, then wait for "ยืนยัน" (confirm) before editing.
- **Never edit the original:** work in a copy folder and back up before editing. Edit only the folder the user named as the working one; ask if unsure which.
- **Wait before touching hardware:** uploading to the Pi, commanding servos, setting params or moving the gimbal only after the user says the hardware is connected. Never set a program to start at boot without discussing it first.
- **Push back:** if the user's guess doesn't match the evidence, say so plainly.
- **Keep docs up to date:** after a code change, update the related docs (PREFLIGHT_COMMANDS, README) to match.

**Why:** this is real flight work with equipment and safety at stake, so the user must agree before changes, a flyable backup must always exist, and hardware may only be commanded while the user is at the aircraft.

**How to apply:** for every UAV task, together with [[uav-pilot-override]] and [[uav-testing]].
