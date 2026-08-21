# Resolving the Todoist project for a repository

Used by both Todoist skills. Keep the behaviour identical in both.

## Inputs

The current directory is available from `pwd`. Gather the remaining signals:
the git remote, `composer.json` or `package.json` name, and README heading.
Missing files and failed commands mean that signal is unavailable and are not
errors.

If no repository identity can be gathered, do not guess. Ask the user which
project to use.

## Rules

1. If the user supplied a project name, use it without matching.
2. Otherwise list Todoist projects and compare them with repository identity.
   Projects may be nested; match their leaf name, not the full path.
3. Accept a match only with corroborating evidence:
   - an exact, case-insensitive name match; or
   - a repository package name, Composer name, or git-remote slug matching the
     project.
4. A generic directory name such as `app`, `src`, `web`, `api`, `code`, or
   `dev` is never enough evidence alone.

## Outcomes

- One corroborated match: use it and state which project was chosen.
- Several candidates or only a fuzzy match: present the candidates and ask the
  user to choose. Never choose silently.
- Nothing plausible: say so, present the project list, and offer to create one.
  Do not proceed based on codebase inspection alone.

Always name the resolved project in the response so a wrong match is visible
before a write occurs.
