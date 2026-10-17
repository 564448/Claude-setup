import json
import os

setup = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
work = os.path.join(os.path.dirname(setup), "Knight")

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": (
            "New session started. Before proceeding with any task, confirm with the user whether to work in "
            f"{setup} (setup) or {work} (or a specific subfolder such as TaughtMe, CS, or Project) for this session."
        ),
    }
}))
