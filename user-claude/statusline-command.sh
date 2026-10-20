#!/bin/bash
# Claude Code statusline: context left; model, 5h and 7d limits right (see statusline-command.py).
exec python3 "$(dirname "$0")/statusline-command.py"
