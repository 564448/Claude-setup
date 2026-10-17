import json
import sys

try:
    prompt = str(json.loads(sys.stdin.buffer.read().decode("utf-8")).get("prompt", ""))
except ValueError:
    sys.exit(0)

lang = "Thai" if any("฀" <= ch <= "๿" for ch in prompt) else "English"

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": f"Language check: the user's latest message appears to be written in {lang}. Respond in {lang}.",
    }
}))
