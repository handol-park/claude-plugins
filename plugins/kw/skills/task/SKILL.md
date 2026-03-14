---
name: task
description: Manage tasks via taskwarrior from within Claude Code. Supports add, list, start, stop, done, modify, delete. Recalls zettelkasten and GTD project context when starting a task.
---

# Task

Manage taskwarrior tasks without leaving Claude Code. Recall relevant
knowledge from the zettelkasten and GTD project notes when starting a task.

Usage: `/task <subcommand> [args]`

## Subcommands

### add

Create a new task.

```bash
task add <description> [project:<name>] [+<tag>] [due:<date>] [priority:<H|M|L>]
```

After creating, report the task ID. If the user didn't specify a project,
ask which project it belongs to.

#### GTD project linking

If `project:<name>` was specified (or the user chose one):

1. Normalize the project name to a filename: lowercase, replace spaces with
   hyphens. For dotted subprojects (e.g., `saccade.l4`), use the top-level
   name (before the first dot).

2. Check if the GTD project note exists:

   ```bash
   test -f ~/notes/gtd/projects/<name>.md && echo "exists"
   ```

3. **If it exists**: confirm the link:
   "Linked to GTD project: `~/notes/gtd/projects/<name>.md`"

4. **If it does not exist**: ask the user: "No GTD project note for
   `<name>`. Create one?" If yes, create with this template:

   ```markdown
   ---
   title: <Name (title-cased)>
   date: <today>
   tags: [project, <name>]
   status: active
   ---

   ## Outcome

   <ask the user, or leave as TODO>

   ## Current Status

   - Just started

   ## Next Actions

   - [ ] <the task description just added>

   ## Waiting For

   ## Reference

   ## Log

   - <today>: Project note created; added task "<description>"
   ```

   If the user declines, proceed without the GTD link.

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

4. Check for a GTD project note:

   ```bash
   test -f ~/notes/gtd/projects/<project>.md && echo "exists"
   ```

   If it exists, read it and extract **Outcome**, **Current Status**, and
   **Next Actions**. For dotted subprojects, use the top-level name.
   If the project field is empty or the file doesn't exist, skip silently.

5. Read the top 5 most relevant zk notes (deduplicated across searches).

6. Present a brief summary:

   ```
   **Started:** <description> (project:<project>)

   **GTD Project:**
   - **Outcome:** <first paragraph>
   - **Status:** <current status content>
   - **Next Actions:** <next actions content>

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

After completing, report the task summary (description, project, time spent).

Then update the GTD project note's log:

1. If the task has a project, check for the GTD note:

   ```bash
   test -f ~/notes/gtd/projects/<project>.md && echo "exists"
   ```

   For dotted subprojects, use the top-level name.

2. If the file exists, append to the `## Log` section:

   ```
   - <today>: Completed "<task description>"
   ```

   If the file has no `## Log` heading, append one before the entry.
   If the file doesn't exist, skip silently.

Learnings are captured by `/reflect`, not here — reflect cross-references
`task completed:today export` to tag learnings with the right task/project.

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
