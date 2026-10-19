---
name: upload-to-github
description: Prep a folder/project for GitHub and upload it — verify the code, write a README, add .gitignore + LICENSE (checking upstream licenses if the code is derived from another project), then push to a new or existing repo. Use when asked to "upload this to github", "push this project to my github", "prep this for github", or similar.
---

# Upload to GitHub

Take a local folder and turn it into a properly documented GitHub repo, then
push it. Do NOT skip ahead to `git push` — walk the steps in order, and stop
for explicit confirmation at the gates marked **STOP**.

## 0. Scope

If it's not obvious which folder is being uploaded, ask. Then check:

- Is there already a `.git` folder here? If yes, this is an **update to an
  existing upload** — skip init, go straight to reviewing/committing new
  changes (step 5) and pushing to the existing `origin` (step 6, existing-repo
  path), unless the user says otherwise.
- **Secret scan**: grep the folder for `.env`, `*.pem`, `*.key`,
  `credentials.json`, and obvious hardcoded secrets (API keys, tokens,
  passwords, connection strings with embedded credentials) in source files.
  **STOP** and tell the user exactly what was found if anything looks
  sensitive — do not proceed until they say how to handle it (exclude it,
  it's a placeholder, etc.).

## 1. Static "does it work" checks

Best-effort, language-appropriate, **static only** — do not assume you can
actually run the program (it may need hardware/services not present here).

- Python: `python -m py_compile <file>.py` on every `.py` file; check that
  imports resolve against stdlib + any pinned dependency list
  (requirements.txt, setup script, etc.); flag any path the code references
  (model dirs, config files, assets) that doesn't exist in the folder.
- Shell: `bash -n <script>.sh` for syntax.
- Other languages: use the closest available static checker (`node --check`,
  `go vet`, `pip check`, etc.) if the toolchain is present; otherwise say
  plainly that no static checker ran for that file type.
- Report results per file: pass/fail, and **explicitly call out anything that
  could not be verified** (e.g. "requires a Raspberry Pi + camera + GStreamer
  — not testable on this machine") rather than implying it works.

## 2. README

Write/update `README.md` covering:

- What the program does.
- Requirements — pin exact versions wherever a setup script, lockfile, or
  requirements file specifies them (don't guess versions).
- Installation — if a setup script exists, document **both** a
  "run the script" path and a manual step-by-step path that mirrors the
  script's actual steps exactly (same package names, same versions, same
  order). If no script exists, document manual install from whatever
  dependency manifest is present.
- Usage — CLI args/flags/examples if applicable.
- A Credits/License section (filled in after step 3).

## 3. .gitignore and LICENSE

**.gitignore**: language-appropriate defaults (venvs, `__pycache__`/build
artifacts, OS cruft, IDE folders) plus anything project-specific (e.g. a venv
directory a setup script creates).

**LICENSE** — before picking one:

1. Determine whether the code is derived from / based on another project,
   tutorial, or repo (ask the user if unclear, or check code comments/README
   for a source they mentioned).
2. If yes: **fetch that project's actual LICENSE file** (don't assume the
   license type from memory) and comply with it — add its full text plus an
   attribution block (original author, project name, link) to this repo's
   `LICENSE`; add a short header comment to modified files noting they're
   changed from the original; add a Credits section to the README.
3. If it's fully original work: ask the user which license they want,
   defaulting to suggesting MIT for a personal/coursework project unless they
   prefer another.

## 4. Re-verify

Re-run the step 1 static checks now that new files exist (README/.gitignore/
LICENSE shouldn't break anything, but confirm nothing got moved/renamed by
mistake).

## 5. Stage and review — STOP

- Run `git status` (and `git diff` for tracked changes) and show the user
  exactly what would be committed.
- Add files **explicitly by name**, or `git add .` only after confirming
  `.gitignore` is in place and `git status` shows nothing unexpected. Never
  blind `git add -A`.
- **STOP**: get explicit confirmation of the file list before committing.

## 6. New repo vs. existing repo

Ask the user (don't assume) which applies:

**New repo:**
- Ask for repo name and visibility (public/private).
- Check `gh auth status`. If `gh` isn't installed: `winget install --id
  GitHub.cli -e`. If not authenticated: `gh auth login --hostname github.com
  --git-protocol https --web` — this prints a one-time code + URL; relay both
  to the user and wait for them to complete it in their browser.
- Set global `git config user.name` / `user.email` if not already configured
  (ask what to use — GitHub username is a reasonable default for name).
- `git init` (only if not already a repo) → commit → 
  `gh repo create <name> --public|--private --source=. --remote=origin --push`.

**Existing repo:**
- Ask for the repo URL (owner/name). Confirm it's reachable with
  `gh repo view <owner>/<name>`.
- Add it as `origin` if not already set (`git remote add origin <url>`).
- Commit, then `git push -u origin <branch>`.
- If the remote already has commits that would conflict, do not force-push —
  explain the conflict to the user and ask how they want to reconcile it
  (merge, rebase, or they push manually).

**STOP**: before the actual push in either path, show a summary — files
committed, destination repo, visibility — and get explicit confirmation.
Pushing is visible to others and not easily reversible; never push silently
even if running in an auto-accept mode.

## 7. Report back

Give the user: the final repo URL, what was added/changed (README, .gitignore,
LICENSE, any code fixes from step 1), and anything flagged along the way
(secrets found, checks that couldn't be verified, license decisions made).
