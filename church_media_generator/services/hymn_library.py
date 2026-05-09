"""Load hymn library with full lyrics and per-Mass-section recommendations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_LIBRARY_PATH = _PROJECT_ROOT / "data" / "hymn_library.json"


def load_library() -> dict[str, Any]:
    if not _LIBRARY_PATH.is_file():
        return {"entrance": [], "offertory": [], "communion": [], "recessional": []}
    try:
        return json.loads(_LIBRARY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"entrance": [], "offertory": [], "communion": [], "recessional": []}


def _priority(item: dict[str, Any], season_key: str) -> int:
    raw = item.get("seasons") or ["all"]
    if not isinstance(raw, list):
        raw = [raw]
    tags = {str(x).strip().lower() for x in raw}
    sk = (season_key or "").strip().lower().replace(" ", "_")
    if sk in tags:
        return 3
    if "all" in tags:
        return 2
    return 1


def recommend_sections(
    *,
    season_key: str,
    per_section: int = 5,
) -> dict[str, list[dict[str, str]]]:
    """
    Return 3–5 hymns per section (capped at ``per_section``, max 5) with id + title for UI.
    Higher priority: season match, then ``all``, then remaining.
    """
    lib = load_library()
    out: dict[str, list[dict[str, str]]] = {}
    cap = max(3, min(per_section, 5))

    for section in ("entrance", "offertory", "communion", "recessional"):
        items: list[dict[str, Any]] = [x for x in (lib.get(section) or []) if isinstance(x, dict)]
        scored: list[tuple[int, int, dict[str, str]]] = []
        for idx, item in enumerate(items):
            hid = str(item.get("id") or "").strip()
            title = str(item.get("title") or "").strip()
            if not hid or not title:
                continue
            pr = _priority(item, season_key)
            scored.append((pr, -idx, {"id": hid, "title": title}))
        scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
        seen: set[str] = set()
        picked: list[dict[str, str]] = []
        for _pr, _ix, row in scored:
            if row["id"] in seen:
                continue
            seen.add(row["id"])
            picked.append(row)
            if len(picked) >= cap:
                break
        out[section] = picked
    return out


def get_hymn(section: str, hymn_id: str) -> Optional[dict[str, Any]]:
    hid = (hymn_id or "").strip()
    sec = (section or "").strip().lower()
    if not hid or sec not in ("entrance", "offertory", "communion", "recessional"):
        return None
    for item in load_library().get(sec) or []:
        if isinstance(item, dict) and str(item.get("id") or "").strip() == hid:
            return item
    return None
