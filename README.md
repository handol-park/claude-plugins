# claude-plugins

Handol Park's Claude Code plugin marketplace.

## Installation

```bash
/plugin marketplace add handol-park/claude-plugins
```

## Available Plugins

### rlm-orchestration

RLM-disciplined orchestration — main thread as orchestrator, subagents as workers, task list as call stack. Inspired by [Recursive Language Models (RLM)](https://arxiv.org/abs/2512.24601).

```bash
/plugin install rlm-orchestration@handol-park-plugins
```

**Core Rules:**

| Rule | Description |
|------|-------------|
| **50/2 Rule** | Delegate if >50 lines or >2 files to read |
| **Circuit Breaker** | STOP after >8 Read/Grep calls without delegating |
| **Subagent Returns** | Every dispatch specifies a Return Format (<200 words, file:line refs) |
| **Trampoline** | When subagent reveals deeper complexity, create new tasks — don't expand yourself |

## License

MIT
