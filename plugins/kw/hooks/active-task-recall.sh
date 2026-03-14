#!/usr/bin/env bash
# SessionStart hook: check for active taskwarrior tasks and recall relevant zk notes

# Get active task(s)
active_json=$(task +ACTIVE export 2>/dev/null)
active_count=$(echo "$active_json" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
if [ "$active_count" = "0" ]; then
  exit 0  # No active task, no output — hook is silent
fi

# Extract first active task's metadata
description=$(echo "$active_json" | python3 -c "import sys,json; t=json.load(sys.stdin)[0]; print(t.get('description',''))" 2>/dev/null)
project=$(echo "$active_json" | python3 -c "import sys,json; t=json.load(sys.stdin)[0]; print(t.get('project',''))" 2>/dev/null)
tags=$(echo "$active_json" | python3 -c "import sys,json; t=json.load(sys.stdin)[0]; print(' '.join(t.get('tags',[])))" 2>/dev/null)
task_id=$(echo "$active_json" | python3 -c "import sys,json; t=json.load(sys.stdin)[0]; print(t.get('id',0))" 2>/dev/null)

# Search zk for relevant notes
notes=""
if command -v zk >/dev/null 2>&1; then
  # Search by description keywords
  if [ -n "$description" ]; then
    hits=$(zk list --match "$description" --format "- [[{{id}}]] {{title}}" --limit 5 2>/dev/null)
    [ -n "$hits" ] && notes="$hits"
  fi
  # Search by project tag
  if [ -n "$project" ]; then
    proj_hits=$(zk list --tag "$project" --format "- [[{{id}}]] {{title}}" --limit 3 2>/dev/null)
    [ -n "$proj_hits" ] && notes=$(printf '%s\n%s' "$notes" "$proj_hits")
  fi
  # Deduplicate
  if [ -n "$notes" ]; then
    notes=$(echo "$notes" | sort -u | head -5)
  fi
fi

# Check for GTD project note
gtd_note=""
if [ -n "$project" ]; then
  # Use top-level name for dotted subprojects (e.g., saccade.l4 → saccade)
  top_project="${project%%.*}"
  gtd_file="$HOME/notes/gtd/projects/${top_project}.md"
  if [ -f "$gtd_file" ]; then
    gtd_note="- GTD project note: \`${gtd_file}\` (read for Outcome, Status, Next Actions)"
  fi
fi

# Build context string
context="## Active Task (#${task_id}): ${description}"
[ -n "$project" ] && context="$context (project:${project})"
[ -n "$tags" ] && context="$context [${tags}]"
if [ -n "$gtd_note" ]; then
  context="$context

**GTD project:**
$gtd_note"
fi
if [ -n "$notes" ]; then
  context="$context

**Relevant notes** (use Read to load if needed):
$notes"
fi

# JSON escape
json_escape() {
  printf '%s' "$1" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))' 2>/dev/null
}

escaped=$(json_escape "$context")

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": ${escaped}
  }
}
EOF
