#!/usr/bin/env python3
"""Emit read-only, per-album beets state as JSON.

The script deliberately does not run any beets command that changes the
library, tags, artwork, or files. It reads the library configured for the
current beets environment, so callers do not need to know its database path.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from beets import config
from beets.library import Library

MOJIBAKE_MARKERS = ("Ã", "â", "�")


def text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        return os.fsdecode(value)
    return str(value)


def field(model: Any, name: str, default: Any = None) -> Any:
    try:
        return model[name]
    except (KeyError, TypeError):
        return getattr(model, name, default)


def as_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def contains_mojibake(values: list[str | None]) -> bool:
    return any(value and any(marker in value for marker in MOJIBAKE_MARKERS) for value in values)


def album_root(item_paths: list[Path]) -> Path | None:
    if not item_paths:
        return None
    return Path(os.path.commonpath([str(path.parent) for path in item_paths]))


def describe_album(album: Any) -> dict[str, Any]:
    items = list(album.items())
    tracks = []
    item_paths = []
    for item in items:
        path = Path(os.fsdecode(field(item, "path", b"")))
        item_paths.append(path)
        tracks.append(
            {
                "id": as_int(field(item, "id")),
                "disc": as_int(field(item, "disc")),
                "disctotal": as_int(field(item, "disctotal")),
                "track": as_int(field(item, "track")),
                "tracktotal": as_int(field(item, "tracktotal")),
                "title": text(field(item, "title")),
                "artist": text(field(item, "artist")),
                "path": str(path),
            }
        )

    root = album_root(item_paths)
    artpath_value = field(album, "artpath")
    artpath = Path(os.fsdecode(artpath_value)) if artpath_value else None
    display_values = [
        text(field(album, "album")),
        text(field(album, "albumartist")),
        *(track["title"] for track in tracks),
        *(track["artist"] for track in tracks),
        *(track["path"] for track in tracks),
    ]
    issues = []
    if contains_mojibake(display_values):
        issues.append("possible-mojibake")
    mb_albumid = text(field(album, "mb_albumid"))
    if not mb_albumid:
        issues.append("missing-mb-release-id")
    elif mb_albumid.startswith(("http://", "https://")):
        issues.append("url-valued-mb-release-id")
    if any(track["disc"] == 0 for track in tracks):
        issues.append("disc-zero")
    disc_totals = {track["disctotal"] for track in tracks if track["disctotal"] is not None}
    if len(disc_totals) > 1:
        issues.append("inconsistent-disc-total")
    if any(path.name.lower().endswith(".1.flac") for path in item_paths):
        issues.append("collision-suffix")
    if not artpath or not artpath.is_file():
        issues.append("missing-or-stale-art")
    if artpath and root and artpath.parent != root and any((root / f"Disc {n}").is_dir() for n in range(1, 100)):
        issues.append("art-not-at-album-root")

    return {
        "album_id": as_int(field(album, "id")),
        "album": text(field(album, "album")),
        "albumartist": text(field(album, "albumartist")),
        "year": as_int(field(album, "year")),
        "label": text(field(album, "label")),
        "catalognum": text(field(album, "catalognum")),
        "mb_albumid": mb_albumid,
        "album_root": str(root) if root else None,
        "artpath": str(artpath) if artpath else None,
        "art_exists": bool(artpath and artpath.is_file()),
        "track_count": len(tracks),
        "tracks": tracks,
        "issues": issues,
    }


def matches(album: Any, album_name: str | None, artist: str | None) -> bool:
    if album_name and text(field(album, "album", "")).casefold() != album_name.casefold():
        return False
    if artist and text(field(album, "albumartist", "")).casefold() != artist.casefold():
        return False
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--album", help="Exact album title, case-insensitive")
    scope.add_argument("--all", action="store_true", help="Inspect every album")
    parser.add_argument("--artist", help="Exact album artist, case-insensitive")
    parser.add_argument("--limit", type=int, help="Maximum albums in output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.limit is not None and args.limit < 1:
        raise SystemExit("--limit must be positive")
    try:
        library = Library(config["library"].as_filename())
        albums = [album for album in library.albums() if matches(album, args.album, args.artist)]
    except Exception as exc:
        print(f"Could not open the configured beets library: {exc}", file=sys.stderr)
        return 2
    if args.limit:
        albums = albums[: args.limit]
    json.dump([describe_album(album) for album in albums], sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
