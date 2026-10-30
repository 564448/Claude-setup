# Domain: high-speed and RF

> Adapted 2026-10-30 from [sequoia-hope/easy_pcb](https://github.com/sequoia-hope/easy_pcb) `.claude/skills/pcb-design/domains/high-speed.md` @ 95bfe5e (MIT, © 2026 Sequoia Alexander). Edit freely; this copy no longer tracks upstream.

Load for USB, Ethernet, DDR, fast QSPI/SDIO, MIPI, HDMI, any RF.

## General

- Impedance-controlled traces on a 4+ layer board with a solid adjacent reference plane.
- Return path continuity: no crossing plane splits; a ground via next to every signal via that changes reference layer.
- Diff pairs: tightly coupled, width/gap from `stackup.md`, length matched within the interface spec, symmetric routing into and out of pads and connectors, minimal vias.
- Series termination near the driver for fast single-ended signals; check whether the interface spec needs termination.
- AC coupling caps and ESD arrays placed per the interface's layout guide, in small packages to limit the discontinuity.
- Follow the chip vendor's layout guide literally and cite it in the part audit.

## Common interfaces

- **USB 2.0 FS/HS**: 90 Ω diff; ESD array rated for HS; short stubs; CC resistors for USB-C.
- **Ethernet**: 100 Ω diff; magnetics placement; isolation gap; Bob Smith termination per PHY guide.
- **QSPI flash**: short, length-matched clock and data; series resistors at the MCU.
- **Crystals**: closest possible to the MCU, guard with ground, no traces underneath on the adjacent layer.

## RF

- 50 Ω coplanar waveguide with ground, via fencing.
- Antenna keepout per module/antenna datasheet (no copper on any layer, no parts), at the board edge.
- Matching network (pi) footprint even if populated with 0 Ω initially.
- Simulate feed and antenna with openEMS for a PCB antenna; otherwise follow the module's reference layout exactly.

## Simulation

2D cross-section solve for every impedance target, confirmed against JLC's calculator. Crosstalk between adjacent pairs and between aggressors and victims. Via transition sim above ~1 GHz content.
