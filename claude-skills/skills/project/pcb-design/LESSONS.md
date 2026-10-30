# Lessons

Corrections the user has had to give. Each is a rule. Read this at the start of every PCB session. When the user corrects something, add the rule here in the same turn.

Format: `- [area] What went wrong → what to do instead.`

> The first ten rules are adapted 2026-10-30 from [sequoia-hope/easy_pcb](https://github.com/sequoia-hope/easy_pcb) `.claude/skills/pcb-design/LESSONS.md` @ 95bfe5e (MIT, © 2026 Sequoia Alexander); they were that author's corrections, not this user's. Keep, change or drop them as this user's own corrections come in. The CanSat-specific lessons live in `references/headless-pipeline.md` §4.

- [schematic] Symbols placed on a grid and connected with global labels → group by function, arrange in signal-flow order, connect with wires within a block, labels only between blocks or sheets.
- [schematic] Inputs and outputs scattered around symbols → inputs left, outputs right, power top, ground bottom; edit the symbol for this project if the library one fights this.
- [placement] ICs placed, then all passives dumped in a linear row → each passive placed with the pin it serves, in the order the datasheet layout guide implies.
- [routing] Manually routing long traces by picking coordinates → pours/planes for power, short critical routes enabled by placement, autorouter for the rest.
- [power] Single via carrying a high-current net (e.g. motor bridge) → via arrays sized by calculation.
- [sync] Part numbers changed in the PCB or schematic without the other → schematic is the source of truth; run the sync check at every gate.
- [silkscreen] Designators under parts, chopped by vias, or overlapping → every designator visible, adjacent to its part, clear of vias, pads and other silk.
- [silkscreen] Connectors with no explanation → every connector labeled with function, polarity and rating (e.g. "+ −  12 V DC MAX").
- [datasheets] Parts chosen without reading the datasheet's fine print (e.g. bulk cap ripple current on BLDC controllers) → full datasheet audit per part, calculations recomputed independently.
- [process] A later board variant tacked on with less polish than the first → treat every variant as its own folder with its own gates.
