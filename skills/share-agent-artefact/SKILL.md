---
name: share-agent-artefact
description: Share a final agent-created file with the user in a T3 Code session when remote download is needed.
---

# Share agent artefact

## Prerequisites

Use this skill only when `T3CODE_HOME` is set to a non-empty value. If it is
unset, do not upload or link a file.

This skill requires `share-agent-artefact`. Resolve it in this order:

1. The executable path in `AGENT_ARTEFACT_HELPER`, if set.
2. `share-agent-artefact` on `PATH`.
3. `$HOME/.local/bin/share-agent-artefact`, if it is executable.

It accepts one local file path and prints one HTTPS URL. If no helper is
available or it fails, report that and do not use another upload mechanism.

## When to share

Share a final file the agent created specifically as the user's deliverable
when the user needs to retrieve it remotely, or when the user explicitly asks
to share a file.

Do not upload ordinary source files, intermediate output, or arbitrary local
files merely because they were mentioned. Use `share-visual-proof-artefact` for
visual evidence and inline image previews.

Do not upload credentials, tokens, private configuration, personal data, or
other sensitive content unless the user explicitly asks for that exact file.

## Share and link

Run the resolved helper with the absolute file path. Treat its complete
standard output as the URL:

```sh
"$artefact_helper" /absolute/path/to/final-file.ext
```

Link the returned URL in Markdown using the file's basename:

```md
[Download: final-file.ext](URL)
```

State what the file contains. If you created the file or a temporary directory
solely for this request, remove it after the upload attempt. Never delete a
user-provided file or an existing project file.
