---
name: skill-intake
description: Evaluate an outside Claude Code skill, plugin or MCP server against this setup, then install or fork it only after the user picks how. Invoked by the user as /skill-intake <link or name> [install method].
disable-model-invocation: true
license: MIT
---

# Skill Intake

> Written 2026-10-15 from the steps used to evaluate obra/superpowers, thananon/9arm-skills `debug-mantra`, mksglu/context-mode and mattpocock/skills `grill-me` in one session.

**Arguments:** `$ARGUMENTS`

## 0. Check the arguments

The first argument must be a link (GitHub repo, file, marketplace page, install command) or a skill/plugin name. Anything after it is the install method the user already chose (e.g. `fork`, `npx`, `plugin`, `mcp-only`, `no`).

If there is no link or name, reply only with this, in the user's language, and stop:

> **[Invalid command]** add a link or skill name, e.g. `/skill-intake https://github.com/<owner>/<repo>` or `/skill-intake grill-me fork`

Don't fall back to a link or name from earlier in the conversation.

## Phase A: Evaluate (always)

### A1. Read the real source
- Only a name: find the repo with a web search first.
- Read the actual files, not a summary or a third-party listing. Those often disagree with the repo.
  - Tree: `gh api repos/<o>/<r>/git/trees/<branch>?recursive=1 --jq '.tree[].path'`
  - File: `gh api repos/<o>/<r>/contents/<path> -H "Accept: application/vnd.github.raw"`
- Record: `LICENSE` (exact type), current commit sha, the files the target depends on (e.g. `grill-me` only loads `grilling`), stars and notable criticism.
- **Skills:** frontmatter (`description`, `disable-model-invocation`), body, referenced files.
- **Plugins / MCP servers:** hooks and which tools they intercept, anything injected every session (SessionStart, CLAUDE.md edits), MCP tools, runtime needs (Node/Bun version, native deps, Windows support).

### A2. Explain how it works
Mechanism step by step, and **when it runs**: on demand by the user, chosen by the model from its description, or always on (hooks / SessionStart).

### A3. Compare with this setup
Read before judging:
- `C:\Knight\CLAUDE.md`
- `C:\Knight\Project\claude-skills\README.md` (index of every skill, agent, command, plugin)
- every own skill that could overlap or conflict (e.g. `coding-guidelines`, `root-cause-debugging`, `verification-before-completion`)
- `~/.claude/settings.json` (`enabledPlugins`) and the facts the target needs (`node --version`, whether the folder is a git repo, …)

Put overlaps and conflicts in a table: existing rule or skill → where the target overlaps or clashes.

Main risk test: **does it force itself into every session?** Always-on (hooks, SessionStart, auto-routing) is high risk. User-invoked is low risk.

### A4. Report
Start with one summary line:

> **[skill-intake]** `<name>` (`<license>`, `<when it runs>`)

Then: what it does, how it works, overlap/conflict table, and a recommendation in tiers by risk (e.g. don't install / partial such as MCP-only / full / fork), with how to turn it off again. End with a `Sources:` list of links.

**Stop and ask which tier to take.** Don't install anything in phase A.

If the user already gave an install method in the arguments, skip the question and go to phase B after the report, **unless** the report found a blocker (e.g. `fork` requested but there's no license, or a hard conflict with an own skill). Then warn and wait.

## Phase B: Install (only the method the user chose)

### B1. Pick the method by license

| Case | Method |
|---|---|
| MIT or another license that allows modification, and the user wants to own it | Fork into `Project/claude-skills/skills/<bucket>/<name>/` |
| No license | Ideas only. Write it yourself, copy no text, and say so in the file |
| `npx skills` | Stays in `C:\Knight\.agents\skills` + `skills-lock.json`. Never move it. Index row only |
| Plugin / MCP server | Install where it lives (`/plugin …`, `claude mcp add …`). Index row only |
| Source-available (e.g. ELv2) | Use it as is. Don't fork |

### B2. Fork / write
Follow `Project/claude-skills/CLAUDE.md`.
- Bucket by purpose (`general`, `cs`, `project`). Ask if unclear. The name must be unique across all buckets.
- Frontmatter: add `license:`. Keep `description` and `disable-model-invocation` as upstream unless the user asks otherwise.
- First line after the frontmatter is a fork note: `> Forked <date> from [<owner>/<repo>](<url>) \`<path>\` @ <sha> (<license>, © <year> <holder>). Edit freely; this copy no longer tracks upstream.`
- Body: keep it unchanged unless the user asked for changes (merge sources, drop domain-specific parts into their domain skill, add a marker).
- Fork every file the target depends on (e.g. `grilling` together with `grill-me`).

### B3. Register
- One row in the matching table of `Project/claude-skills/README.md` (Own skills, or Third-party for npx/plugin).
- For own skills, also an entry in the bucket `README.md` with the longer notes and the fork source.
- Run `Project/claude-skills/link-skills.ps1` and read its output.
- If the fork duplicates an installed plugin, set it to `false` in `enabledPlugins` so it doesn't load twice.
- Only add to `C:\Knight\CLAUDE.md` if the user asks. Fit it to the existing structure, and name a skill the model can invoke (not one with `disable-model-invocation: true`).

### B4. Verify and summarize
Run `verification-before-completion`. Typical checks:
- body diff against upstream (if unchanged)
- junction in `~/.claude/skills` points to the repo folder
- exactly one index entry per README
- the skill appears in the available-skills list (user-invoked skills won't; mark that as unverified and say how to test it)
- edited files are still UTF-8

Then give the end-of-task summary with the **[Verified]** block.
