# My Claude Skills & Agents — General Tooling Knowledge

These are the skills and agents I have available in Claude Code that are about the tool itself — configuration, automation, and reference knowledge — rather than tied to a specific coursework subject or project.

## Skills

### `claude-api`
Reference for the Claude API / Anthropic SDK: model IDs, pricing, parameters, streaming, tool use, MCP, agents, prompt caching, token counting, and model migration guidance.

### `keybindings-help`
Used to customize keyboard shortcuts, rebind keys, add chord bindings, or edit `~/.claude/keybindings.json`.

### `update-config`
Configures the Claude Code harness via `settings.json` — hooks (automated "when X happens" behaviors), permissions, environment variables. Automated behaviors require hooks configured here; they can't be fulfilled through memory or preferences alone.

### `loop`
Runs a prompt or slash command on a recurring interval (e.g. `/loop 5m /foo`), or self-paces if no interval is given. Used for recurring tasks or polling, not one-off work.

### `schedule`
Creates, updates, lists, or runs scheduled cloud agents (routines) that execute on a cron schedule — for recurring automated agents or one-time scheduled runs.

### `upload-to-github`
Preps a folder/project for GitHub and uploads it: static code checks, README generation, `.gitignore` + `LICENSE` (checking upstream licenses when the code is derived from another project), then pushes to a new or existing repo via `gh`. Always confirms before the actual push.

### `andrej-karpathy-skills:karpathy-guidelines`
Behavioral guidelines to reduce common LLM coding mistakes, derived from Andrej Karpathy's observations. **Mandatory: use this skill any time a program/code is being written.** Surfaces assumptions, keeps changes minimal and surgical, and defines verifiable success criteria before/after coding.

### `emilkowalski/skills` (installed via `npx skills@latest add`)
UI/animation "taste" skills from Emil Kowalski (Vercel/Linear, creator of Sonner/Vaul), installed at the root of `C:\Knight` (`.agents\skills\`). Covers `animate`, `animation-vocabulary`, `apple-design`, `emil-design-eng`, `find-animation-opportunities`, `improve-animations`, `pick-ui-library`, `prototype`, `review-animations` — see full breakdown in [`Project/skills-and-agents/README.md`](../../Project/skills-and-agents/README.md).

## Agents

### `claude` (catch-all)
Default agent for any task that doesn't fit a more specific agent.

### `claude-code-guide`
Answers questions about Claude Code itself (the CLI, hooks, slash commands, MCP servers, settings, IDE integrations, keyboard shortcuts), the Claude Agent SDK, the Claude API, and Claude Tag (Claude in Slack).

### `statusline-setup`
Configures the Claude Code status line setting.

## Note

This folder is documentation about my own available tooling — written the same way as [`9arm-skills-summary.md`](../9arm-skills-summary.md), which covers a third-party skills repo for comparison.
