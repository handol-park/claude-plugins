---
name: zk-connect
description: Find missing links between notes in the zettelkasten. Use when a note feels isolated or after adding new notes to surface bidirectional connections.
model: sonnet
---

# zk-connect

Surface missing bidirectional links for a note or set of notes.

## When to Use

- After creating a new zettel (to find what it should link to)
- "Find links for [[id]]"
- "What notes relate to X?"
- Periodic vault maintenance to reduce orphan notes

## Procedure

### 1. Identify the target note

If given an ID, read `~/notes/zettelkasten/<id>.md`.
If given a title or topic, find it first:

```bash
zk list --match "<title>" --format "{{id}} {{title}}"
```

### 2. Extract key concepts

From the note content, identify 3–5 core concepts, terms, or claims to search against.

### 3. Search for related notes

```bash
zk list --match "<concept>" --format "{{id}} {{title}}"
```

One search per concept. Exclude the target note itself.

### 4. Read candidates

Read each candidate note. Assess whether a link is meaningful:

- Does the candidate _directly_ develop, support, contrast, or apply the target idea?
- Would a reader of the target note benefit from following this link?

Discard weak associations.

### 5. Present link suggestions

```
**Suggested links for [[id]] — Title:**

→ [[id]] Title
  Reason: <one sentence why these ideas connect>
  Direction: <target → candidate | candidate → target | bidirectional>

→ [[id]] Title
  ...
```

### 6. Apply (with confirmation)

For each accepted link, add to the appropriate note:

```markdown
## Links

- [[id]] — Title — <reason>
```

Always add links in both directions unless the relationship is clearly one-way.

## Rules

- Quality over quantity — 2 strong links beat 8 weak ones
- Never link just because topics overlap — link when ideas _develop_ each other
- Always update both notes for bidirectional links

## User Input

$ARGUMENTS - Note ID, title, or topic to find connections for
