"""Shared mass media generation for CLI and web."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional

from generators.gospel_visual import render_gospel_moment
from generators.poster_generator import (
    PosterTemplate,
    export_social_variants,
    generate_mass_poster,
)
from generators.powerpoint import generate_mass_ppt
from services.community_config import get_logo_path, update_community
from services.gospel_quote_extractor import (
    first_sentence_slide_quote,
    pick_sentence_interactive,
    split_slide_sentences,
)
from services.hymn_library import recommend_sections
from services.liturgical_calendar import get_liturgical_color
from services.lectionary_service import get_liturgical_data


@dataclass
class PreviewPayload:
    ok: bool
    error: Optional[str] = None
    title: str = ""
    gospel_reference: str = ""
    season: str = ""
    lectionary_cycle: str = ""
    liturgical_color: Optional[Mapping[str, Any]] = None
    gospel_text_length: int = 0
    sentences: list[str] = field(default_factory=list)
    quote_attribution: Optional[str] = None
    songs_by_section: dict[str, list[dict[str, str]]] = field(default_factory=dict)


def resolve_slide_line(
    gospel_slide_quote: str,
    gospel_text: str,
    *,
    sentence_index: Optional[int] = None,
    interactive_pick: bool = False,
) -> str:
    """Pick the short line for slides (first sentence by default, or chosen index / CLI prompt)."""
    base_quote = (gospel_slide_quote or "").strip() or (gospel_text or "")
    sentences = split_slide_sentences(base_quote)
    if sentence_index is not None and sentences and 0 <= sentence_index < len(sentences):
        return sentences[sentence_index]
    if interactive_pick and len(sentences) > 1:
        return pick_sentence_interactive(sentences)
    return first_sentence_slide_quote(base_quote)


def fetch_preview(date: str) -> PreviewPayload:
    data = get_liturgical_data(date)
    if not data:
        return PreviewPayload(
            ok=False,
            error="Unable to fetch liturgical data. Use a valid date (YYYY-MM-DD).",
        )
    liturgical_color = get_liturgical_color(date)
    gospel_text = data.get("gospel_text") or ""
    gospel_slide_quote = (data.get("gospel_slide_quote") or "").strip()
    base_quote = gospel_slide_quote or gospel_text or ""
    sentences = split_slide_sentences(base_quote)
    season_key = str(liturgical_color.get("season") or "ordinary_time")
    by_sec = recommend_sections(season_key=season_key, per_section=5)
    return PreviewPayload(
        ok=True,
        title=data.get("title") or "Sunday Mass Celebration",
        gospel_reference=data.get("gospel_reference") or "N/A",
        season=data.get("season") or "",
        lectionary_cycle=data.get("lectionary_cycle") or "",
        liturgical_color=liturgical_color,
        gospel_text_length=len(gospel_text),
        sentences=sentences,
        quote_attribution=data.get("quote_attribution"),
        songs_by_section=by_sec,
    )


@dataclass
class GenerationResult:
    ok: bool
    error: Optional[str] = None
    pptx_path: Optional[Path] = None
    poster_path: Optional[Path] = None
    title: str = ""
    gospel_reference: str = ""
    slide_line_preview: str = ""
    gospel_text_length: int = 0
    liturgical_color_name: str = ""
    liturgical_color_hex: str = ""
    liturgical_season_label: str = ""


def _poster_template_arg(name: str) -> PosterTemplate:
    n = (name or "").strip().lower()
    if n == "classic_white" or n == "classic":
        return "classic_white"
    return "liturgical_color"


def generate_mass_media(
    date: str,
    celebrant: str,
    *,
    sentence_index: Optional[int] = None,
    interactive_pick: bool = False,
    poster_template: str = "liturgical_color",
    include_social_exports: bool = True,
    include_gospel_art: bool = True,
    community_name: Optional[str] = None,
    song_selections: Optional[Mapping[str, str]] = None,
) -> GenerationResult:
    if community_name and str(community_name).strip():
        update_community(community_name=str(community_name).strip())

    data = get_liturgical_data(date)
    if not data:
        return GenerationResult(
            ok=False,
            error="Unable to fetch liturgical data.",
        )

    title = data.get("title") or "Sunday Mass Celebration"
    gospel_ref = data.get("gospel_reference") or "N/A"
    gospel_text = data.get("gospel_text") or ""
    gospel_slide_quote = (data.get("gospel_slide_quote") or "").strip()
    season = data.get("season") or ""
    cycle = data.get("lectionary_cycle") or ""
    quote_attr = data.get("quote_attribution")

    liturgical_color = get_liturgical_color(date)
    color_name = str(liturgical_color.get("color_name") or "")
    color_hex = str(liturgical_color.get("hex") or "")
    season_lbl = str(liturgical_color.get("season") or "")

    slide_line = resolve_slide_line(
        gospel_slide_quote,
        gospel_text,
        sentence_index=sentence_index,
        interactive_pick=interactive_pick,
    )

    generate_mass_ppt(
        title=title,
        gospel_reference=gospel_ref,
        gospel_quote=slide_line or gospel_text,
        season=season,
        lectionary_cycle=cycle,
        celebrant=celebrant,
        date=date,
        quote_attribution=quote_attr,
        quote_max_chars=400,
        gospel_full_text=gospel_text,
        first_reading_ref=data.get("first_reading") or "",
        first_reading_text=data.get("first_reading_text") or "",
        psalm_ref=data.get("psalm") or "",
        psalm_text=data.get("psalm_text") or "",
        second_reading_ref=data.get("second_reading") or "",
        second_reading_text=data.get("second_reading_text") or "",
        liturgical_color=liturgical_color,
        song_selections=dict(song_selections) if song_selections else None,
    )

    tpl = _poster_template_arg(poster_template)
    logo = get_logo_path()
    poster_path = generate_mass_poster(
        title=title,
        gospel_reference=gospel_ref,
        celebrant=celebrant,
        date=date,
        template=tpl,
        liturgical_color=liturgical_color,
        logo_path=logo,
    )

    if include_social_exports:
        export_social_variants(poster_path)

    if include_gospel_art:
        ref_short = (gospel_ref or "").strip()[:90] if gospel_ref else ""
        render_gospel_moment(
            liturgical_color=liturgical_color,
            line1="Gospel",
            line2=ref_short,
        )

    _root = Path(__file__).resolve().parent
    pptx_path = _root / "outputs" / "mass_presentation.pptx"

    preview = slide_line[:180] + ("…" if len(slide_line) > 180 else "")

    return GenerationResult(
        ok=True,
        pptx_path=pptx_path,
        poster_path=poster_path,
        title=title,
        gospel_reference=gospel_ref,
        slide_line_preview=preview,
        gospel_text_length=len(gospel_text),
        liturgical_color_name=color_name,
        liturgical_color_hex=color_hex,
        liturgical_season_label=season_lbl,
    )
