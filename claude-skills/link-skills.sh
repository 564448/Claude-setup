#!/usr/bin/env bash
# Links every shippable skill in this repo into the folder Claude Code loads it from.
# Claude Code only discovers skills one level deep (<skills-dir>/<name>/SKILL.md), so the
# bucketed layout here (skills/<bucket>/<name>/) is flattened with symlinks.
#
#   general/     -> ~/.claude/skills          (user scope: available in every folder)
#   cs/          -> <setup root>/.claude/skills
#   project/     -> <setup root>/.claude/skills
#   in-progress/, deprecated/ -> not linked
#
# Also removes stale links that point into this repo but no longer match a shippable skill.
# Real folders are never deleted. Usage: ./link-skills.sh [--dry-run]
set -euo pipefail

dry=0
[ "${1:-}" = "--dry-run" ] && dry=1
run() { if [ "$dry" = 1 ]; then echo "would $*"; else "$@"; fi; }

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
root=$(cd "$repo/.." && pwd)

declare -A dest=([general]="$HOME/.claude/skills" [cs]="$root/.claude/skills" [project]="$root/.claude/skills")
declare -A src bucket

# Collect shippable skills and refuse duplicate names (flattening would make one silently win).
for b in "${!dest[@]}"; do
    for d in "$repo/skills/$b"/*/; do
        [ -f "${d}SKILL.md" ] || continue
        d=${d%/}
        n=$(basename "$d")
        if [ -n "${src[$n]:-}" ]; then
            echo "Duplicate skill name '$n' in skills/$b and skills/${bucket[$n]}" >&2
            exit 1
        fi
        src[$n]=$d
        bucket[$n]=$b
    done
done

for n in $(printf '%s\n' "${!src[@]}" | sort); do
    t="${dest[${bucket[$n]}]}/$n"
    if [ -L "$t" ]; then
        if [ "$(readlink "$t")" = "${src[$n]}" ]; then echo "ok      $n"; continue; fi
        run rm "$t"
    elif [ -e "$t" ]; then
        echo "skip $n: $t is a real folder, not a link. Move it into the repo or delete it, then re-run." >&2
        continue
    fi
    run mkdir -p "$(dirname "$t")"
    run ln -s "${src[$n]}" "$t"
    [ "$dry" = 1 ] || echo "linked  $n -> skills/${bucket[$n]}/$n"
done

# Prune links into this repo that are no longer shippable.
for dir in $(printf '%s\n' "${dest[@]}" | sort -u); do
    [ -d "$dir" ] || continue
    for l in "$dir"/*; do
        [ -L "$l" ] || continue
        t=$(readlink "$l")
        case "$t" in "$repo"/*) ;; *) continue ;; esac
        n=$(basename "$l")
        if [ -z "${src[$n]:-}" ] || [ "${src[$n]}" != "$t" ] || [ "${dest[${bucket[$n]}]}" != "$dir" ]; then
            run rm "$l"
            echo "pruned  $l (was -> $t)"
        fi
    done
done
