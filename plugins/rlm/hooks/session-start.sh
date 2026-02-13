#!/usr/bin/env bash
# RLM Orchestration — SessionStart hook
# Injects orchestrator discipline into every session (startup, resume, clear, compact)

CONTENT=$(cat <<'RULES'
## RLM Orchestration Mode (DEFAULT)

You are an ORCHESTRATOR. Decompose, dispatch, synthesize. Never accumulate raw context.

**50/2 Rule**: >50 lines or >2 files → delegate to subagent.
**Circuit Breaker**: >8 Read/Grep calls without delegating → STOP, restructure as subagent dispatch.
**Returns**: Every subagent prompt MUST specify Return Format. Default: summary <200 words, file:line refs.
**Task List = Call Stack**: Encode decomposition as tasks with blockedBy. Deeper complexity → new tasks + new subagents (trampoline).

DO directly: interpret intent, read small files (<50 lines), manage task list, synthesize summaries, write to external files.
NEVER: read large files, explore file-by-file, chain Read/Grep for analysis — always delegate with focused query.

Use `rlm` skill for: delegation decisions, prompt templates, anti-patterns, skill integration.
RULES
)

# Escape content as JSON string
# Try Python first (most robust), fall back to pure bash
json_escape_python() {
  local py=""
  if python3 --version >/dev/null 2>&1; then py="python3"
  elif python --version >/dev/null 2>&1; then py="python"
  else return 1; fi
  printf '%s' "$1" | "$py" -c 'import sys,json; print(json.dumps(sys.stdin.read()))'
}

json_escape_bash() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\r'/}"
  s="${s//$'\t'/\\t}"
  printf '"%s"' "$s"
}

ESCAPED=$(json_escape_python "$CONTENT" 2>/dev/null) || ESCAPED=$(json_escape_bash "$CONTENT")

cat <<EOF
{
  "hookSpecificOutput": {
    "additionalContext": ${ESCAPED}
  }
}
EOF
