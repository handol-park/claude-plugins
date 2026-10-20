---
name: issue
description: Draft and file a well-defined GitHub issue — walks the author through root cause, evidence (including a search for earlier attempts), outcome requirements R1..Rn, scope with named exclusions, alternatives scored against the requirements, and falsifiable acceptance criteria, then files it via the REST API after the user confirms. Use when the user says "file an issue", "draft an issue", "open a ticket", or invokes /gh:issue.
---

# Issue

Refine the problem before anything is built. An issue is the contract its PR is
reviewed against: the PR maps each change back to the issue's requirement IDs, so
a vague issue produces a PR that gets refined in review instead.

An issue body states the **problem**; the PR body states the **solution**. Same
what/why-vs-how split as a spec and its implementation plan.

## Input

`<owner>/<repo>` (ask if not given) and a one-line problem. Optional `type=` —
only for an organization repo that defines issue types; check with
`gh api orgs/<owner>/issue-types --jq '.[].name'`, and skip it for a user-owned
repo.

## Step 1 — Walk the author through the body, in this order

Ask for each section in turn and draft from the answers. Do not skip ahead to a
solution: an answer offered to an open question enters as a **candidate** under
Alternatives, not as a requirement.

1. **Problem** — the root cause, not the symptom or the fix. Ask "why does this
   happen?" until the answer names something that, if changed, removes the symptom.
2. **Evidence** — what was observed, with its grounding: a command and its output,
   a `file:line`, a query, a linked issue/PR (`owner/repo#N (short tag)`). Say what
   was not verified. Search for earlier attempts at the same problem — issues and
   PRs, open or closed (`gh search issues --repo <owner>/<repo> "<keywords>"`, then
   `gh search prs`), and any decision records the repo keeps — and list each one
   found, with what became of it; the implementing PR references them too. Say
   which searches ran, so "none found" can be checked.
3. **Requirements `R1..Rn`** — outcomes, with RFC 2119 keywords, not mechanisms.
   Apply the **deletion test** to each: if removing it would change nothing the
   problem needs, cut it; if it names *how*, rewrite it as *what*.
4. **Scope** — a rule for what is in, plus **named** exclusions (what is out, and
   why), never an open-ended list.
5. **Alternatives** — a table of options, each scored against every `R`, including
   process cost (reviews, approvals, releases). Carry any candidate answers from
   above.
6. **Acceptance criteria** — written as GitHub task-list items (`- [ ]`), each one
   falsifiable by a check someone can run, and each traceable to an `R`. The
   implementing PR references the issue without a closing keyword unless every
   criterion is already checked before the merge; otherwise close the issue by
   hand once its last criterion is checked.

The body states **current state** only: edit it in place as things change, and
record history (what changed, when) as comments — no dated `Refreshed` blocks,
no folded prior versions. Solution detail (tables of changes, SQL, phases)
belongs in the PR body. A reference that must resolve outside this repo is
written in full as `owner/repo#N`, with a short tag after it.

## Step 2 — Confirm, then file

Write the title and the body to temp files and show the user the full title and
body. File only after they confirm; a hook letting the call through is not the
user's go-ahead. File through REST, which works the same with or without a type:

```bash
# Write the title with the Write tool, or printf '%s'; no trailing newline.
gh api "repos/<owner>/<repo>/issues" -F title=@<title-file> -F body=@<file> \
  --jq '{number, html_url, type: .type.name}'
# Organization repo with issue types: add  -f type=<Type>
```

`-F` (not `-f`) is what reads a file, and it sends `@file` content as a literal
string, so an apostrophe in the title is safe and `true`, `null` or a number stay
text. It also keeps a trailing newline, which is why the title file has none. Read
the result back — confirm `type` when one was asked for — and report the issue URL.

## Prerequisites

`gh` authenticated against `github.com` with write access to the target repo. With
several `gh` accounts, run the call as the one that has it:
`GH_TOKEN=$(gh auth token --user <login>) gh api ...`.
