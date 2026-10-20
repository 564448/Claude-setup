# Claude-setup (Linux branch)

Personal Claude Code setup for Ubuntu: CLAUDE.md, self-written skills, third-party skills,
hooks, and user-level settings/memory. Private repo. The Windows setup is on the `Windows` branch.

## Restore on a new Ubuntu PC
Expected layout: Claude runs from `/home/knight/Claude` (this repo); the work folders
`TaughtMe/`, `CS/` and `Project/` sit in `/home/knight/Knight`.

1. Install git, GitHub CLI (`gh`), python3 and Claude Code. Run `gh auth login`.
2. `git clone -b Linux https://github.com/564448/Claude-setup /home/knight/Claude`
3. Copy your work folders into `/home/knight/Knight`. Skip `Project/claude-skills`: the skills come from this repo.
4. `bash /home/knight/Claude/bootstrap.sh`
5. Start Claude Code in `/home/knight/Claude` and run /login.

(For Claude: just follow these steps and report any error.)

## Layout
- CLAUDE.md, skills-lock.json, .agents/ – workspace rules and third-party skills
- .claude/ – project settings and hooks (python3)
- claude-skills/ – self-written skills (see its README.md)
- user-claude/ – copies of ~/.claude settings, statusline and memory

## Not included
- Credentials, history, sessions, settings.local.json, and the work folders (CS, Project, TaughtMe).
- Windows-only tooling kept on `Windows`: pcb-autoroute, pcb-design, remote_vm_kali, the nkrafa-* agents and /Review_NKRAFA_report.
- `report-format-check` is included, but its reference report (`CS/รายงานพี่แซ่บ.docx`) must be copied over with your CS folder.
- `remote-pi-min` needs your SSH key for the Pi in `~/.ssh`.

## Refresh the user-level copies after changing them
Copy ~/.claude/settings.json, statusline-command.sh, statusline-command.py and projects/<setup-path-with-dashes>/memory/* into user-claude/, then commit.