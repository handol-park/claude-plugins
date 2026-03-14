# kw — Knowledge Workflow

A Claude Code plugin that integrates **GTD task management** and
**zettelkasten note-taking** using a single [zk](https://github.com/zk-org/zk)
vault for context-aware task execution and continuous knowledge capture.

## What It Does

Tasks are zk notes in `~/notes/gtd/tasks/` with status tracked via tags.
Projects are dashboard notes in `~/notes/gtd/projects/` that aggregate
task status. When you start a task, kw recalls relevant zettels and
surfaces the project context. Completions log to the project dashboard.

## Vault Structure

```
~/notes/
  .zk/config.toml
  zettels/               ← permanent knowledge
  gtd/
    projects/            ← project dashboards
    tasks/               ← task notes with context
    inbox/               ← fleeting captures
```

## Plugin Structure

```
plugins/kw/
├── .claude-plugin/plugin.json      ← manifest (v0.4.0)
├── hooks/
│   ├── hooks.json                  ← SessionStart event registration
│   └── active-task-recall.sh       ← auto-recall context for active tasks
└── skills/
    ├── tk/SKILL.md                 ← task management (add/start/stop/done/…)
    ├── zk-capture/SKILL.md         ← quick fleeting notes to inbox
    ├── zk-zettel/SKILL.md          ← permanent atomic notes
    ├── zk-search/SKILL.md          ← query the full vault
    ├── zk-connect/SKILL.md         ← surface missing links between notes
    └── reflect/SKILL.md            ← synthesize sessions into lessons
```

## Hook

**active-task-recall.sh** fires on `SessionStart`. Queries `zk list -t "active"`
for active task notes, then searches zettels for relevant context and injects
it into the session.

## Skills

| Skill         | Description                                                                                       |
| ------------- | ------------------------------------------------------------------------------------------------- |
| `/tk`         | Manage GTD tasks as zk notes — add, list, start (with context recall), stop, done, modify, delete |
| `/zk-capture` | Capture a fleeting note to `gtd/inbox/`                                                           |
| `/zk-zettel`  | Create a permanent atomic note in `zettels/`                                                      |
| `/zk-search`  | Query the full vault — zettels, tasks, projects, inbox                                            |
| `/zk-connect` | Find missing links across the full vault                                                          |
| `/reflect`    | Synthesize recent sessions into lessons, saved as zettels                                         |

## Prerequisites

- [zk](https://github.com/zk-org/zk) — zettelkasten CLI

## Installation

Install via the Claude Code plugin marketplace:

```
handol-park-plugins/kw
```
