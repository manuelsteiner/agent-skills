# claude-plugins

Personal Claude Code plugin marketplace.

## Install

```
/plugin marketplace add manuelsteiner/claude-plugins
/plugin install todoist-workflow@manuelsteiner-claude-plugins
```

`todoist-workflow` needs the Todoist connector, which is maintained by Doist:

```
/plugin marketplace add doist/todoist-mcp
/plugin install todoist@doist
```

Connector config is deliberately not vendored here — Doist maintains the
endpoint, so their plugin stays current when it changes.

## Plugins

| Plugin             | Skills                                              |
| ------------------ | --------------------------------------------------- |
| `todoist-workflow` | `/todoist-workflow:queue`, `/todoist-workflow:capture` |
| `unslop`           | `/unslop:unslop`                                    |

## Adding a plugin

1. Create `plugins/<name>/.claude-plugin/plugin.json`
2. Add skills under `plugins/<name>/skills/<skill>/SKILL.md`
3. Register it in `.claude-plugin/marketplace.json`
4. Bump the plugin `version` so existing installs pick up the change

Plugin `name` values are immutable slugs. Renaming one breaks existing installs
unless you add a `renames` entry to `marketplace.json`. Avoid names that clash
with plugins from other marketplaces, since skills are namespaced by plugin name.
