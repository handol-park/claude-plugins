---
name: reflect
description: Reflect on recent sessions — synthesize conversation transcripts into lessons learned and implement improvements
---

# Reflect

Synthesize recent conversation transcripts into lessons and implement
improvements. Can be run anytime (`/reflect [duration]`).

Optional argument: a duration like `3d`, `1w`, `2w` that caps how far
back to look. Without it, reflects on everything since the last reflection.

## Procedure

1. Determine the start boundary:
   - If a duration argument is given, compute the cutoff:

     ```bash
     date -u -d "now - 3 days" '+%Y-%m-%d'  # for 3d
     ```

   - Otherwise, find the last reflection by searching the zettelkasten:

     ```bash
     zk list --tag "reflection" --sort created- --limit 1 --format "{{id}} {{title}}"
     ```

     The start date is the day **after** that reflection's date.
     If no prior reflection exists, use the earliest transcript.

   - Use whichever start date is **more recent** (the duration cap or
     the last reflection boundary).

2. Find conversation transcripts since the start date:

   ```bash
   find ~/.claude/projects/ -name '*.jsonl' -newermt "$start_date" -type f | sort
   ```

   If no new transcripts exist, stop and tell the user — nothing to
   reflect on.

3. For each transcript, use a subagent to extract a summary:
   - What was done (completed work)
   - Surprises (expected X, got Y)
   - Tool failures and their causes

   Use `jq` or `head`/`tail` on the `.jsonl` transcript — do NOT read
   the whole file (they exceed 25K tokens). Extract the last few assistant
   messages for a summary.

4. Search existing knowledge to avoid duplicating known lessons:
   - Read always-loaded lesson files (currently `lessons-*.md` in rules/)
   - Use `/zk-search` to check for existing notes on each surprise topic

5. Save the reflection as a zettel using `/zk-zettel`:
   - Tag with `reflection`
   - Structure the note body as:

     ```markdown
     ## Sessions reviewed

     - YYYY-MM-DD: {one-line summary}

     ## Surprises (grouped by topic)

     ### {Topic}

     - {expected X, got Y}

     ## Fail patterns

     - {N occurrences of X — likely cause}

     ## Rules to add/update

     - {concrete rule for each recurring surprise or failure}
     ```

   - Let `/zk-zettel` handle ID generation, linking, and file placement

6. For each surprise or fail pattern that is **new** (not already a known
   lesson or existing zettel), save it as its own zettel via `/zk-zettel`:
   - One atomic note per lesson
   - Tag with `lesson` and a topic tag (e.g., `infra`, `eval`, `llm`)
   - Link back to the reflection note

7. Classify each new lesson to decide if it needs implementation beyond
   a zettel (apply in order — first match wins):

   **Hook** — the failure is detectable by inspecting tool inputs/outputs.
   Ask: "Can a shell script, given the tool name and JSON input/output,
   catch this before or after it happens?"
   - Yes → write a hook. Examples:
     - PreToolUse: block `git push --force` to main
     - PostToolUse: lint files after Edit/Write
     - PreToolUse: reject Bash commands containing hardcoded secrets
   - Heuristic: if the lesson says "don't do X" and X is a specific
     tool action with a detectable pattern, it's a hook.
   - Target: `~/.claude/settings.json` (or project `.claude/settings.json`)

   **Skill** — the lesson describes a multi-step procedure that a user
   would invoke on demand (not an automated guardrail).
   Ask: "Would a user say `/do-this-thing` to trigger it?"
   - Yes → create or update a skill.
   - Heuristic: if the lesson is procedural (do A, then B, then C)
     and requires judgment at each step, it's a skill.
   - Target: `~/.claude/skills/<name>/SKILL.md`

   **Rule** — the lesson recurs frequently and should be always-loaded
   rather than recalled on demand.
   Ask: "Will this apply to most sessions regardless of project?"
   - Yes → add to the appropriate `lessons-<topic>.md` file.
   - No → the zettel from step 6 is sufficient (recallable on demand).

   **None** — the zettel is enough. Most lessons stay as zettels.

8. Implement candidates:
   - For hooks: use `/hookify` if available, otherwise edit settings.json
     directly. Include a `description` field explaining the incident.
   - For skills: create a new `SKILL.md` or update an existing one.
     Don't create a skill for a single-use procedure.
   - For rules: add with incident context. Prune stale rules from the
     same file to keep always-loaded context lean.

9. Commit: `chore(claude): reflection YYYY-MM-DD — {summary}`

## Important

Surprises are the signal. Group by topic (not date) to reveal patterns.
A rule without incident context is noise — be specific.
If the same surprise appears 2+ times, it **must** become a rule or hook.
The classification test is sequential — don't skip to "rule" because it's
easier. If it's detectable, it should be a hook.
Most lessons should stay as zettels — only promote to always-loaded rules
when they apply universally across projects.
