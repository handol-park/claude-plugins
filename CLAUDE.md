# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A Claude Code plugin marketplace (`handol-park-plugins`). Each plugin under `plugins/` is a self-contained unit with hooks, skills, and metadata that Claude Code loads at runtime.

## Architecture

```
.claude-plugin/marketplace.json   ← marketplace manifest (lists all plugins + versions)
plugins/<name>/
  .claude-plugin/plugin.json      ← plugin manifest (name, version, license, keywords)
  hooks/
    hooks.json                    ← hook registration (event → command mapping)
    *.sh                          ← hook scripts (must output JSON to stdout)
  skills/<skill-name>/
    SKILL.md                      ← skill definition (frontmatter name/description + markdown body)
```

**Key invariant**: The `version` field in `marketplace.json` and the plugin's `plugin.json` must always match. Update both when bumping versions.

## Current Plugins

| Plugin | Description |
|--------|-------------|
| `rlm` | RLM-disciplined orchestration — enforces subagent delegation via 50/2 rule, circuit breaker, and trampoline pattern |

## Hook Output Contract

Session hooks must print valid JSON to stdout. The `hookEventName` field is **required** for validation. The expected shape:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<escaped string>"
  }
}
```

`session-start.sh` uses Python for JSON escaping with a pure-bash fallback (for environments without Python, e.g., Windows without a real Python install).

## Testing Changes

```bash
# Test a hook script produces valid JSON
bash plugins/rlm/hooks/session-start.sh

# Verify no stale references after renames
grep -r "old-name" --include="*.json" --include="*.md" --include="*.sh" .
```

## Cross-Platform Notes

- Hook scripts use `#!/usr/bin/env bash` — requires Git Bash or WSL on Windows.
- Python detection in hooks uses `--version` checks (not `command -v`) to skip Windows Store stubs that don't actually run Python.
