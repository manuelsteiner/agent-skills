# Library policy and command reference

Read this reference before changing a beets library with this skill.

## Required configuration guardrails

Inspect the active configuration before work. Do not silently rewrite it. The expected plugins are `musicbrainz`, `bandcamp`, `fetchart`, `edit`, `duplicates`, `ftintitle`, `inline`, `zero`, and `albumrootart`. The custom `albumrootart.py` belongs directly in `~/.config/beets/plugins`, not a nested `beetsplug` directory.

Imports must remain conservative: no automatic copy, move, write, or autotag, and duplicate handling must ask. Multi-disc paths need per-disc numbering and an `Artist/Album/Disc N/NN - Title` form. The active `replace` configuration must make Windows-invalid characters, control characters, leading dots, leading hyphens, and edge whitespace safe for exFAT.

Keep `fetchart` cautious and opt-in. It should use filesystem, `cover_art_url`, Cover Art Archive release or release-group art, and iTunes. It must not list Bandcamp directly as a fetchart source.

## Release identity comes first

Choose the release that describes the files, not the candidate with the best beets score. Strong evidence is exact track and disc structure, durations, hidden or silent tracks, original release era, catalog or barcode, label, country, and bonus-track structure. Score alone, the first result, a later reissue, or a current canonical artist name are weak evidence.

Prefer, in order, an exact MusicBrainz release, a same-era release with the same structure, then the closest plausible release when the provenance cannot be known. Do not invent certainty. If no credible MusicBrainz release fits, use careful manual cleanup rather than attaching a false MBID.

Bandcamp is acceptable for a known Bandcamp download or when MusicBrainz has no suitable release. Keep Bandcamp URLs in the beets database as provenance if useful, but never write them to `MUSICBRAINZ_*ID` file tags. Verify that `zero` remains enabled with URL patterns for `mb_albumartistid`, `mb_albumartistids`, `mb_albumid`, `mb_artistid`, `mb_artistids`, `mb_releasegroupid`, `mb_releasetrackid`, and `mb_trackid`. Its database-update setting must leave database provenance intact. The plural fields matter because mediafile may regenerate artist-ID tags from them.

Preserve deliberate display choices. Release-era display names can be preferable to a later canonical rename, such as `Machine Gun Kelly` instead of `mgk`. Keep meaningful hidden-track titles and intentional concise titles. Do not replace correct metadata for cosmetic conformity.

## Inspect and evaluate

Use scoped queries. Quote album names as needed for the active shell.

```sh
beet ls -f '$track :: $title :: $artist :: $albumartist :: $year-$month-$day :: $label :: $catalognum :: $genre :: $path' album:"Album Name"
beet ls -f '$disc/$disctotal :: $track/$tracktotal :: $title :: $path' album:"Album Name"
beet import -a -W -C -M -L album:"Album Name"
beet import -a -W -C -M -L --search-id MUSICBRAINZ_RELEASE_UUID album:"Album Name"
```

The `-L` form targets the existing library record. Do not reimport its filesystem path. If beets asks whether to skip, merge, remove, keep, or upgrade the same physical files, do not choose `Merge all` reflexively. It can create a doubled candidate. Defer an ambiguous duplicate prompt.

Evaluate track count and order, disc count and numbering, title changes, missing and unmatched tracks, hidden tracks, date, country, label, catalog number, barcode, medium, and whether a candidate is an unsuitable later reissue. A structurally correct original-era release is better than a wrong reissue.

Silent tracks are not an error by themselves. For example, a local copy of `Korn - Follow the Leader` may store audible tracks 13 through 25 while beets reports the first twelve silent tracks as missing. Preserve `13/25` through `25/25`; do not renumber it to make the warning disappear.

## Deliberate manual edits

Use `beet modify -M -W` for DB-only corrections before the write stage. Do not omit those flags.

```sh
beet modify -M -W album:"Life Is Peachy" track:14 title="Kill You"
beet modify -M -W album:"Korn" track:13 title="Michael & Geri"
beet modify -M -W album:"Chocolate Starfish And The Hot Dog Flavored Water" disc:0 disc=1 disctotal=2
```

Use manual edits sparingly. Preferred visible featured-artist style is `Title (feat. Guest)`. The `ftintitle` plugin uses artist credits. Do not add `feat.` because another person appears only in performer, writer, or relationship metadata. Normalize genres to useful lower-case values such as `hip hop` when the evidence supports it.

## Write, move, and collision passes

Every persistent action is album-scoped and previewed:

```sh
beet write -p album:"Album Name"
beet write album:"Album Name"
beet move -p album:"Album Name"
beet move album:"Album Name"
beet move -p album:"Album Name"
```

Review tag previews for bad title, artist, date, edition, numbering, or MBID changes. Review path previews for only expected normalization. Case-only renames can create `.1.flac` files. If the next preview shows `foo.1.flac -> foo.flac`, run another scoped `beet move` and preview again. Repeat only until it says `Moving 0 items`. Never delete a collision file before beets has reconciled it.

The library uses exFAT-safe paths. Characters that exFAT rejects may be replaced in filenames while remaining correct in embedded titles. A title such as `High Life?` may intentionally map to `High Life_.flac`. Do not edit good tag text to match the sanitized filename.

For multi-disc releases, preserve per-disc numbering and the configured `Artist/Album/Disc N/NN - Title` layout. Verify disc assignments before moving. Do not change a layout until disc metadata is correct.

## Artwork

Check art with:

```sh
beet ls -af '$artpath' album:"Album Name"
```

If it is blank, stale, or missing on disk, run `beet fetchart album:"Album Name"`, then check again. `fetchart -q` may write artwork, so it is never a dry run. The configured sources should not list Bandcamp directly. For multi-disc releases, `albumrootart` must move fetched art out of `Disc N` to the album root and update `$artpath`. Inspect unknown `._*` or `.beets` files first. Do not delete them automatically.

## Definition of done

An album is done when its chosen release is correct or explicitly the best available match; display names and titles are intentional; feature credits, genre, tracks, and discs are correct; tags have been written; paths are exFAT-safe; no move remains; no `.1.flac` artifact remains; and `$artpath` points to usable album-root `cover.jpg`. Confirm that URL-shaped fake MusicBrainz IDs did not land in file tags.
