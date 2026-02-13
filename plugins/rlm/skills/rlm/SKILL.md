---
name: rlm
description: Use when deciding whether to delegate to subagents, structuring subagent prompts, encoding task decomposition as a call stack, or when any orchestration decision is ambiguous. Invoke on complex delegation decisions.
---

# RLM Orchestration — Detailed Reference

## 1. Delegation Decision Tree

```
User request arrives
  │
  ├─ Requires reading >50 lines? ──── YES ──→ DELEGATE
  │
  ├─ Requires reading >2 files? ───── YES ──→ DELEGATE
  │
  ├─ Unfamiliar subsystem? ────────── YES ──→ DELEGATE (Explore first)
  │
  ├─ Simple lookup <50 lines
  │  in known location? ───────────── YES ──→ DO DIRECTLY
  │
  ├─ Error message / stack trace? ─── YES ──→ READ DIRECTLY, then delegate fix
  │
  └─ Uncertain? ───────────────────── YES ──→ DELEGATE (err on delegation side)
```

## 2. Concrete Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Lines to read | >50 | Delegate |
| Files to read | >2 | Delegate |
| Complexity | Unfamiliar subsystem | Delegate |
| Tool calls accumulated | >8 Read/Grep without delegation | STOP, delegate |
| Response requires | Multi-file synthesis | Delegate |

## 3. Subagent Prompt Template

Every dispatch MUST include these four sections:

```
**Objective**: [1 sentence — what the subagent must accomplish]

**Scope**: [Specific files, directories, or patterns to examine]

**Return Format**:
- Structured summary, <200 words
- Include file:line references for key findings
- [Any task-specific format requirements]

**Constraints**:
- Do not return raw file contents
- Focus on [specific aspect]
- If scope is insufficient, report what's missing rather than expanding
```

## 4. Subagent Type Selection

| Purpose | Agent Type | Prompt Focus |
|---------|-----------|--------------|
| Find files/structure | Explore | "Find all X, report paths and brief descriptions" |
| Understand code | Explore | "Read X, summarize: purpose, inputs, outputs, dependencies" |
| Search for patterns | Explore | "Find all occurrences of X, report locations and context" |
| Plan changes | Plan | "Given X needs to change, identify affected files and changes" |
| Implement feature | general-purpose | "Implement X following TDD: write test, implement, verify" |
| Review code | general-purpose | "Review changes in X for correctness, security, quality" |
| Run commands | Bash (subagent) | "Execute X, report output and exit code" |

## 5. Task List as Call Stack

Map task states to recursive call semantics:

| Task State | Call Stack Equivalent |
|------------|----------------------|
| `pending` | Unresolved stack frame |
| `in_progress` | Currently executing |
| `completed` | Resolved — return value available |
| `blockedBy` | Waiting on sub-call to resolve |

### Encoding pattern

```
User request
  └─ Task #1: Top-level goal (pending)
       ├─ Task #2: Sub-problem A (pending, blockedBy: [])
       │    └─ Dispatch Explore subagent → on return, mark #2 completed
       ├─ Task #3: Sub-problem B (pending, blockedBy: [#2])
       │    └─ Uses #2's summary → dispatch Plan subagent
       └─ Task #4: Synthesize (pending, blockedBy: [#2, #3])
            └─ Combine summaries → respond to user → mark #1 completed
```

## 6. Trampoline Pattern

When a subagent returns a summary that reveals deeper complexity:

1. **Do NOT** expand the analysis yourself
2. Create new tasks for each revealed sub-problem
3. Set `blockedBy` relationships
4. Dispatch new subagents for the leaf tasks
5. Synthesize when all leaves complete

Example: Subagent returns "found 3 subsystems: auth, routing, storage — each needs analysis"
- Create Task #5: Analyze auth (dispatch Explore)
- Create Task #6: Analyze routing (dispatch Explore)
- Create Task #7: Analyze storage (dispatch Explore)
- Create Task #8: Synthesize findings (blockedBy: [#5, #6, #7])

## 7. Anti-Patterns

| Thought | Instead |
|---------|---------|
| "Let me just quickly read this file" | If >50 lines, delegate |
| "I need to understand the codebase first" | Delegate to Explore subagent |
| "One more grep to confirm" | If >8 tool calls, delegate |
| "I already have context from earlier" | Context rots — re-delegate for fresh reads |
| "A subagent would be overkill" | Unless <50 line config file, delegate |
| "I'll be faster doing this myself" | Short-term true, long-term context rot |
| "Let me just check one more thing" | Batch into a single subagent dispatch |
| "I can synthesize from what I've read" | If you read >50 lines to get here, you already violated the rule |

## 8. Workflow Orchestration Patterns

RLM defines HOW the orchestrator participates in any workflow — by delegating, not accumulating.

| Workflow Phase | RLM Orchestrator Role |
|----------------|----------------------|
| Brainstorming | Dispatch research subagents, synthesize options |
| Planning | Delegate codebase exploration, synthesize into plan |
| TDD | Delegate test writing/running to subagents |
| Implementation | Decompose tasks, dispatch parallel subagents with thresholds |
| Debugging | Delegate evidence gathering, synthesize diagnosis |
| Verification | Delegate verification runs, synthesize pass/fail |
| Code Review | Delegate review to code-reviewer subagent |

## 9. Escape Hatch — Direct Reads Permitted

Direct reads (without delegation) are allowed ONLY for:

- Single files under 50 lines (configs, manifests, short scripts)
- Error messages, stack traces, and single-command output
- Known-location value lookups (e.g., version in package.json)
- Writing to files already understood from subagent summaries
- Task list management (reading task descriptions)
- Memory files (MEMORY.md, project notes)

When in doubt: **delegate**.
