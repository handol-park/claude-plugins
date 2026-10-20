---
name: pr
description: Draft and open a well-defined GitHub pull request — checks the branch first (linked issue refined, conventional commit subjects, diff size, every change traced to a requirement ID in the issue, sibling PRs editing the same files), drafts a body that states why, maps each change to its requirement, documents how it was tested and calls out breaking changes, picks a closing keyword vs a plain reference by the issue's acceptance criteria, and opens the PR after the user confirms. Use when the user says "open a PR", "draft a PR", "write the PR body", or invokes /gh:pr.
---

# PR

A PR body states the **solution** to the problem its issue states (see
`/gh:issue`). A reviewer reads the body against the issue, so every change in the
diff should trace to one of the issue's requirement IDs, and the body should make
that mapping explicit rather than leave the reviewer to rebuild it.

## Input

`<owner>/<repo>` (default: the current checkout's `origin`), the head branch
(default: the current branch) and the tracking issue (`owner/repo#N`; ask if not
given). Base is the default branch unless the PR builds on an open prerequisite
PR, whose branch is then the base.

## Step 1 — Check the branch

Report each finding to the user; fix what is theirs to fix before drafting.

1. **Issue first** — read the linked issue body. If it has no requirement IDs
   (`R1..Rn`) or no task-list acceptance criteria, say so and offer `/gh:issue`
   to refine it: a PR built before its requirements are settled turns review into
   requirements discovery.
2. **Commits** — every subject since the base follows Conventional Commits,
   `<type>(<scope>): <subject>` (`git log --format=%s origin/<base>..HEAD`).
3. **Size** — `git diff --stat origin/<base>...HEAD`. Over ~500 changed lines,
   propose a split.
4. **Trace** — read the whole diff (the author's self-review) and map every
   change to an `R` in the issue. A change that maps to none is cut, or the
   requirement is added to the issue first — never invented in the PR body.
5. **Siblings** — list open PRs touching the same files:
   `gh pr list --repo <owner>/<repo> --state open --json number,title,files`, then
   intersect with `git diff --name-only origin/<base>...HEAD`. For each overlap,
   settle the merge order and state it in the body.
6. **Verification** — collect the checks that ran (tests, type check, lint,
   runtime output) with their results, and what was not verified.

## Step 2 — Draft the body

In this order, prose unwrapped (one paragraph per line — GitHub renders a hard
wrap as a ragged break):

1. **Banner** — only when something must not be missed: merge order, a blocking
   dependency, a breaking change. A `> ⚠️` line at the very top, because the body
   is always read and comments scroll away.
2. **Why** — the problem in one or two sentences, pointing at the issue.
3. **Changes** — each change with the `R` it implements. A table when there are
   more than three.
4. **Verification** — each check as the command and its result; then what was
   not verified.
5. **Breaking changes** — listed, or `None`.
6. **Issue link** — count the issue's unchecked criteria:

   ```bash
   gh issue view <n> --repo <owner>/<repo> --json body --jq .body \
     | grep -c '^\s*- \[ \]'
   ```

   `Closes owner/repo#N` **only** when that count is 0: GitHub closes the issue
   as completed on merge whatever its criteria say, and a criterion checked
   against the default branch can only be ticked after the merge. Otherwise
   write `Refs owner/repo#N` and close the issue by hand once its last criterion
   is checked.

Leave out anything that may still change after approval, such as a version-bump
level, and carry it as a label. Follow the repo's own `CLAUDE.md` or
`CONTRIBUTING.md` for its versioning and attribution conventions. A reference
that must resolve outside this repo is written in full as `owner/repo#N`, with a
short tag after it.

## Step 3 — Confirm, then open

Write the title and body to temp files and show both to the user. Open only
after they confirm. Open as a draft unless the user says it is ready:

```bash
gh pr create --repo <owner>/<repo> --base <base> --head <branch> --draft \
  --title "$(cat <title-file>)" --body-file <body-file>
```

Read the body back (`gh pr view <n> --repo <owner>/<repo> --json body`) and
report the URL.

## After opening

The body states **current state**: edit it in place as things change, and post
a comment saying what changed — no dated `Refreshed` blocks, no folded prior
versions. If `gh pr edit --body-file` reports success but the body does not
change, edit through REST instead:
`gh api -X PATCH repos/<owner>/<repo>/pulls/<n> -F body=@<file>`. Where pushing
after approval dismisses it, land rework before approval and send late
suggestions to a follow-up issue.

## Prerequisites

`gh` authenticated against `github.com` with write access to the target repo.
With several `gh` accounts, run the calls as the one that has it:
`GH_TOKEN=$(gh auth token --user <login>) gh ...` — and the same prefix on
`git push`, since the `gh` credential helper follows it.
