---
name: zk-zettel
description: Turn conversation content or research into a permanent zettel note. Use when the user wants to save a synthesized idea, research output, or insight as a proper permanent note with links.
model: sonnet
---

# zk-zettel

Convert conversation content into a permanent atomic note in `~/notes/zettels/`.

## When to Use

- "Add this to my zettels"
- "Save this as a note"
- After `/research` produces a report
- When a conversation yields a reusable insight worth keeping

## Procedure

### 1. Extract the atomic idea

Identify the single core idea. If the content contains multiple distinct ideas,
ask the user which to capture (or create multiple notes).

### 2. Find related existing notes

```bash
zk list zettels --match "<keyword1>" --format "{{filename-stem}} {{title}}"
zk list zettels --match "<keyword2>" --format "{{filename-stem}} {{title}}"
```

Run 2–3 searches across key terms. Collect candidate IDs for linking.

### 3. Create the note with `zk new`

```bash
zk new zettels --title "<title>" --print-path --no-input
```

This returns the file path (e.g. `/home/handolpark/notes/zettels/abc12345.md`).
Then write the body into that file — the template already adds frontmatter with
`title` and `date`; you only need to fill in `tags` and the content.

The note body structure:

```markdown
---
title: <concise title, noun phrase>
date: <auto-filled>
tags: [<relevant tags>]
---

<Opening sentence: the core claim or definition, no preamble.>

<Body: atomic — one idea, fully developed. Use ## headers for sub-sections
if needed. Keep it dense and durable — written for future-you with no
context from this conversation.>

## Sources

- [Title](url) — for any web sources used

## Links

- [[<id>]] — <title> — <one-line reason for the link>
```

### 5. Confirm

Report the filename and title. Offer to run `zk-connect` to surface more links.

## Rules

- One idea per note (atomic)
- Opening sentence must stand alone — no "In this note..."
- Links must be bidirectional: if you link to a note, mention updating that note too
- No orphan notes — every permanent note links to at least one other

## User Input

$ARGUMENTS - The content, topic, or conversation excerpt to turn into a zettel
