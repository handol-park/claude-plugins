---
name: task
description: Manage GTD tasks as zk notes in ~/notes/gtd/tasks/. Supports add, list, start, stop, done, modify, delete. Recalls zettelkasten context when starting a task.
---

# Task

Manage GTD tasks as zk notes. Tasks live in `~/notes/gtd/tasks/` with
status tracked via tags in frontmatter. Project dashboards in
`~/notes/gtd/projects/` aggregate task status.

Usage: `/task <subcommand> [args]`

## Subcommands

### add

Create a new task note.

1. **Generate an ID**:

   ```bash
   cat /dev/urandom | tr -dc 'a-z0-9' | head -c 8
   ```

2. **Create `~/notes/gtd/tasks/<id>.md`**:

   ```markdown
   ---
   title: <task description>
   date: <today YYYY-MM-DD>
   tags: [task, pending]
   project: <project-name>
   ---

   <context or details if provided>

   ## Sub-tasks

   ## Blockers

   ## Links

   - [[<project-id>]] — <project title> (parent project)
   ```

   If the user didn't specify a project, ask which project it belongs to.

3. **Link to project dashboard**: If `project:<name>` was specified (or
   the user chose one), normalize the name (lowercase, hyphens for spaces).

   ```bash
   zk list --path gtd/projects --match "<name>" --format "{{filename}} {{title}}" 2>/dev/null
   ```

   - **If found**: Add the new task to the project's `## Tasks` section:

     ```
     - [[<task-id>]] <task title> — `pending`
     ```

   - **If not found**: Ask the user: "No project dashboard for `<name>`.
     Create one?" If yes, create with this template:

     ```markdown
     ---
     title: <Name (title-cased)>
     date: <today>
     tags: [project, active]
     ---

     ## Outcome

     <ask the user, or leave as TODO>

     ## Tasks

     - [[<task-id>]] <task description> — `pending`

     ## Reference

     ## Log

     - <today>: Project created; added task "<description>"
     ```

     If the user declines, proceed without the project link.

4. **Report** the task ID and filename.

### list

List tasks from the vault.

```bash
zk list --path gtd/tasks --format "{{id}} {{title}} [{{tags}}]" 2>/dev/null
```

Filters:

- By status: `zk list --path gtd/tasks -t "active"` (or `pending`, `done`)
- By project: `zk list --path gtd/tasks --match "project: <name>"`
- Default (no filter): show all non-done tasks (`-t "active"` + `-t "pending"` in two queries, or filter output)

### start

Start working on a task. **This triggers context recall.**

1. Find the task note by ID or title search:

   ```bash
   zk list --path gtd/tasks --match "<query>" --format "{{filename}} {{title}}" 2>/dev/null
   ```

2. Edit the task note: change tag `pending` → `active` in frontmatter.

3. Update the project dashboard: change the task's status suffix from
   `` `pending` `` to `` `active` ``.

4. **Context recall** — extract search terms from title, project, and tags:

   ```bash
   zk list --path zettels --match "<title keywords>" --format "{{id}} {{title}}" --limit 5 2>/dev/null
   zk list --path zettels -t "<project>" --format "{{id}} {{title}}" --limit 3 2>/dev/null
   ```

5. Read the project dashboard for Outcome, Tasks, and recent Log entries.

6. Read the top 5 most relevant zettel notes (deduplicated).

7. Present:

   ```
   **Started:** <title> (project: <project>)

   **Project dashboard:**
   - **Outcome:** <first paragraph>
   - **Tasks:** <task list with statuses>

   **Relevant notes:**
   - [[id]] Title — one-line relevance

   **No notes found on:** <gap topics, if any>
   ```

### stop

Pause a task without completing it.

1. Edit the task note: change tag `active` → `pending`.
2. Update the project dashboard status suffix.
3. Ask the user if there's anything to capture before stopping
   (blockers, open questions). If yes, add to the task note's
   `## Blockers` section.

### done

Mark a task complete.

1. Edit the task note: change tag to `done`.
2. Update the project dashboard:
   - Change the task's status suffix to `` `done` ``
   - Append to `## Log`:

     ```
     - <today>: Completed [[<task-id>]] "<task title>"
     ```

3. Report task summary (title, project).

### modify

Edit a task note's frontmatter or content directly.

1. Find the task note.
2. Apply the requested changes (title, tags, project, content).
3. If project changed, update both old and new project dashboards.

### delete

Remove a task.

1. Confirm with the user before deleting.
2. Remove the task note file.
3. Remove the task link from the project dashboard's `## Tasks` section.

## Inferring Subcommands

If the user says something natural instead of a subcommand, map it:

| User says                          | Subcommand           |
| ---------------------------------- | -------------------- |
| `/task fix the login bug`          | `add`                |
| `/task what's on my plate`         | `list`               |
| `/task work on T4 Brain`           | `start`              |
| `/task T4 is done`                 | `done`               |
| `/task pause`                      | `stop` (active task) |
| `/task change T4 to high priority` | `modify`             |

If ambiguous, ask.

## Active Task Awareness

When no task is specified for `stop`, `done`, or `modify`, find active
tasks:

```bash
zk list --path gtd/tasks -t "active" --format "{{id}} {{title}}" 2>/dev/null
```

If exactly one is active, use it. If multiple, ask which one.

## Status Convention (tags)

- `active` — currently being worked on (multiple allowed)
- `pending` — not started or paused
- `done` — completed

## User Input

$ARGUMENTS - The subcommand and arguments (e.g., "add fix login bug project:web")
