# Design: Auto-Roasting GitHub Profile README

**Date:** 2026-03-29
**Status:** Approved

## Overview

A GitHub Actions workflow that runs daily (and on-demand) to fetch the last 30 commits for GitHub user `jx4e` across public repos, send them to Claude for a snarky quality roast, and inject the result into a specific section of the profile README — without touching the rest of the file.

The codebase is structured as a plugin system so additional README features (riddle of the day, etc.) can be added by dropping in a new module.

---

## Architecture & Data Flow

```
GitHub Actions (cron: daily + workflow_dispatch)
    │
    └─► main.py
          ├─► features/roast.py
          │     ├─► GitHub API → fetch last 30 commits for jx4e
          │     └─► Claude API (claude-sonnet-4-20250514) → generate roast markdown
          ├─► [future features...]
          └─► readme.py
                └─► read README.md → replace each feature's marker section → write back
    │
    └─► git commit + push (GITHUB_TOKEN)
```

---

## File Structure

```
.github/
  workflows/
    update-readme.yml     # Workflow definition
scripts/
  main.py                 # Orchestrator — runs all features, updates README
  readme.py               # Shared marker-injection utility
  features/
    roast.py              # Commit roast feature
    # riddle.py           # Future: riddle of the day
README.md                 # Profile README (managed externally, markers placed by user)
```

---

## Components

### `main.py`
Orchestrator. Imports all registered feature modules, calls each `generate()` function to get markdown content, passes results to `readme.py` for injection. Fails loudly on any error — no silent swallowing.

### `readme.py`
Shared utility. Signature: `update_section(filepath: str, marker: str, content: str) -> None`

- Reads the README file
- Finds `<!-- {MARKER}_START -->` ... `<!-- {MARKER}_END -->` block
- Replaces the content between markers with the new content
- Raises `ValueError` if markers are not found (so missing markers are a loud failure, not a silent no-op)
- Writes the result back to disk

### `features/roast.py`
Exports a single `generate() -> str` function.

1. Reads `GITHUB_USERNAME` and `ANTHROPIC_API_KEY` from environment
2. Fetches last 30 commits via GitHub Events API (`GET /users/{username}/events/public`)
3. Extracts commit messages and repo names
4. Sends to Claude (`claude-sonnet-4-20250514`) with a prompt asking for a snarky roast: rating quality, calling out lazy messages like "fix", "wip", "update", and writing a short summary
5. Returns the Claude response as a markdown string

### `workflows/update-readme.yml`
- Triggers: `schedule` (daily 8am UTC) + `workflow_dispatch`
- Steps:
  1. Checkout repo
  2. Set up Python
  3. Install dependencies (`anthropic`, `requests`)
  4. Run `python scripts/main.py`
  5. Check `git diff --quiet README.md` — skip commit if no changes
  6. Commit and push with `GITHUB_TOKEN`

---

## Secrets

| Secret | Source | Purpose |
|--------|--------|---------|
| `ANTHROPIC_API_KEY` | Manual — add in repo Settings → Secrets | Claude API access |
| `GITHUB_TOKEN` | Built-in — no setup needed | Commit + push README |

---

## README Markers

User places these markers manually in their README where they want the roast to appear:

```html
<!-- ROAST_START -->
<!-- ROAST_END -->
```

The script replaces everything between them on each run.

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| No commits found | Returns placeholder: `_No recent commits to roast. Suspiciously quiet..._` |
| Claude API failure | Exception propagates — workflow step fails visibly in Actions log |
| Missing README markers | `ValueError` raised — workflow fails loudly |
| No diff after update | `git diff --quiet` check skips commit — no empty commits |
| GitHub API rate limit | Unauthenticated limit is 60 req/hr (well within daily run needs); can pass `GITHUB_TOKEN` as bearer to raise to 5000/hr if needed |

---

## Adding Future Features

1. Create `scripts/features/your_feature.py` with a `generate() -> str` function
2. Register it in `main.py`
3. Add `<!-- YOUR_FEATURE_START -->` / `<!-- YOUR_FEATURE_END -->` markers to README

No other changes needed.
