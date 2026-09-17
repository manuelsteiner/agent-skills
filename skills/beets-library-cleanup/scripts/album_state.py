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
import re
import sys
from pathlib import Path
from typing import Any

from beets import config
from beets.library import Library

MOJIBAKE_MARKERS = ("Ã", "â", "�")
MB_RELEASE_ID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
EXCEPTIONS_PATH = Path(__file__).parents[1] / "references" / "settled-library-exceptions.json"
CASEFOLD_CHILDREN: dict[Path, dict[str, Path]] = {}


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


def load_exceptions() -> dict[str, Any]:
    try:
        value = json.loads(EXCEPTIONS_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"artist_normalizations": {}, "albums": []}
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid exception registry {EXCEPTIONS_PATH}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"Exception registry {EXCEPTIONS_PATH} must contain an object")
    value.setdefault("artist_normalizations", {})
    value.setdefault("albums", [])
    return value


def album_root(tracks: list[dict[str, Any]]) -> Path | None:
    item_paths = [Path(track["current_path"]) for track in tracks if track["current_path"]]
    if not item_paths:
        return None
    directories = []
    for track in tracks:
        if not track["current_path"]:
            continue
        path = Path(track["current_path"])
        is_disc_dir = track["disctotal"] and track["disctotal"] > 1 and re.fullmatch(r"Disc \d+", path.parent.name)
        directories.append(path.parent.parent if is_disc_dir else path.parent)
    return Path(os.path.commonpath([str(directory) for directory in directories]))


def casefold_child(parent: Path, name: str) -> Path | None:
    direct = parent / name
    if direct.exists():
        return direct
    try:
        children = CASEFOLD_CHILDREN.setdefault(
            parent, {child.name.casefold(): child for child in parent.iterdir()}
        )
    except OSError:
        return None
    return children.get(name.casefold())


def current_path(database_path: Path, configured_directory: Path) -> Path | None:
    """Resolve a stored path inside beets' active directory without hardcoding a former root."""
    if database_path.is_file():
        return database_path
    parts = [part for part in database_path.parts if part not in {database_path.anchor, "/"}]
    # A normal album path has at least artist, album, and filename. Try the
    # shortest plausible suffix first so a moved library root is ignored.
    for start in range(len(parts) - 3, -1, -1):
        candidate = configured_directory
        for part in parts[start:]:
            child = casefold_child(candidate, part)
            if child is None:
                break
            candidate = child
        else:
            if candidate.is_file():
                return candidate
    return None


def exception_for(album: Any, exceptions: dict[str, Any]) -> dict[str, Any] | None:
    album_name = text(field(album, "album", "")).casefold()
    artist_name = text(field(album, "albumartist", "")).casefold()
    for entry in exceptions["albums"]:
        if not isinstance(entry, dict):
            continue
        if entry.get("album", "").casefold() == album_name and entry.get("albumartist", "").casefold() == artist_name:
            return entry
    return None


def provenance_status(mb_albumid: str | None, exception: dict[str, Any] | None) -> dict[str, Any]:
    if exception:
        return {
            "status": exception["provenance"],
            "source": "settled-exception",
            "notes": exception.get("notes"),
        }
    if mb_albumid and MB_RELEASE_ID_RE.fullmatch(mb_albumid):
        return {"status": "musicbrainz", "source": "mb_albumid", "notes": None}
    if mb_albumid and ".bandcamp.com" in mb_albumid.casefold():
        return {"status": "bandcamp", "source": "bandcamp-url-in-database", "notes": None}
    if mb_albumid:
        return {"status": "conflicting", "source": "unrecognised-mb_albumid", "notes": None}
    return {"status": "unknown", "source": "no-recorded-provenance", "notes": None}


def established_normalizations(album: Any, tracks: list[dict[str, Any]], exceptions: dict[str, Any]) -> list[dict[str, str]]:
    rules = exceptions["artist_normalizations"]
    values = [("albumartist", text(field(album, "albumartist")))]
    values.extend(("track-artist", track["artist"]) for track in tracks)
    normalizations = []
    seen = set()
    for field_name, current in values:
        target = rules.get(current) if current else None
        if target and current != target and (field_name, current) not in seen:
            normalizations.append({"field": field_name, "from": current, "to": target, "status": "established"})
            seen.add((field_name, current))
    return normalizations


def describe_album(
    album: Any, raw_album: Any, configured_directory: Path, exceptions: dict[str, Any]
) -> dict[str, Any]:
    items = list(album.items())
    raw_items = {as_int(field(item, "id")): item for item in raw_album.items()}
    tracks = []
    for item in items:
        item_id = as_int(field(item, "id"))
        raw_item = raw_items.get(item_id, item)
        database_path = Path(os.fsdecode(field(raw_item, "path", b"")))
        resolved_path = current_path(database_path, configured_directory)
        current_exists = resolved_path is not None
        database_exists = database_path.is_file()
        if current_exists:
            path_status = "current"
        elif database_exists:
            path_status = "database-path-only"
        else:
            path_status = "missing"
        database_status = "exists" if database_exists else "relocated" if current_exists else "stale"
        tracks.append(
            {
                "id": item_id,
                "disc": as_int(field(item, "disc")),
                "disctotal": as_int(field(item, "disctotal")),
                "track": as_int(field(item, "track")),
                "tracktotal": as_int(field(item, "tracktotal")),
                "title": text(field(item, "title")),
                "artist": text(field(item, "artist")),
                "path": str(resolved_path or database_path),
                "current_path": str(resolved_path) if resolved_path else None,
                "current_path_exists": current_exists,
                "database_path": str(database_path),
                "database_path_exists": database_exists,
                "database_path_status": database_status,
                "path_status": path_status,
            }
        )

    root = album_root(tracks)
    exception = exception_for(album, exceptions)
    raw_artpath_value = field(raw_album, "artpath")
    raw_artpath = Path(os.fsdecode(raw_artpath_value)) if raw_artpath_value else None
    artpath = current_path(raw_artpath, configured_directory) if raw_artpath else None
    artpath_exists = artpath is not None
    raw_artpath_exists = bool(raw_artpath and raw_artpath.is_file())
    if raw_artpath_exists:
        database_artpath_status = "exists"
    elif artpath_exists:
        database_artpath_status = "relocated"
    elif raw_artpath:
        database_artpath_status = "stale"
    else:
        database_artpath_status = "unset"
    root_cover = root / "cover.jpg" if root else None
    root_cover_exists = bool(root_cover and root_cover.is_file())
    if artpath_exists and root and artpath.parent == root:
        artpath_status = "at-album-root"
    elif artpath_exists:
        artpath_status = "present-outside-album-root"
    elif root_cover_exists:
        artpath_status = "stale-but-root-cover-present"
    elif raw_artpath:
        artpath_status = "stale"
    else:
        artpath_status = "unset"
    artwork_status = "present" if artpath_exists or root_cover_exists else "missing"
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
    provenance = provenance_status(mb_albumid, exception)
    if provenance["status"] == "unknown":
        issues.append("provenance-unknown")
    elif provenance["status"] == "conflicting":
        issues.append("provenance-conflict")
    if any(track["disc"] == 0 for track in tracks):
        issues.append("disc-zero")
    disc_totals = {track["disctotal"] for track in tracks if track["disctotal"] is not None}
    if len(disc_totals) > 1:
        issues.append("inconsistent-disc-total")
    if any(track["current_path"] and Path(track["current_path"]).name.lower().endswith(".1.flac") for track in tracks):
        issues.append("collision-suffix")
    if any(track["path_status"] == "missing" for track in tracks):
        issues.append("missing-item-path")
    if artwork_status == "missing":
        issues.append("artwork-missing")
    if artpath_exists and root and artpath.parent != root and any((root / f"Disc {n}").is_dir() for n in range(1, 100)):
        issues.append("art-not-at-album-root")
    if exception and exception.get("expected_disctotal") and disc_totals != {exception["expected_disctotal"]}:
        issues.append("settled-exception-structure-mismatch")

    return {
        "album_id": as_int(field(album, "id")),
        "album": text(field(album, "album")),
        "albumartist": text(field(album, "albumartist")),
        "year": as_int(field(album, "year")),
        "label": text(field(album, "label")),
        "catalognum": text(field(album, "catalognum")),
        "mb_albumid": mb_albumid,
        "provenance": provenance,
        "settled_exception": exception,
        "established_normalizations": established_normalizations(album, tracks, exceptions),
        "album_root": str(root) if root else None,
        "database_artpath": str(raw_artpath) if raw_artpath else None,
        "database_artpath_exists": raw_artpath_exists,
        "database_artpath_status": database_artpath_status,
        "artpath": str(artpath) if artpath else None,
        "art_exists": artpath_exists,
        "artpath_status": artpath_status,
        "current_root_cover": str(root_cover) if root_cover else None,
        "current_root_cover_exists": root_cover_exists,
        "artwork_status": artwork_status,
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
        library_path = config["library"].as_filename()
        configured_directory = Path(config["directory"].as_filename())
        library = Library(library_path)
        raw_library = Library(library_path)
        raw_albums = {as_int(field(album, "id")): album for album in raw_library.albums()}
        albums = [album for album in library.albums() if matches(album, args.album, args.artist)]
        exceptions = load_exceptions()
    except Exception as exc:
        print(f"Could not open the configured beets library: {exc}", file=sys.stderr)
        return 2
    if args.limit:
        albums = albums[: args.limit]
    json.dump(
        [
            describe_album(
                album, raw_albums[as_int(field(album, "id"))], configured_directory, exceptions
            )
            for album in albums
        ],
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
