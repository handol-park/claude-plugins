---
name: zk-connect
description: Find missing links between notes across the full vault (zettels + GTD). Use when a note feels isolated or after adding new notes to surface bidirectional connections.
model: sonnet
---

# zk-connect

Surface missing bidirectional links for a note or set of notes across the
full vault (`~/notes/`).

## When to Use

- After creating a new zettel (to find what it should link to)
- "Find links for [[id]]"
- "What notes relate to X?"
- Periodic vault maintenance to reduce orphan notes

## Procedure

### 1. Identify the target note

If given an ID, find and read the note (could be in any group):

```bash
zk list --match "<id or title>" --format "{{filename}} {{title}} ({{path}})" 2>/dev/null
```

### 2. Extract key concepts

From the note content, identify 3–5 core concepts, terms, or claims to search against.

### 3. Search for related notes

```bash
zk list --match "<concept>" --format "{{filename-stem}} {{title}} ({{path}})" 2>/dev/null
```

One search per concept. Exclude the target note itself. Results may span
zettels, GTD tasks, and project dashboards.

### 4. Read candidates

Read each candidate note. Assess whether a link is meaningful:

- Does the candidate _directly_ develop, support, contrast, or apply the target idea?
- Would a reader of the target note benefit from following this link?

Discard weak associations.

### 5. Present link suggestions

```
**Suggested links for [[id]] — Title:**

→ [[id]] Title (zettels/)
  Reason: <one sentence why these ideas connect>
  Direction: <target → candidate | candidate → target | bidirectional>

→ [[id]] Title (gtd/tasks/)
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
