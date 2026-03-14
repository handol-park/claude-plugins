---
name: zk-search
description: Search the zettelkasten vault to answer a question or find relevant notes. Use when the user wants to query their knowledge base.
model: sonnet
---

# zk-search

Query `~/notes/zettelkasten/` and synthesize an answer from existing notes.

## When to Use

- "What do I have on X?"
- "Search my notes for Y"
- "What do I know about Z?"
- Before starting research — check vault first to avoid duplicating work

## Procedure

### 1. Decompose the query into search terms

Break the question into 3–5 keyword variants (synonyms, related concepts).

### 2. Search the vault

```bash
zk list --match "<term>" --format "{{id}} {{title}}" 2>/dev/null
```

Run one search per term. Collect all unique note IDs returned.

### 3. Read candidate notes

For each unique ID found, read the file:

```
~/notes/zettelkasten/<id>.md
```

Skim for relevance. Read fully if relevant.

### 4. Synthesize

Produce a response that:

- Answers the question using content from the notes
- Cites notes inline as `[[id]] Title`
- Flags gaps: "No notes found on X — consider running /research"

### 5. Suggest next steps

If relevant notes exist but are sparsely linked, suggest `zk-connect`.
If the vault has no coverage, suggest `research` + `zk-zettel`.

## Output Format

```
**From your notes:**

<synthesized answer citing [[id]] references>

**Relevant notes:**
- [[id]] Title — one-line summary
- [[id]] Title — one-line summary

**Gaps:** <what's missing, if anything>
```

## User Input

$ARGUMENTS - The question or topic to search for
