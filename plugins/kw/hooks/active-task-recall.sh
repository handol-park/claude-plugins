#!/usr/bin/env bash
# SessionStart hook: check for active zk task notes and recall relevant context

# Require zk
if ! command -v zk >/dev/null 2>&1; then
  exit 0
fi

# Get active tasks from zk vault
active=$(zk list gtd/tasks -t "active" --format "{{filename-stem}}|{{title}}|{{filename}}" --quiet 2>/dev/null)
if [ -z "$active" ]; then
  exit 0  # No active tasks, silent
fi

# Build context from active tasks
context="## Active Tasks"
notes=""

while IFS='|' read -r id title filename; do
  [ -z "$id" ] && continue

  # Extract project from frontmatter
  task_file="$HOME/notes/gtd/tasks/${filename}"
  project=""
  if [ -f "$task_file" ]; then
    project=$(sed -n 's/^project: *//p' "$task_file" | head -1)
  fi

  line="- [[${id}]] ${title}"
  [ -n "$project" ] && line="$line (project: ${project})"
  context="$context
$line"

  # Search zettels for relevant notes
  if [ -n "$title" ]; then
    hits=$(zk list zettels --match "$title" --format "- [[{{filename-stem}}]] {{title}}" --limit 3 --quiet 2>/dev/null)
    [ -n "$hits" ] && notes=$(printf '%s\n%s' "$notes" "$hits")
  fi

  # Check for project dashboard
  if [ -n "$project" ]; then
    proj_file="$HOME/notes/gtd/projects/${project}.md"
    if [ -f "$proj_file" ]; then
      context="$context
  - Project dashboard: \`${proj_file}\`"
    fi
  fi
done <<< "$active"

# Deduplicate and add relevant notes
if [ -n "$notes" ]; then
  notes=$(echo "$notes" | grep -v '^$' | sort -u | head -5)
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
