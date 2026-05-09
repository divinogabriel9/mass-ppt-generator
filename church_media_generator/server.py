"""
Church Media Generator — minimal web UI + JSON API.

Run from project root:
  cd church_media_generator && uvicorn server:app --reload --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from pipeline import PreviewPayload, fetch_preview, generate_mass_media
from services.community_config import (
    LOGO_RELATIVE,
    get_community_name,
    logo_file_absolute,
    update_community,
    uploads_dir,
)

# Optional outputs produced alongside mass_poster.png (Phase 3)
_BUNDLE_OPTIONAL = (
    "gospel_moment.png",
    "mass_poster_instagram_square.png",
    "mass_poster_instagram_story.png",
    "mass_poster_open_graph.png",
)

_PROJECT = Path(__file__).resolve().parent
_OUTPUT_DIR = _PROJECT / "outputs"
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

_UPLOAD_DIR = uploads_dir()
_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

_ALLOWED_LOGO_TYPES = frozenset(
    ("image/png", "image/jpeg", "image/webp", "image/gif", "image/x-png", "image/jpg")
)
_MAX_LOGO_BYTES = 2_500_000

_BUNDLE_NAME = "mass_bundle.zip"


def _write_mass_bundle_zip() -> None:
    """Pack latest PPT, poster, social sizes, and gospel art into one zip."""
    out = _OUTPUT_DIR / _BUNDLE_NAME
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, arc in (
            (_OUTPUT_DIR / "mass_presentation.pptx", "mass_presentation.pptx"),
            (_OUTPUT_DIR / "mass_poster.png", "mass_poster.png"),
        ):
            if path.is_file():
                zf.write(path, arcname=arc)
        for name in _BUNDLE_OPTIONAL:
            p = _OUTPUT_DIR / name
            if p.is_file():
                zf.write(p, arcname=name)


app = FastAPI(title="Church Media Generator")
templates = Jinja2Templates(directory=str(_PROJECT / "templates"))
app.mount("/media", StaticFiles(directory=str(_OUTPUT_DIR)), name="media")
app.mount("/uploads", StaticFiles(directory=str(_UPLOAD_DIR)), name="uploads")


def _preview_to_json(p: PreviewPayload) -> dict[str, Any]:
    lc = p.liturgical_color
    liturgical: Optional[dict[str, Any]] = None
    if lc:
        liturgical = {
            "color_name": lc.get("color_name"),
            "hex": lc.get("hex"),
            "season": lc.get("season"),
            "rgb": list(lc.get("rgb", ())),
        }
    return {
        "ok": p.ok,
        "error": p.error,
        "title": p.title,
        "gospel_reference": p.gospel_reference,
        "season": p.season,
        "lectionary_cycle": p.lectionary_cycle,
        "liturgical_color": liturgical,
        "gospel_text_length": p.gospel_text_length,
        "sentences": p.sentences,
        "sentence_count": len(p.sentences),
        "quote_attribution": p.quote_attribution,
        "songs_by_section": p.songs_by_section,
    }


class SongSelection(BaseModel):
    entrance: Optional[str] = None
    offertory: Optional[str] = None
    communion_1: Optional[str] = None
    communion_2: Optional[str] = None
    recessional: Optional[str] = None


class CommunityNameBody(BaseModel):
    community_name: str = Field(..., min_length=1, max_length=240)


class PreviewBody(BaseModel):
    date: str = Field(..., min_length=8, description="YYYY-MM-DD")


class GenerateBody(BaseModel):
    date: str = Field(..., min_length=8)
    celebrant: str = Field(..., min_length=1, max_length=200)
    sentence_index: Optional[int] = Field(None, ge=0)
    poster_template: str = Field(
        "liturgical_color",
        description="liturgical_color | classic_white",
    )
    include_social_exports: bool = Field(True)
    include_gospel_art: bool = Field(True)
    community_name: Optional[str] = Field(None, max_length=240)
    songs: Optional[SongSelection] = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/community")
def api_community() -> dict[str, Any]:
    logo_exists = logo_file_absolute().is_file()
    return {
        "community_name": get_community_name(),
        "logo_url": "/uploads/community_logo.png" if logo_exists else None,
    }


@app.post("/api/community")
def api_set_community_name(body: CommunityNameBody) -> dict[str, Any]:
    update_community(community_name=body.community_name.strip())
    return {"ok": True, "community_name": get_community_name()}


@app.post("/api/upload-logo")
async def api_upload_logo(file: UploadFile = File(...)) -> dict[str, Any]:
    ctype = (file.content_type or "").split(";")[0].strip().lower()
    if ctype not in _ALLOWED_LOGO_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Use a PNG, JPEG, WebP, or GIF image.",
        )
    raw = await file.read()
    if len(raw) > _MAX_LOGO_BYTES:
        raise HTTPException(status_code=400, detail="Image must be at most about 2.5 MB.")

    try:
        from PIL import Image
    except ImportError as exc:
        raise HTTPException(status_code=500, detail="Pillow is required for image upload.") from exc

    try:
        im = Image.open(io.BytesIO(raw))
        im.load()
    except OSError as exc:
        raise HTTPException(status_code=400, detail="Could not read image file.") from exc

    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in getattr(im, "info", {})):
        im = im.convert("RGBA")
    else:
        im = im.convert("RGB")

    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    out_path = logo_file_absolute()
    im.save(out_path, format="PNG", optimize=True)

    update_community(logo_path=LOGO_RELATIVE)
    return {
        "ok": True,
        "logo_url": "/uploads/community_logo.png",
        "message": "Logo saved. It will appear on the next generated poster.",
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> Any:
    # Starlette 0.28+: (request, name, context); request is injected into the template context.
    return templates.TemplateResponse(
        request,
        "index.html",
        {"title": "Church Media Generator"},
    )


@app.post("/api/preview")
def api_preview(body: PreviewBody) -> Any:
    p = fetch_preview(body.date.strip())
    return _preview_to_json(p)


@app.post("/api/generate")
def api_generate(body: GenerateBody) -> Any:
    song_map = body.songs.model_dump(exclude_none=True) if body.songs else None
    result = generate_mass_media(
        body.date.strip(),
        body.celebrant.strip(),
        sentence_index=body.sentence_index,
        poster_template=body.poster_template,
        include_social_exports=body.include_social_exports,
        include_gospel_art=body.include_gospel_art,
        community_name=body.community_name.strip() if body.community_name else None,
        song_selections=song_map,
    )
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error or "Generation failed.")
    _write_mass_bundle_zip()
    zip_ready = (_OUTPUT_DIR / _BUNDLE_NAME).is_file()
    return {
        "ok": True,
        "title": result.title,
        "gospel_reference": result.gospel_reference,
        "slide_excerpt": result.slide_line_preview,
        "pptx_url": "/media/mass_presentation.pptx",
        "poster_url": "/media/mass_poster.png",
        **(
            {"zip_url": f"/media/{_BUNDLE_NAME}"}
            if zip_ready
            else {}
        ),
    }
