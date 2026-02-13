# rlm-orchestration

RLM-disciplined orchestration plugin for Claude Code. Enforces the main thread as orchestrator-only: decompose, dispatch subagents, synthesize summaries. Never accumulate raw context.

Inspired by [Recursive Language Models (RLM)](https://arxiv.org/abs/2512.24601).

## What It Does

- **SessionStart hook** injects orchestrator discipline on every session start (including after `/compact` and `/clear`)
- **Skill** provides detailed delegation decision trees, subagent prompt templates, and anti-pattern reference
- **Task list as call stack** — encodes multi-step decomposition as tasks with `blockedBy` relationships, simulating recursive calls through trampolining

## Core Rules

| Rule | Description |
|------|-------------|
| **50/2 Rule** | Delegate if >50 lines or >2 files to read |
| **Circuit Breaker** | STOP after >8 Read/Grep calls without delegating |
| **Subagent Returns** | Every dispatch specifies a Return Format (<200 words, file:line refs) |
| **Trampoline** | When subagent reveals deeper complexity, create new tasks — don't expand yourself |

## Installation

```bash
claude plugin marketplace add hpark/dotfiles
claude plugin install rlm-orchestration@hpark-dotfiles
```

Or add to `settings.json`:

```json
{
  "enabledPlugins": {
    "rlm-orchestration@hpark-dotfiles": true
  }
}
```

## Usage

The hook fires automatically on every session start. The `rlm-orchestration` skill is available for detailed reference when delegation decisions are ambiguous.

Invoke the skill explicitly:

```
/rlm-orchestration
```

## Integration

Works alongside the `superpowers` plugin. Superpowers defines WHAT workflow to follow. RLM defines HOW the orchestrator participates — by delegating, not accumulating.

## License

MIT
