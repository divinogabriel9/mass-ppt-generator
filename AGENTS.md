# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

Church Media Generator — a Python/FastAPI web app that generates PowerPoint slide decks and promotional posters for Sunday Mass celebrations. Single-service architecture, no external databases or message queues required.

### Running the dev server

```bash
cd church_media_generator
uvicorn server:app --reload --host 127.0.0.1 --port 8000
```

The UI is at `http://127.0.0.1:8000` and health check at `/health`.

### Linting

No project-specific linter is configured. Use `ruff` (installed alongside dev dependencies):

```bash
cd church_media_generator && python3 -m ruff check . --exclude .pdf_extract
```

### Tests

The only existing test is `church_media_generator/test_api.py` (a simple HTTP fetch to the external readings API). Run with:

```bash
cd church_media_generator && python3 test_api.py
```

### Key API endpoints

- `POST /api/preview` — fetch lectionary readings for a date (`{"date": "YYYY-MM-DD"}`)
- `POST /api/generate` — generate PPT + poster bundle (requires `date`, `celebrant`; optional: `sentence_index`, `poster_template`, `include_social_exports`, `include_gospel_art`, `songs`)
- `GET /api/community` — get community name and logo URL
- `POST /api/community` — update community name
- `POST /api/upload-logo` — upload church logo (multipart form)

### Gotchas

- The app requires `fonts-dejavu-core` system package for poster text rendering via Pillow. This font is pre-installed in the Cloud Agent VM.
- The external USCCB reading site (`bible.usccb.org`) may return HTTP 403 from certain networks. The app has automatic fallback to `bible-api.com` (World English Bible translation).
- Generated files go to `church_media_generator/outputs/` (gitignored).
- SQLite cache is stored at `church_media_generator/data/lectionary.sqlite` (auto-created, gitignored). Set `LECTIONARY_IGNORE_CACHE=1` to bypass cache reads.
