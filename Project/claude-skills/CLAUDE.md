Self-written Claude Code skills live in bucket folders under `skills/`:

- `general/`: useful in any folder, so it is linked into `~/.claude/skills` (user scope)
- `cs/`: tied to coursework / an academic pipeline, linked into `C:\Knight\.claude\skills`
- `project/`: for building a personal project, linked into `C:\Knight\.claude\skills`
- `in-progress/`: drafts, not linked
- `deprecated/`: retired, not linked

Pick the bucket by the skill's *purpose*. If it doesn't clearly fit one, ask.

After creating, moving, renaming or deleting a skill, run `.\link-skills.ps1` (PowerShell) and check its output. Never edit a skill through its junction path in `.claude\skills`. Edit the file in this repo.

Every skill in `general/`, `cs/` or `project/` must have:
1. a row in the "Own skills" table of the top-level `README.md`, with the name linked to its `SKILL.md`
2. an entry in its bucket's `README.md`, with the name linked to `./<name>/SKILL.md` and the longer notes

Skills in `in-progress/` and `deprecated/` appear only in their bucket README, never in the top-level index.

Third-party skills (`npx skills` → `C:\Knight\.agents\skills` + `skills-lock.json`, or plugins), built-in skills, agents and commands are **not moved into this repo**. They only get a row in the matching table of the top-level `README.md`.

Skill names must be unique across all buckets, because linking flattens them. `link-skills.ps1` refuses duplicates.
