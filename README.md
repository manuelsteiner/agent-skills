# agent-skills

Personal, agent-agnostic skills. Each directory in [`skills/`](skills/) is a
portable skill with a `SKILL.md` entry point.

## Install

Point the skill directory used by each agent at this repository's `skills/`
directory. For example:

```sh
ln -s /path/to/agent-skills/skills ~/.agents/skills
ln -s ~/.agents/skills ~/.claude/skills
```

The Todoist skills require a Todoist integration configured for the agent in
use. This repository deliberately does not prescribe a client-specific MCP or
connector configuration.

## Skills

| Skill | Purpose |
| --- | --- |
| `unslop` | Edit writing to remove common AI tells and add human voice. |
| `todoist-capture` | Turn session observations into Todoist tasks for the current repository. |
| `todoist-queue` | Pick up and work one delegated Todoist task for the current repository. |

## Adding a skill

Create `skills/<skill-name>/SKILL.md` with portable YAML frontmatter containing
at least `name` and `description`. Put supporting files beside it or in a shared
subdirectory of `skills/` when several skills need the same reference.
