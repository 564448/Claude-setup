#!/bin/bash
# Claude Code statusline: shows 5-hour and 7-day rate limit usage as percentages
# and reset times.

input=$(cat)

RESET='\033[0m'
DIM='\033[2m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'

color_for() {
  local pct_int=$1
  if [ "$pct_int" -ge 80 ]; then
    printf '%s' "$RED"
  elif [ "$pct_int" -ge 50 ]; then
    printf '%s' "$YELLOW"
  else
    printf '%s' "$GREEN"
  fi
}

fmt_reset() {
  local ts=$1
  local out
  out=$(date -d "@$ts" "+%a %H:%M" 2>/dev/null)
  if [ -z "$out" ]; then
    out=$(date -r "$ts" "+%a %H:%M" 2>/dev/null)
  fi
  printf '%s' "$out"
}

jq() {
  python3 -c '
import json, sys
data = json.load(sys.stdin)
path = sys.argv[1].split(".")[1:]
cur = data
try:
    for key in path:
        cur = cur[key]
    if cur is None:
        raise KeyError
    print(cur)
except (KeyError, TypeError):
    pass
' "$1"
}

five_pct=$(printf '%s' "$input" | jq '.rate_limits.five_hour.used_percentage')
five_reset=$(printf '%s' "$input" | jq '.rate_limits.five_hour.resets_at')
week_pct=$(printf '%s' "$input" | jq '.rate_limits.seven_day.used_percentage')
week_reset=$(printf '%s' "$input" | jq '.rate_limits.seven_day.resets_at')

segments=()

if [ -n "$five_pct" ]; then
  five_int=$(printf '%.0f' "$five_pct")
  five_color=$(color_for "$five_int")
  five_reset_fmt=$(fmt_reset "$five_reset")
  seg="${DIM}5h${RESET} ${five_color}${five_int}%${RESET}"
  if [ -n "$five_reset_fmt" ]; then
    seg="${seg} ${DIM}(resets ${five_reset_fmt})${RESET}"
  fi
  segments+=("$seg")
fi

if [ -n "$week_pct" ]; then
  week_int=$(printf '%.0f' "$week_pct")
  week_color=$(color_for "$week_int")
  week_reset_fmt=$(fmt_reset "$week_reset")
  seg="${DIM}7d${RESET} ${week_color}${week_int}%${RESET}"
  if [ -n "$week_reset_fmt" ]; then
    seg="${seg} ${DIM}(resets ${week_reset_fmt})${RESET}"
  fi
  segments+=("$seg")
fi

ctx_pct=$(printf '%s' "$input" | jq '.context_window.used_percentage')

if [ "${#segments[@]}" -eq 0 ]; then
  out="${DIM}No rate limit data available yet${RESET}"
else
  out=""
  for i in "${!segments[@]}"; do
    if [ "$i" -gt 0 ]; then
      out="${out}${DIM} | ${RESET}"
    fi
    out="${out}${segments[$i]}"
  done
fi

# Context window usage, right-aligned to the terminal width.
if [ -n "$ctx_pct" ]; then
  ctx_int=$(printf '%.0f' "$ctx_pct")
  right="${DIM}ctx${RESET} $(color_for "$ctx_int")${ctx_int}%${RESET}"

  cols=$( { stty size </dev/tty; } 2>/dev/null | awk '{print $2}')
  [ -z "$cols" ] && cols=$(tput cols 2>/dev/null)
  [ -z "$cols" ] && cols=${COLUMNS:-120}

  strip() { printf '%b' "$1" | sed 's/\x1b\[[0-9;]*m//g'; }
  left_plain=$(strip "$out")
  right_plain=$(strip "$right")
  pad=$((cols - 4 - ${#left_plain} - ${#right_plain}))
  [ "$pad" -lt 2 ] && pad=2
  out="${out}$(printf '%*s' "$pad" '')${right}"
fi

printf '%b\n' "$out"
