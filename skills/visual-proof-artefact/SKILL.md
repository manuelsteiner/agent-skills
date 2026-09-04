---
name: visual-proof-artefact
description: Create and share a visual proof artefact for GUI work in a T3 Code session when the user asks or visual evidence is needed.
---

# Visual proof artefact

## Prerequisites

Use this skill only when `T3CODE_HOME` is set to a non-empty value. If it is
unset, stop without capturing, uploading, or embedding an image.

This skill requires `share-verification-artefact` on `PATH`. It accepts one
local image path and prints one HTTPS URL. If the command is unavailable or
fails, report that and do not use another upload mechanism.

## When to create an artefact

Create one when the user explicitly asks to see, check, or verify a visual
result, or when a completed GUI change needs visual evidence to establish the
requested result.

Do not create one for ordinary code, backend, or text-only changes. Do not
upload every intermediate state. One final image is normally enough.

## Capture and share

Capture only the state that proves the relevant result. Use the environment's
available visual capture method. The result must be a local image file.

Do not upload an image containing credentials, tokens, personal data, billing
details, or other sensitive material unless the user explicitly asks for it.

Run the helper with the absolute image path. Treat its complete standard output
as the URL:

```sh
share-verification-artefact /absolute/path/to/image.png
```

Embed the URL as a linked inline image:

```md
[![Verification: concise description](URL)](URL)
```

If nested image links do not render, use `![Verification: concise description](URL)`.
State what the image verifies. Do not claim a result the image does not show.
