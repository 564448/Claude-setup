---
name: distill-memory
description: Distill the user's instructions from this session into topic-folder memories, after the user reviews every step. Invoked by the user as /distill-memory [topic].
disable-model-invocation: true
license: MIT
---

# Distill Memory

> Written 2026-10-17 from the steps used to build the `UAV/` memory folder in one session.

**Arguments:** `$ARGUMENTS` (optional topic, e.g. `UAV`)

Turn what the user told you in this session into persistent memories. Every step below ends by waiting for the user, **in every permission mode**, including Auto and Bypass: memories shape every later session, so nothing is written until the user confirms.

## Layout

All memories live in this project's memory folder (`~/.claude/projects/<project slug>/memory/`; the slug is the working directory path with every character that isn't a letter or digit replaced by `-`, e.g. `C--Knight-Claude` on Windows or `-home-knight-claude` on Linux).

```
memory/
├─ MEMORY.md            one line per topic folder + one line per top-level memory
├─ <cross-topic>.md     applies to every topic
└─ <Topic>/
   ├─ README.md         index: what the folder is for + one line per file
   └─ <name>.md         one memory per file
```

- Every topic gets a folder with a `README.md`, even with a single memory.
- `MEMORY.md` gets exactly one line per folder, pointing to its README, e.g. `- [UAV](UAV/README.md) — UAV/drone/GCS work: ... (read the README first)`.
- A memory that applies across topics stays at the top level with its own line in `MEMORY.md`.
- **The user names every new folder.** Propose 1–3 names and wait for the choice.
- Everything is in English: file names, frontmatter, body, README lines and the `MEMORY.md` line.

Each memory file:

```markdown
---
name: <topic>-<short-kebab-slug>
description: <one line, used to decide relevance>
metadata:
  type: user | feedback | project | reference
---

<the rule or fact>

**Why:** <the reason the user gave, or the incident behind it>   (feedback / project)

**How to apply:** <when and where it applies; link related memories with [[name]]>
```

The folder README uses the same frontmatter (`name: <topic>-index`, `type: reference`). Its body says what the folder holds, that the list must be updated whenever a file is added, edited or deleted, and has one line per file: `- [[name]] (\`file.md\`): <hook>`.

## What to keep

- **Keep:** guidelines and requirements that hold beyond the current task: how the user wants you to work, safety rules, testing standards, stable reference facts.
- **Drop:** one-off task details, mission or feature specifics, values that live in code, machine-specific data (IPs, COM ports, hostnames that change), and anything the repo, git history or `CLAUDE.md` already records.
- Group by type: `feedback` (how to work, with Why/How to apply), `project` (ongoing goals or constraints), `reference` (pointers and stable facts), `user` (who the user is).

## Step 1: Collect the instructions

1. Read the user's messages for the **whole session**, including the part before any compaction. Find the transcript as the most recently modified `*.jsonl` in `~/.claude/projects/<project slug>/`, and extract the user's text messages, skipping tool results, skill bodies and system text:

   ```bash
   PYTHONIOENCODING=utf-8 python - "<transcript.jsonl>" <<'EOF'
   import json, sys
   for line in open(sys.argv[1], encoding="utf-8"):
       try: d = json.loads(line)
       except ValueError: continue
       if d.get("type") != "user": continue
       c = d.get("message", {}).get("content")
       t = c if isinstance(c, str) else " ".join(
           x.get("text", "") for x in (c or []) if isinstance(x, dict) and x.get("type") == "text")
       t = t.strip()
       if t and not t.startswith(("<", "Base directory", "This session", "[Image")):
           print("-", t[:600].replace("\n", " "))
   EOF
   ```

   If the output is too long, save it to a file in the scratchpad and read it in parts.
2. With a topic argument, keep only the instructions about that topic. Without one, list the topics you found (with a count each) and ask which to distill. Stop until the user answers.
3. Read `MEMORY.md` and, for the chosen topic, its folder README and files if they exist.

## Step 2: Propose the summary

Show the instructions as short numbered groups (e.g. ways of working, safety, testing, reference). Under each point, keep the user's intent, not the wording of one message. Mark anything you plan to drop and why. Ask the user to cut, edit or add, then stop.

Repeat until the user is happy with the content.

## Step 3: Propose the files

Show, in one message:

- **Folder:** the existing topic folder, or 1–3 proposed names for a new one (the user picks or gives another).
- **Files:** a table of file name, type and the README line for each.
- **Index lines:** the README list and the `MEMORY.md` line as they will be written.
- **Changes to existing memories.** For every existing file the new content touches, whether it adds detail or conflicts, show:
  - the current text and the proposed text side by side
  - at least two options (e.g. replace, merge into the existing file, keep both as separate files), each with its pros and cons
  - your recommended option

  Never change an existing memory without the user picking an option.

End with: type "confirm" (or the user's usual word, e.g. "ยืนยัน") to write. Stop.

## Step 4: Write

Only after confirmation:

1. Create the folder (if new) and write each memory file.
2. Write or update the folder `README.md`.
3. Add or update the folder's single line in `MEMORY.md`. Don't touch other lines.
4. Apply the chosen option for each existing memory that was touched.
5. If the project keeps a copy of its memories in a repo (e.g. `user-claude/memory/`, restored by a bootstrap script), copy every new or changed file there too, keeping the folder layout. Tell the user the memories reach the remote only after that repo is committed and pushed.

## Step 5: Verify

Run the `verification-before-completion` gate:

- List the memory folder: every planned file exists, and nothing else was added or removed.
- Read `MEMORY.md`: one line for the folder, other lines unchanged.
- Every `name:` is unique, and every `[[link]]` matches an existing `name:`.
- The README lists every file in the folder.
- If there is a repo copy (Step 4.5), `diff -r` between it and the memory folder shows no differences (line endings aside).

Finish with the end-of-task summary and its **[Verified]** block. Say plainly that you can't check in this session whether a new session recalls the memories, and that the user can check by asking about the topic in a fresh session.
