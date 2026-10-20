#!/usr/bin/env bash
# Restores the Claude Code setup from this repo on a new Ubuntu PC. Run from inside the clone
# (e.g. /home/knight/Claude); the work folders are expected in a sibling folder named Knight.
# Does not touch credentials: log in to Claude Code and gh yourself.
#
#   1. links the self-written skills        (claude-skills/link-skills.sh)
#   2. links the third-party skills         (.agents/skills/* -> .claude/skills)
#   3. copies user-claude/ into ~/.claude   (existing files are backed up as *.bak)
#   4. lets Claude reach the work folders   (permissions.additionalDirectories)
#   5. installs the enabled plugins, if the `claude` CLI is on PATH
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
work="$(dirname "$root")/Knight"
claude_dir="$HOME/.claude"
# Claude Code names a project's memory folder after its path, every non-alphanumeric char -> "-".
mem="$claude_dir/projects/$(printf '%s' "$root" | sed 's/[^A-Za-z0-9]/-/g')/memory"

"$root/claude-skills/link-skills.sh"

mkdir -p "$root/.claude/skills" "$claude_dir" "$mem"
for s in "$root"/.agents/skills/*/; do
    s=${s%/}
    l="$root/.claude/skills/$(basename "$s")"
    if [ ! -e "$l" ] && [ ! -L "$l" ]; then ln -s "$s" "$l"; fi
done

copy() {
    if [ -f "$2" ] && ! cmp -s "$1" "$2"; then cp "$2" "$2.bak"; fi
    cp "$1" "$2"
}
copy "$root/user-claude/settings.json" "$claude_dir/settings.json"
copy "$root/user-claude/statusline-command.sh" "$claude_dir/statusline-command.sh"
copy "$root/user-claude/statusline-command.py" "$claude_dir/statusline-command.py"
while IFS= read -r f; do
    rel=${f#"$root"/user-claude/memory/}
    mkdir -p "$mem/$(dirname "$rel")"
    copy "$f" "$mem/$rel"
done < <(find "$root/user-claude/memory" -type f)

python3 - "$claude_dir/settings.json" "$work" <<'PY'
import json, sys
path, work = sys.argv[1:3]
with open(path, encoding="utf-8") as f:
    settings = json.load(f)
dirs = settings.setdefault("permissions", {}).setdefault("additionalDirectories", [])
if work not in dirs:
    dirs.append(work)
with open(path, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2)
PY

if command -v claude >/dev/null 2>&1; then
    python3 -c 'import json,sys; print("\n".join(k for k,v in json.load(open(sys.argv[1]))["enabledPlugins"].items() if v))' \
        "$claude_dir/settings.json" | while read -r p; do claude plugin install "$p"; done
else
    echo "WARNING: claude CLI not found: install Claude Code, then re-run this script to install plugins." >&2
fi
echo "Done. Log in to Claude Code (/login) and run: gh auth login"
