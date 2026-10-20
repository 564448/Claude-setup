import json, os, re, shutil, subprocess, sys, time

sys.stdout.reconfigure(encoding="utf-8")

ORANGE = "\033[38;2;217;119;87m"
DIM = "\033[2m"
RESET = "\033[0m"
RED = "\033[38;2;255;60;60m"
BAR_W = 10
BOLD = "[1m"


def get(d, *keys):
    for k in keys:
        if not isinstance(d, dict) or d.get(k) is None:
            return None
        d = d[k]
    return d


def color(pct, limit):
    return RED if pct >= limit else ORANGE


def bar(pct, limit=85):
    filled = max(0, min(BAR_W, round(pct / 100 * BAR_W)))
    return f"{color(pct, limit)}{'█' * filled}{RESET}{DIM}{'░' * (BAR_W - filled)}{RESET}"


def seg(label, pct, resets=None, limit=85):
    p = round(pct)
    s = f"{DIM}{label}{RESET} {bar(pct, limit)} {color(pct, limit)}{BOLD}{p}%{RESET}"
    if resets:
        t = time.strftime("%a %H:%M", time.localtime(resets))
        s += f" {DIM}({t}){RESET}"
    return s


data = json.load(sys.stdin)

left = ""
ctx = get(data, "context_window", "used_percentage")
if ctx is not None:
    left = seg("context", ctx, limit=70)

right = []
model = get(data, "model", "display_name") or ""
model = model.replace(" ", "")
effort = get(data, "effort", "level") or get(data, "effort_level")
if model:
    right.append(ORANGE + BOLD + model + (f"-{effort}" if effort else "") + RESET)
for label, key in (("5h", "five_hour"), ("7d", "seven_day")):
    pct = get(data, "rate_limits", key, "used_percentage")
    if pct is not None:
        right.append(seg(label, pct, get(data, "rate_limits", key, "resets_at")))
if left:
    right.append(left)
cwd = get(data, "workspace", "current_dir") or data.get("cwd") or os.getcwd()
branch = None
try:
    branch = subprocess.run(
        ["git", "-C", cwd, "branch", "--show-current"],
        capture_output=True, text=True, timeout=1,
    ).stdout.strip() or None
except Exception:
    pass
if branch:
    right.append(f"{DIM}Branch:{RESET}{ORANGE}{BOLD}{branch}{RESET}")
folder = os.path.basename(os.path.normpath(cwd))
if folder:
    right.append(f"{DIM}Directory:{RESET}{ORANGE}{BOLD}/{folder}{RESET}")
right = f"{DIM} | {RESET}".join(right)

print(right)
