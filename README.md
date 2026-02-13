# claude-plugins

Handol Park's Claude Code plugin marketplace.

## Prerequisites

- **Bash** — Git Bash (bundled with Git for Windows) or WSL on Windows; native on macOS/Linux
- **Python** (optional, 3.x recommended) — used by session hooks for JSON escaping if available; pure-bash fallback included

## Installation

```bash
/plugin marketplace add handol-park/claude-plugins
```

## Available Plugins

### rlm

RLM-disciplined orchestration — main thread as orchestrator, subagents as workers, task list as call stack. Inspired by [Recursive Language Models (RLM)](https://arxiv.org/abs/2512.24601).

```bash
/plugin install rlm@handol-park-plugins
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
