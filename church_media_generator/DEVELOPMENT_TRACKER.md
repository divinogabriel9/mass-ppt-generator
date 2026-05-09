# Development tracker

_Last updated: 2026-05-09 — Phase 2 complete + Phase 3 kickstarted._

How to read this: **✅** = implemented in the current codebase in a useful form. **⬜** = not built yet (or only a stub / placeholder).

---

## PHASE 1 — FOUNDATION

| Item | Status |
|------|--------|
| Folder structure | ✅ |
| Python basics | ✅ |
| PowerPoint generation | ✅ (`generators/powerpoint.py`) |
| Liturgical detection | ✅ (season/calendar + Sunday cycle: `core/`, `services/liturgical_calendar.py`, `lectionary_service`) |
| Basic poster generation | ✅ (`generators/poster_generator.py` — 1080×1350 PNG) |

---

## PHASE 2 — CATHOLIC LOGIC

| Item | Status |
|------|--------|
| Lectionary database | ✅ **SQLite** — `data/lectionary.sqlite` via `services/lectionary_store.py` (cache on fetch; `LECTIONARY_IGNORE_CACHE=1` bypasses read) |
| Gospel lookup | ✅ (`lectionary_service`, `usccb_*`, gospel fallback) |
| Year A / B / C logic | ✅ (`core/liturgical_calendar.py` → `sunday_lectionary_cycle`) |
| Season colors | ✅ (`services/liturgical_calendar.py` → deck/poster theme) |
| Song recommendation engine | ✅ **Rule-based** — `data/hymn_suggestions.json` + `services/song_recommendations.py`, surfaced in `/api/preview` and UI |

---

## PHASE 3 — VISUAL ENGINE

| Item | Status |
|------|--------|
| AI Gospel images | ✅ **Kickstart** — non-AI art in liturgical colors (`generators/gospel_moment.png`); swap module later for true AI |
| Poster templates | ✅ **`classic_white`** & **`liturgical_color`** (+ logo placement) |
| Social media auto-resize | ✅ **IG square 1080, Stories 1080×1920, OG 1200×630** (`export_social_variants`) |
| Church logo system | ✅ **`data/community.json`** — `community_name`, `logo_path` — footer text in PPT; logo on poster when path set |

---

## PHASE 4 — FULL MASS SYSTEM

| Item | Status |
|------|--------|
| Full Mass slide flow | ✅ (GFCC-style flow: `gfcc_flow_content.py` + generator) |
| Lyrics slides | ⬜ (hymn *placeholders* exist; not a lyrics library or full song slides) |
| Prayer database | ⬜ (fixed text blocks / Missal placeholders; not a queryable DB) |
| Multilingual toggle | ⬜ |

---

## PHASE 5 — REAL PRODUCT

| Item | Status |
|------|--------|
| User accounts | ⬜ |
| Church profiles | ⬜ |
| Cloud storage | ⬜ |
| Subscription system | ⬜ |
| Deployment | ✅ **Partial** — `Dockerfile`, FastAPI web UI (`server.py`), `/health`; ⬜ hosted PaaS / CI as you prefer later |

---

## Extra already in repo

- **CLI** — `main.py`.
- **Web app** — UI + `/api/preview`, `/api/generate`, ZIP includes PPT, poster, social PNGs, `gospel_moment.png` when present.
- **Gospel excerpt logic** — `gospel_quote_extractor`.
- **Generate options (JSON)** — `poster_template`, `include_social_exports`, `include_gospel_art`.

---

When you finish an item, change **⬜** → **✅** and adjust notes if needed.
