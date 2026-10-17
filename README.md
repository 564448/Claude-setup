# Claude-setup

Personal Claude Code setup for `C:\Knight`: CLAUDE.md, self-written skills, third-party skills,
agents, commands, hooks, and user-level settings/memory. Private repo.

## Restore on a new Windows PC
1. Install git, GitHub CLI (gh), Node, Claude Code. Run `gh auth login`.
2. `git clone https://github.com/564448/Claude-setup C:\Knight`  (path must be C:\Knight)
3. `powershell -ExecutionPolicy Bypass -File C:\Knight\bootstrap.ps1`
4. Start Claude Code in C:\Knight and run /login.

(For Claude: just follow these four steps and report any error.)

## Layout
- CLAUDE.md, skills-lock.json, .agents/ – workspace rules and third-party skills
- .claude/ – agents, commands, hooks, project settings
- Project/claude-skills/ – self-written skills (see its README.md)
- user-claude/ – copies of ~/.claude settings, statusline and memory

## Not included
Credentials, history, sessions, settings.local.json, the rest of C:\Knight (CS, Project, ClaudeTaughtMe),
and pcb-autoroute's freerouting.jar and JRE zip (see Project/claude-skills/skills/project/pcb-autoroute/tools/README.txt).

## Refresh the user-level copies after changing them
Copy ~/.claude/settings.json, statusline-command.sh and projects/C--Knight/memory/* into user-claude/, then commit.
