---
name: frontend-design
description: Single entry point for ALL front-end design work: building, redesigning, reviewing or polishing landing pages, product pages, dashboards, app screens and components. Covers colour, type, spacing, layout, depth, imagery, motion, states, copy, accessibility. Decides which installed toolkit leads and which rules win where the toolkits conflict. Use for any web or app UI design task.
---

# Frontend design

Three toolkits are installed on disk but hidden from automatic use. This skill is the only entry point.
Never call them through the Skill tool. Read their files and run their scripts by absolute path.

- **T** (taste): `<setup root>/.claude/skills/design-taste-frontend/` has `SKILL.md`, `references/`, `scripts/` (`draw.mjs`, `inspect.mjs`), `library/`
- **I** (impeccable): `<setup root>/.claude/skills/impeccable/` has `SKILL.md`, `reference/`, `scripts/impeccable`
- **E** (emil): `<setup root>/.agents/skills/animate/SKILL.md`, `emil-design-eng/SKILL.md`, `review-animations/SKILL.md`

## Step 0: resolve the request
1. The user named a toolkit or command (`/impeccable polish`, "use taste"): use only that and skip the rest.
2. New build or existing page? If unclear, ask one question.
3. Mode: **Persuade** (landing, marketing, portfolio) or **Operate/Read** (dashboard, app, settings, docs).

## Step 1: who leads
| Request | Lead | Helpers |
|---|---|---|
| New page, Persuade | T: read its `SKILL.md`, follow its run | I `reference/craft-floor.md` before editing; I `critique` after |
| New screen, Operate/Read | I: `reference/new-work.md`, `shape.md` | T `references/colour.md` for the palette only |
| Existing page, any mode | I: critique, audit, polish, typeset, layout... keep the incumbent identity | none |
| Motion, any mode | E `animate` gate first, then I `reference/animate.md` for the cap | none |

When T leads, run its scripts from the project folder (so `.taste-skill/` lands there), not the setup root.
When I is used, run `scripts/impeccable context` once per session first.

## Step 2: decisions where the toolkits conflict (these win)
1. **Colour:** T's dealt palette and proportions (ground 70-90%, accent under 5%). I `colorize` only on existing pages.
2. **Type size:** Persuade follows T (display may exceed 6rem). Operate/Read follows I (6rem cap, role scale).
3. **Shadows and lines:** Persuade follows T (tone steps, no borders or shadows). Operate/Read follows I (border or shadow, not both; radius 12-16px).
4. **Motion:** E leads. The cap is I's rule: one authored focal moment, not scattered reveals. T's "8 moving elements" floor does not apply.
5. **Direction:** a stated brand or brief wins. Otherwise T deals 3 directions and the user picks.
6. **Source of truth:** `DESIGN.md` holds palette and fonts. T's direction sheet only feeds it at the start.
7. **Review loop:** on a T-built page run T `inspect.mjs` first, then I `critique`. Never run `quieter` or `polish` over a T build.
8. **Drawn imagery:** only when no real or open-collection picture exists. Flat shapes in palette colours. No sketch/doodle style, no `feTurbulence` grain, no gradients.

## Step 3: inspector
`node <T>\scripts\inspect.mjs <target> --allow <ids>`
Allow only what Step 2 requires: `still-page` (decision 4), and `shadow`, `heavy-shadow`, `outlined-box` in Operate/Read (decision 3).
Never allow `gradient`, `gradient-text`, `emoji`, `eyebrow`. List every allowed rule in the report.

## Step 4: subtopic -> read this
Colour: T `references/colour.md`. Type: I `reference/typeset.md`. Spacing/layout: I `reference/layout.md`.
Depth: T `references/colour.md` s4 + I `reference/craft-floor.md`. Imagery: T `references/imagery.md`.
Motion: E `animate/SKILL.md`. States/robustness/a11y: I `craft-floor.md`, `harden.md`, `audit.md`.
Copy: Persuade T `references/copy.md`; UI text I `reference/clarify.md`. Review: I `critique.md`, `polish.md`.
Tone: I `bolder.md`, `quieter.md`. Native: I `ios.md`, `android.md`. Full 24-row map: `references/subtopics.md`.

## Rules
- Ask before creating or editing `PRODUCT.md` or `DESIGN.md`, and create them inside the project folder, never the setup root.
- Do not turn on I's hooks. Do not run `impeccable init` unless asked.
- Before UI edits, read I `reference/craft-floor.md`. Report which toolkit led and which rules were waived.
