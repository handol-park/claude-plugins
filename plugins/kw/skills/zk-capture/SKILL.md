---
name: zk-capture
description: Quickly capture a fleeting note to the GTD inbox. Use when the user wants to jot down an idea, thought, or reference without formatting ceremony.
model: sonnet
---

# zk-capture

Minimal-friction capture of a fleeting note to `~/notes/gtd/inbox/`.

## When to Use

- "Capture this idea"
- "Add this to my notes"
- "Save this for later"
- Any quick thought that shouldn't interrupt the current flow

## Procedure

1. **Generate an ID**: 8 random lowercase alphanumeric characters

   ```bash
   cat /dev/urandom | tr -dc 'a-z0-9' | head -c 8
   ```

2. **Create `~/notes/gtd/inbox/<id>.md`** with minimal frontmatter:

   ```markdown
   ---
   title: <short title inferred from content>
   date: <today>
   tags: []
   ---

   <content as-is, unprocessed>
   ```

3. **Confirm**: Report the filename created. Do not elaborate or process the content.

## Rules

- Do NOT rewrite, clean up, or structure the content — capture raw
- Do NOT add links — that's for `zk-connect`
- Do NOT promote to a permanent note — that's for `zk-zettel`
- Inbox notes are intentionally rough

## User Input

$ARGUMENTS - The idea, thought, or content to capture
