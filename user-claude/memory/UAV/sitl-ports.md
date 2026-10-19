---
name: uav-sitl-ports
description: "SITL MAVLink ports on this machine — udp 127.0.0.1:14000 for the GUI, udp 127.0.0.1:15000 for Claude to control the vehicle"
metadata:
  node_type: memory
  type: reference
  originSessionId: 5e28ec13-cc72-4d0b-8de5-3757740732cd
  modified: 2026-10-17T09:46:59.717Z
---

When the user starts SITL:
- `udp 127.0.0.1:14000`: for the GCS GUI
- `udp 127.0.0.1:15000`: for Claude to control or read the vehicle

Connection data for the real aircraft (IP, COM, video port) differs per machine and changes often. Don't store it; ask the user each time.

Used when testing per [[uav-testing]].
