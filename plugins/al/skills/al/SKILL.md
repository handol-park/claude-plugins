---
name: al
description: Run a minimal agentic loop. Orchestrator dispatches subagents iteratively toward a goal; state file (not agent text) signals completion. Use when a task requires repeated autonomous iterations with a verifiable done condition.
---

# al — Agentic Loop

Runs a goal-directed loop where each iteration is handled by a subagent. The
orchestrator never trusts the agent's text output — completion is signaled
exclusively via a state file written by the subagent.

Usage: `/al <goal> [workdir=<path>] [max=<N>]`

## State File

Location: `<workdir>/.al-state.json` (default workdir: current directory)

Schema:

```json
{
  "status": "pending | in_progress | done | failed",
  "iteration": 0,
  "goal": "<goal string>",
  "progress": "<what was accomplished this iteration>",
  "result": "<final output when status=done>",
  "error": "<reason when status=failed>"
}
```

The orchestrator reads this file after every Agent call. The subagent's text
return value is ignored.

## Orchestrator Steps

1. **Initialize**: write state file with `status: pending`, `iteration: 0`, `goal`.

2. **Loop** (repeat until done, failed, or `iteration >= max`):
   a. Increment `iteration` in state file (`status: in_progress`).
   b. Dispatch subagent via Agent tool using the prompt template below.
   c. After Agent returns, read state file.
   d. If `status == "done"` → exit loop, report `result`.
   e. If `status == "failed"` → exit loop, report `error`.
   f. Otherwise → continue.

3. **Max iterations reached**: report timeout, show last `progress` from state file.

## Subagent Prompt Template

```
Goal: <goal>
State file: <workdir>/.al-state.json
Iteration: <N> of <max>

Instructions:
1. Read the state file to understand what has been done so far (check `progress`).
2. Do the next unit of work toward the goal.
3. Update the state file when finished with this iteration:
   - If the goal is fully complete:
     {"status": "done", "iteration": <N>, "goal": "<goal>", "progress": "<what was done>", "result": "<final output or summary>"}
   - If more work remains:
     {"status": "in_progress", "iteration": <N>, "goal": "<goal>", "progress": "<what was done this iteration>"}
   - If unrecoverable error:
     {"status": "failed", "iteration": <N>, "goal": "<goal>", "error": "<reason>"}

Write the state file atomically (write to .al-state.tmp, then rename to .al-state.json).
Do NOT signal completion in your text response — the state file is the only signal.
```

## Verification

After reading the state file, the orchestrator independently verifies the
`done` signal where possible:

- If `result` references a file → check it exists and is non-empty.
- If `result` references a count → spot-check against the actual artifact.

If verification fails, treat the iteration as `in_progress` and continue.

## Defaults

| Parameter | Default                   |
| --------- | ------------------------- |
| `workdir` | current working directory |
| `max`     | 10                        |

## Example

```
/al "process all CSV files in ./data and write summary to ./output/summary.json" workdir=. max=5
```

State file after completion:

```json
{
  "status": "done",
  "iteration": 3,
  "goal": "process all CSV files in ./data and write summary to ./output/summary.json",
  "progress": "processed final 2 files (total 7)",
  "result": "summary written to ./output/summary.json with 7 records"
}
```
