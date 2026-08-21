---
name: todoist-queue
description: Work one delegated Todoist task for the current repository.
---

# Todoist queue

## Prerequisite

Needs a configured Todoist integration. If no Todoist tools are available, say
so and stop. Do not infer work from the codebase instead.

## Repository identity

Gather the current directory with `pwd`. Before resolving the project, also
check the git remote and repository metadata. A failed command or missing file
simply means that signal is unavailable, not an error:

- `git remote get-url origin`
- `composer.json` or `package.json` — use the `name` field if present
- `README.md` — use the first heading if present

## 1. Resolve the project

Follow [the project-matching rules](../references/todoist-project-matching.md).
Arguments passed to this skill are the project name.

## 2. Fetch the queue

Fetch open, incomplete tasks in that project carrying the `Agent` label,
including their descriptions.

If the queue is empty, say so and stop.

## 3. Pick one task

Order tasks by priority, p1 first, then by age within each priority.

- For one task, confirm before starting.
- For several tasks, present up to ten choices with their priority and a
  one-line summary. Offer to page through more tasks. Do not choose for the
  user.

Work one task per invocation. If asked for several, complete the first, report,
and ask the user to invoke the skill again.

## 4. Plan before editing

Fetch the task's comments before planning. Clarifications, decisions, and links
to supporting material may supersede the description.

Read any repository file linked from the description or comments. Treat it as a
starting point to evaluate against the current code, not something to apply
wholesale.

Read the description, then investigate the actual code. A `Hint:` is a lead to
verify, not a specification. Confirm the stated cause before acting; if it is
wrong, say so and proceed from what you found.

State the plan and get agreement before changing anything unless the task is
small and unambiguous.

## 5. Implement

Follow existing repository conventions. Stay in scope and capture adjacent
problems for `todoist-capture` rather than fixing them silently.

If the task is substantially larger than described, stop and report it.

## 6. Report back

Summarise what changed and which files were touched. Offer these next steps and
act only on explicit confirmation:

- Commit the changes with a concise commit message.
- Comment on the task with a one-paragraph summary and the commit SHA. Commit
  first if needed.
- Complete the task only when the user confirms it is verified. Passing tests
  alone do not establish that the user's intent was met.

For partial work, offer to update the description with what remains rather than
completing the task.

## Constraints

- Never modify Todoist tasks other than the one being worked.
- Never delete tasks, labels, or projects.
- An unclear task is a signal to ask, not a licence to pick a direction.
