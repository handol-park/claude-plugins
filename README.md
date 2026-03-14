# claude-plugins

Handol Park's Claude Code plugin marketplace.

## Prerequisites

- **Bash** — Git Bash (bundled with Git for Windows) or WSL on Windows; native on macOS/Linux
- **Python** (optional, 3.x recommended) — used by session hooks for JSON escaping if available; pure-bash fallback included

## Installation

```bash
/plugin marketplace add handol-park/claude-plugins
```

## Plugins

| Plugin              | Description                                                                                                     |
| ------------------- | --------------------------------------------------------------------------------------------------------------- |
| [rlm](plugins/rlm/) | RLM-disciplined orchestration — subagent delegation via 50/2 rule, circuit breaker, and trampoline pattern      |
| [kw](plugins/kw/)   | Knowledge Workflow — taskwarrior + zettelkasten integration for task management, context recall, and reflection |

## License

MIT
