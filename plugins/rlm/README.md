# rlm — RLM-Disciplined Orchestration

A Claude Code plugin that enforces subagent delegation via hard rules,
keeping the main thread as a lightweight orchestrator.

## What It Does

RLM (Responsibility Lifecycle Management) prevents context overload by
injecting orchestration discipline into every session:

- **50/2 Rule** — Delegate to a subagent when a task requires >50 lines
  of reading or touches >2 files.
- **Circuit Breaker** — After >8 Read/Grep calls without delegating,
  stop and restructure as subagent dispatch.
- **Task List = Call Stack** — Encode task decomposition with `blockedBy`
  dependencies; deeper complexity spawns new tasks + new subagents
  (trampoline pattern).

## Structure

```
plugins/rlm/
├── .claude-plugin/plugin.json      ← manifest (v1.2.1)
├── hooks/
│   ├── hooks.json                  ← SessionStart event registration
│   └── session-start.sh            ← injects orchestration rules on startup
└── skills/
    └── rlm/
        └── SKILL.md                ← delegation decision reference
```

## Hook

**session-start.sh** fires on `SessionStart` (startup, resume, clear,
compact). It injects the orchestration rules as `additionalContext` so
every session starts with the delegation discipline active.

## Skill: `/rlm`

A comprehensive reference for delegation decisions:

- Decision tree (delegate vs. do-directly)
- Subagent prompt template (Objective, Scope, Return Format, Constraints)
- Subagent type selection matrix (Explore, Plan, general-purpose, Bash)
- Anti-pattern guide and escape hatches

## Installation

Install via the Claude Code plugin marketplace:

```
handol-park-plugins/rlm
```
