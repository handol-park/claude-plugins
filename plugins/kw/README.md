# kw — Knowledge Workflow

A Claude Code plugin that integrates **taskwarrior** (task management),
**zk** (zettelkasten note-taking), and **GTD project notes** for
context-aware task execution and continuous knowledge capture.

## What It Does

When you start a task, kw automatically recalls relevant notes from your
zettelkasten and surfaces the GTD project context (outcome, status, next
actions). When you add a task, it links to the GTD project note — or
offers to create one. When you complete a task, it logs the completion
in the project note. As you work, you capture learnings back into the
vault. When you finish, you reflect on what you learned.

## GTD Integration

GTD project notes live at `~/notes/gtd/projects/<project>.md` and serve
as the source of truth for project-level context that taskwarrior tasks
lack. The project name in taskwarrior maps to the filename (dotted
subprojects like `saccade.l4` use the top-level name `saccade`).

## Structure

```
plugins/kw/
├── .claude-plugin/plugin.json      ← manifest (v0.3.0)
├── hooks/
│   ├── hooks.json                  ← SessionStart event registration
│   └── active-task-recall.sh       ← auto-recall context for active tasks
└── skills/
    ├── task/SKILL.md               ← task management (add/start/stop/done/…)
    ├── zk-capture/SKILL.md         ← quick fleeting notes to inbox
    ├── zk-zettel/SKILL.md          ← permanent atomic notes
    ├── zk-search/SKILL.md          ← query the vault
    ├── zk-connect/SKILL.md         ← surface missing links between notes
    └── reflect/SKILL.md            ← synthesize sessions into lessons
```

## Hook

**active-task-recall.sh** fires on `SessionStart`. If a taskwarrior task
is active, it searches the zk vault by description and tags, then injects
the top 5 relevant notes as session context.

## Skills

| Skill         | Description                                                                                                  |
| ------------- | ------------------------------------------------------------------------------------------------------------ |
| `/task`       | Manage taskwarrior tasks — add, list, start (with auto context-recall), stop, done, modify, delete, annotate |
| `/zk-capture` | Capture a fleeting note to the inbox with minimal friction                                                   |
| `/zk-zettel`  | Create a permanent atomic note with frontmatter, links, and bidirectional connections                        |
| `/zk-search`  | Query the vault — decomposes queries, reads matches, synthesizes answers with citations                      |
| `/zk-connect` | Find missing links — extracts concepts, searches related notes, suggests connections                         |
| `/reflect`    | Synthesize recent session transcripts into lessons learned, saved as zettels                                 |

## Prerequisites

- [taskwarrior](https://taskwarrior.org/) (v3+)
- [zk](https://github.com/zk-org/zk) — zettelkasten CLI

## Installation

Install via the Claude Code plugin marketplace:

```
handol-park-plugins/kw
```
