---
name: zk-open
description: Open a note in the default editor by ID, title, or keyword. Use when the user wants to edit or view a specific note.
model: sonnet
---

# zk-open

Open a note from `~/notes/` in the default editor (configured in `.zk/config.toml`).

## When to Use

- "Open my MedGemma note"
- "Edit the Saccade project"
- "Open note abc12345"
- "Open the T4 task"

## Procedure

### 1. Resolve the note

If the user gave a bare ID (e.g. `y1g3oxl4`), use it directly.

Otherwise, search by keyword:

```bash
zk list --match "<query>" --format "{{filename-stem}} {{title}} ({{path}})" --notebook-dir ~/notes 2>/dev/null
```

If multiple matches, show them and ask which one.

### 2. Open with `zk edit`

```bash
zk edit <id-or-path> --notebook-dir ~/notes
```

`zk edit` opens the note in the editor configured in `~/notes/.zk/config.toml` (currently `vim`).

### 3. Confirm

Report which note was opened: `Opened [[<id>]] <title>`.

## Notes

- If the query is ambiguous, list candidates before opening.
- Prefer exact ID matches over fuzzy title matches to avoid opening the wrong note.

## User Input

$ARGUMENTS - Note ID, title, or keyword to search for
