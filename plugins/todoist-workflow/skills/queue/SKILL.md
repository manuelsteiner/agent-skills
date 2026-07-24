---
name: queue
description: Work a task from the Todoist delegation queue for this repo.
argument-hint: [project-name]
disable-model-invocation: true
allowed-tools: Bash(pwd), Bash(git remote get-url origin), Bash(grep:*), Bash(head:*)
---

# Todoist queue

## Prerequisite

Needs the Todoist MCP server. If no Todoist tools are available, stop and tell
the user to install Doist's connector plugin:

```
/plugin marketplace add doist/todoist-mcp
/plugin install todoist@doist
```

Then `/mcp` to complete the OAuth flow. Do not proceed without it, and do not
infer work from the codebase instead.

## Repo identity

**Directory:** !`pwd`

Before resolving the project, also check for a git remote and repo manifest.
Each of these is commonly absent — a failed command or missing file means
that signal is unavailable, not an error condition. Don't stop or report a
problem over it:

- `git remote get-url origin`
- `composer.json` / `package.json` — the `name` field, if the file exists
- `README.md` — the first heading, if the file exists

## 1. Resolve the project

Follow [references/project-matching.md](../../references/project-matching.md).
Arguments passed to this skill are the project name.

## 2. Fetch the queue

Open, incomplete tasks in that project carrying the `ClaudeCode` label. Include
descriptions — they hold the brief.

Empty queue: say so and stop.

## 3. Pick one task

Order by priority (p1 first), then oldest first within a priority.

- **One task** — confirm before starting.
- **Several** — present up to ten via the `AskUserQuestion` tool, each option
  labelled with priority and a one-line gist. Offer to page if more. Do not
  choose.

One task per invocation. If asked for several, do the first, report, and let the
user re-invoke. Keeps commits and review scoped.

## 4. Plan before editing

Fetch the task's comments before planning. Clarifications, decisions and links
to supporting material are often added there rather than in the description, and
the newest comment may supersede the original brief.

If the description or a comment points at a file in the repo — a proposal, a
reference implementation, a spec — read it. Treat it as a starting point to
evaluate against the current code, not as something to apply wholesale.

Read the description, then investigate the actual code.

Descriptions may carry a `Hint:` section. **Hints are leads to verify, not
specifications.** They were written without reading the codebase. Confirm the
described cause is real before acting on it; if it isn't, say so and proceed from
what you found.

State the plan and get agreement before changing anything, unless the task is
small and unambiguous.

## 5. Implement

Follow existing repo conventions. Stay in scope — note adjacent problems for
`/todoist:capture` at the end rather than fixing them silently.

If the task is substantially bigger than its description implies, stop and report
instead of pressing on.

## 6. Report back

Summarise what changed and which files were touched.

Then offer next steps via the `AskUserQuestion` tool (multi-select), acting only
on explicit confirmation:

- **Commit** the changes with a concise commit message.
- **Comment on the task** with a one-paragraph summary and the commit SHA. This
  needs a commit to exist first — if "Commit" wasn't selected and no commit
  exists yet for this work, commit before writing the comment.
- **Complete the task** — only when the user confirms it is verified. Never on
  your own judgement. Passing tests are not evidence the user's intent was met.

Partial work: offer to update the description with what remains, not to complete.

## Constraints

- Never modify Todoist tasks other than the one being worked.
- Never delete tasks, labels or projects.
- An unclear task is a signal to ask, not licence to pick a direction.
