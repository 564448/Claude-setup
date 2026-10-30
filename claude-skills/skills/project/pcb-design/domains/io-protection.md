# Domain: I/O protection

> Adapted 2026-10-30 from [sequoia-hope/easy_pcb](https://github.com/sequoia-hope/easy_pcb) `.claude/skills/pcb-design/domains/io-protection.md` @ 95bfe5e (MIT, © 2026 Sequoia Alexander). Edit freely; this copy no longer tracks upstream.

Load for any board with connectors to the outside world (almost all of them).

## For every external connector (from `intent.md`)

Ask: what's the worst thing that could be plugged in, touched or shorted here? Then protect against it.

- **ESD**: TVS diode on every signal and power pin that goes off-board, placed **right at the connector**, before anything else, with a short, wide path to ground. Choose by working voltage (standoff ≥ max normal signal), clamp voltage (below downstream abs max at the expected current) and capacitance (low for high-speed lines; USB and Ethernet need arrays rated for that speed).
- **Power input**: reverse polarity (P-FET ideal diode, series Schottky for low current, or diode + fuse); overvoltage/surge TVS (load dump, inductive kicks); fuse or eFuse; inrush limiting for big bulk caps; hot-plug ringing on long cables (bulk electrolytic damping).
- **Signal lines**: series resistor for current limiting into ESD clamps and MCU pins; consider 12 V or 24 V accidentally connected to a logic pin (miswired harness).
- **Shorts**: outputs that can be shorted to ground or supply should survive (current limit, PTC, short-circuit-protected driver).
- **Buses** (CAN, RS-485): bus-specific protection, common-mode chokes, split termination.
- **Shield and chassis**: connector shell to ground via the right path (direct, RC, or isolated); decide and log.

## Layout

- Protection parts between the connector pins and everything else, so the surge sees the TVS first.
- Short, low-inductance ground path from TVS to the plane (multiple vias).
- Keep unprotected traces from the connector short and away from internal circuits.

## Silkscreen

Each connector's label includes ratings from `intent.md`, and any lack of protection the user should know about.
