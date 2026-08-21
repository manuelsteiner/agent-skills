---
name: todoist-capture
description: Turn things noticed during this session into Todoist tasks for the current repository.
---

# Todoist capture

## Prerequisite

Needs a configured Todoist integration. If no Todoist tools are available, say
so and report what would have been created. Do not silently discard the
capture.

## Repository identity

Gather the current directory with `pwd`. Before resolving the project, also
check the git remote, current commit, and a repository manifest. A failed
command or missing file simply means that signal is unavailable, not an error:

- `git remote get-url origin`
- `git rev-parse --short HEAD`
- `composer.json` or `package.json` — use the `name` field if present

## 1. Resolve the project

Follow [the project-matching rules](../references/todoist-project-matching.md).
Arguments are the thing to capture, not a project name. If the project cannot
be resolved, ask before continuing.

## 2. Gather candidates

**With arguments** — capture that one thing.

**Without arguments** — sweep the session for things worth recording:

- problems you flagged but deliberately left alone
- things the user said were for later
- follow-ups implied by work that was done

Only capture things actually observed or stated in this session. Do not invent
plausible improvements. If nothing qualifies, say so.

## 3. Check for duplicates

Search open tasks in the project before proposing anything. If something
nearly matches an existing task, identify it and offer to skip it or add a
comment to it instead of creating a duplicate.

## 4. Propose, then write

Present the list for approval before creating anything. For each task provide:

- **Title** — one specific line that states the problem, not the fix
- **Description** — what was observed, where, and why it matters; include file
  and line references plus the commit SHA when available
- **Priority** — p4 unless the user says otherwise
- **`Agent` label** — only for self-contained work an agent could pick up cold;
  do not label work that needs a design decision, judgement call, or discussion

Let the user drop, edit, or reprioritise proposals. Create the approved set in
one batch of at most 25 tasks. Confirm what was created and where.

## Constraints

- Never modify or complete existing tasks; only create them, or comment on a
  duplicate when the user asks.
- Never create tasks in a project that was not confirmed.
