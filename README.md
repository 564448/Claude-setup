# Claude-setup

Personal Claude Code setup for Windows: CLAUDE.md, self-written skills, third-party skills,
agents, commands, hooks, and user-level settings/memory. Private repo.

## Restore on a new Windows PC
Expected layout: Claude runs from `C:\Knight\Claude` (this repo, the setup root); the work folders
`ClaudeTaughtMe\`, `CS\` and `Project\` sit in `C:\Knight` (the work root).

1. Install git, GitHub CLI (gh), Node, Claude Code. Run `gh auth login`.
2. `git clone https://github.com/564448/Claude-setup C:\Knight\Claude`
3. Copy your work folders into `C:\Knight`.
4. `powershell -ExecutionPolicy Bypass -File C:\Knight\Claude\bootstrap.ps1`
5. Start Claude Code in C:\Knight\Claude and run /login.

(For Claude: just follow these steps and report any error.)

## Layout
- CLAUDE.md, skills-lock.json, .agents/ – workspace rules and third-party skills
- .claude/ – agents, commands, hooks, project settings
- claude-skills/ – self-written skills (see its README.md)
- user-claude/ – copies of ~/.claude settings, statusline and memory

## Not included
Credentials, history, sessions, settings.local.json, the work folders (CS, Project, ClaudeTaughtMe),
and pcb-autoroute's freerouting.jar and JRE zip (see claude-skills/skills/project/pcb-autoroute/tools/README.txt).

## Refresh the user-level copies after changing them
Copy ~/.claude/settings.json, statusline-command.sh, statusline-command.py and projects/C--Knight-Claude/memory/* into user-claude/, then commit.
