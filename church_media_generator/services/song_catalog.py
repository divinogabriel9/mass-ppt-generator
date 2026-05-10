"""Song catalog helpers for section-based hymn library storage."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_LIBRARY_PATH = _PROJECT_ROOT / "data" / "hymn_library.json"
_SECTIONS = ("entrance", "offertory", "communion", "recessional", "meditation")
_PART_MAP = {
    "entrance": "entrance",
    "offertory": "offertory",
    "communion": "communion",
    "recessional": "recessional",
    "meditation": "meditation",
}


def _blank_library() -> dict[str, list[dict[str, Any]]]:
    return {k: [] for k in _SECTIONS}


def load_catalog() -> dict[str, list[dict[str, Any]]]:
    if not _LIBRARY_PATH.is_file():
        return _blank_library()
    try:
        raw = json.loads(_LIBRARY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _blank_library()
    out = _blank_library()
    for sec in _SECTIONS:
        rows = raw.get(sec) or []
        out[sec] = [x for x in rows if isinstance(x, dict)]
    return out


def save_catalog(data: dict[str, list[dict[str, Any]]]) -> None:
    _LIBRARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    _LIBRARY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def make_song_id(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", (title or "").strip().lower()).strip("_")
    if not slug:
        slug = "song"
    return slug[:72]


def import_titles(grouped_titles: dict[str, list[str]]) -> dict[str, Any]:
    """Upsert section-grouped song titles into the local hymn catalog."""
    data = load_catalog()
    added = 0
    existing = 0
    per_section: dict[str, int] = {}
    for sec, titles in grouped_titles.items():
        section = str(sec).strip().lower()
        if section not in _SECTIONS:
            continue
        rows = data[section]
        by_title = {str(r.get("title") or "").strip().lower(): r for r in rows}
        by_id = {str(r.get("id") or "").strip(): r for r in rows}
        local_added = 0
        for t in titles or []:
            title = str(t).strip()
            if not title:
                continue
            ttl = title.lower()
            if ttl in by_title:
                existing += 1
                continue
            hid_base = make_song_id(title)
            hid = hid_base
            n = 2
            while hid in by_id:
                hid = f"{hid_base}_{n}"
                n += 1
            row = {
                "id": hid,
                "title": title,
                "language": "English",
                "seasons": ["all"],
                "lyrics": "",
            }
            rows.append(row)
            by_title[ttl] = row
            by_id[hid] = row
            added += 1
            local_added += 1
        per_section[section] = local_added
    save_catalog(data)
    return {"added": added, "existing": existing, "per_section": per_section}


def import_song_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Import rows in the shape:
      {"title": str, "language": str, "mass_part": [str, ...]}
    Ignore duplicates by title (global, case-insensitive).
    """
    data = load_catalog()
    all_titles = set()
    for sec in _SECTIONS:
        for item in data.get(sec, []):
            all_titles.add(str(item.get("title") or "").strip().lower())

    added = 0
    existing = 0
    per_section: dict[str, int] = {k: 0 for k in _SECTIONS}

    # id index for uniqueness
    by_id = set()
    for sec in _SECTIONS:
        for item in data.get(sec, []):
            by_id.add(str(item.get("id") or "").strip())

    for raw in rows or []:
        if not isinstance(raw, dict):
            continue
        title = str(raw.get("title") or "").strip()
        if not title:
            continue
        ttl = title.lower()
        if ttl in all_titles:
            existing += 1
            continue
        language = str(raw.get("language") or "English").strip() or "English"
        parts = raw.get("mass_part") or []
        if not isinstance(parts, list):
            parts = [parts]
        sections: list[str] = []
        for p in parts:
            key = str(p or "").strip().lower()
            sec = _PART_MAP.get(key)
            if sec and sec not in sections:
                sections.append(sec)
        if not sections:
            continue

        hid_base = make_song_id(title)
        hid = hid_base
        n = 2
        while hid in by_id:
            hid = f"{hid_base}_{n}"
            n += 1
        by_id.add(hid)

        row = {
            "id": hid,
            "title": title,
            "language": language,
            "seasons": ["all"],
            "lyrics": "",
        }
        for sec in sections:
            data[sec].append(dict(row))
            per_section[sec] += 1
        all_titles.add(ttl)
        added += 1

    save_catalog(data)
    return {"added": added, "existing": existing, "per_section": per_section}


def update_lyrics(section: str, hymn_id: str, lyrics: str, source_link: str = "") -> bool:
    """Store fetched lyrics for a section/id pair."""
    sec = (section or "").strip().lower()
    hid = (hymn_id or "").strip()
    lyr = (lyrics or "").strip()
    if sec not in _SECTIONS or not hid or not lyr:
        return False
    data = load_catalog()
    changed = False
    for item in data.get(sec) or []:
        if str(item.get("id") or "").strip() != hid:
            continue
        item["lyrics"] = lyr
        if source_link:
            item["text_link"] = source_link
        changed = True
        break
    if changed:
        save_catalog(data)
    return changed

