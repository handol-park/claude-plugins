---
name: task
description: Manage tasks via taskwarrior from within Claude Code. Supports add, list, start, stop, done, modify, delete. Recalls relevant zettelkasten context when starting a task.
---

# Task

Manage taskwarrior tasks without leaving Claude Code. Recall relevant
knowledge from the zettelkasten when starting a task.

Usage: `/task <subcommand> [args]`

## Subcommands

### add

Create a new task.

```bash
task add <description> [project:<name>] [+<tag>] [due:<date>] [priority:<H|M|L>]
```

After creating, report the task ID. If the user didn't specify a project,
ask which project it belongs to.

### list

List tasks. Pass filters directly to taskwarrior.

```bash
task <filter> list
```

Common filters: `project:<name>`, `+<tag>`, `status:pending`, `due:today`.
Default (no filter): show all pending tasks.

### start

Start working on a task. **This triggers context recall.**

```bash
task <id> start
```

After starting:

1. Export the task metadata:

   ```bash
   task <id> export
   ```

2. Extract search terms from `description`, `project`, and `tags`.

3. Search the zettelkasten for relevant notes:

   ```bash
   zk list --match "<description>" --format "{{id}} {{title}}" 2>/dev/null
   zk list --tag "<project>" --format "{{id}} {{title}}" 2>/dev/null
   zk list --tag "<tag>" --format "{{id}} {{title}}" 2>/dev/null
   ```

4. Read the top 5 most relevant notes (deduplicated across searches).

5. Present a brief summary:

   ```
   **Started:** <description> (project:<project>)

   **Relevant notes:**
   - [[id]] Title — one-line relevance
   - [[id]] Title — one-line relevance

   **No notes found on:** <gap topics, if any>
   ```

### stop

Stop working on a task without completing it.

```bash
task <id> stop
```

Ask the user if there's anything to capture before stopping:

- Blockers, open questions, or partial progress worth noting
- If yes, save via `/zk-capture` tagged with the task's project

### done

Mark a task complete.

```bash
task <id> done
```

After completing:

1. Ask: "Anything worth saving from this task?" (learnings, surprises,
   decisions made)
2. If yes, save as a zettel via `/zk-zettel` tagged with `lesson` and
   the task's project
3. Report completion

### modify

Modify a task's attributes.

```bash
task <id> modify <changes>
```

Changes can include description, project, tags, due date, priority.

### delete

Delete a task.

```bash
task <id> delete
```

Confirm with the user before deleting.

### annotate

Add a note to a task.

```bash
task <id> annotate <text>
```

## Inferring Subcommands

If the user says something natural instead of a subcommand, map it:

| User says                      | Subcommand            |
| ------------------------------ | --------------------- |
| `/task fix the login bug`      | `add`                 |
| `/task what's on my plate`     | `list`                |
| `/task work on 3`              | `start 3`             |
| `/task 3 is done`              | `done 3`              |
| `/task pause`                  | `stop` (active task)  |
| `/task change 3 priority to H` | `modify 3 priority:H` |

If ambiguous, ask.

## Active Task Awareness

When no ID is given for `stop`, `done`, or `annotate`, check for an
active task:

```bash
task +ACTIVE export
```

If exactly one task is active, use it. If multiple, ask which one.

## User Input

$ARGUMENTS - The subcommand and arguments (e.g., "add fix login bug project:web +urgent")
