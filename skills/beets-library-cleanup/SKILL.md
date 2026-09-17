---
name: beets-library-cleanup
description: Conservatively audit and clean an existing beets music library album by album. Use for release matching, tag and filename cleanup, artwork checks, and cleanup prioritization, not bulk retagging.
---

# Beets library cleanup

Use this skill for an existing beets library. The aim is a correct, pleasant library, not maximum retagging. Preserve known-good metadata and treat one album as the unit of any persistent change.

## Start safely

Choose the mode from the request. Default to `guided`.

- `audit` may inspect the whole library and build a queue. It must not change the database, tags, paths, artwork, or files.
- `guided` works one album at a time. Pause for any real release-identity or manual metadata decision. Once that decision is settled, run the ordinary verification and cleanup commands without asking between every deterministic step.
- `auto-safe` processes an album only when its release candidate, track order, disc structure, previews, and provenance are unambiguous. Skip every other album unchanged and report why.

Never run an unattended library-wide `beet write`, `beet move`, import, or mass retag. Do not use a filesystem path to reimport an album already in the library. Use the library query form with `-L` instead.

Discover the current beets configuration and library at runtime. Do not assume a mount path. Confirm that the expected plugins and path rules are present before relying on them. Read [the policy reference](references/library-policy.md) before making any change.

## Discover and select work

For a library-wide audit or queue, use the included read-only inspector. It loads beets' configured library and emits one JSON object per album:

```sh
python3 skills/beets-library-cleanup/scripts/album_state.py --all > /tmp/beets-albums.json
```

It flags observable signals such as mojibake, missing art, `disc=0`, and `.1.flac` collisions. It does not decide release identity. Prioritize clear mojibake, artist or album-artist inconsistency, absent or suspicious release identity, disc problems, missing art, pending moves, then cosmetic work. Use `beet ls` to inspect candidates in detail.

Select the next album from that queue, but persist changes and verify results for only that album. Keep a short run record with `DONE`, `NEEDS REVIEW`, and `SKIPPED` entries and their reasons.

## Per-album workflow

1. Inspect the current fields, paths, and disc structure. For repeatable structured output, run `album_state.py --album "Album Name"`. Also use a rich `beet ls` listing when evaluating metadata.
2. For an album already catalogued, ask beets for candidates with `beet import -a -W -C -M -L album:"Album Name"`. Do not accept the first or highest-scoring candidate by default.
3. Compare candidate release structure with the local files. If a better MusicBrainz release is known, compare it with `--search-id MUSICBRAINZ_RELEASE_UUID`. Prefer structural and provenance evidence over score.
4. Apply only under the selected mode. After applying, verify track and disc numbering. Use `beet modify -M -W` for deliberate database-only exceptions before the tag-write stage.
5. Always run `beet write -p album:"Album Name"` before `beet write album:"Album Name"`. Stop on a surprising diff.
6. Always run `beet move -p album:"Album Name"` before `beet move album:"Album Name"`. Check the preview again afterward. Let beets resolve a known `.1.flac` collision with scoped move passes until it reports `Moving 0 items`. Never delete collision files by hand first.
7. Check `$artpath`. Fetch art only when it is absent or invalid, then confirm that the configured `albumrootart` behavior puts multi-disc artwork at the album root. `beet fetchart -q` is not a dry run.
8. Mark the album done only after tags, paths, artwork, and completeness check out.

For command forms, decision rules, exceptions, and the full definition of done, read [the policy reference](references/library-policy.md).

## Pause and defer

In `guided`, ask before choosing among plausible pressings, accepting unexplained unmatched or missing tracks, changing numbering or discs, making an unestablished title override, accepting a large tag diff, resolving an ambiguous duplicate prompt, or deleting or replacing files.

In `auto-safe`, skip the album without any persistent change when any of those conditions appears. Typical review reasons include a later reissue scoring above an original-era release, hidden-track ambiguity, a missing bonus disc, unmatched local tracks, a numbering mismatch, an unapproved display-title choice, unexpected preview changes, or a duplicate prompt.

## Examples

- "Audit my library and prioritize cleanup."
- "Clean the next 10 albums in guided mode."
- "Process everything auto-safe and show me what still needs review."
