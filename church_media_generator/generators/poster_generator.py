"""Portrait mass poster (social) + 16×9 poster for projection / deck handouts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Mapping, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from services.community_config import get_community_name

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_OUTPUT_DIR = _PROJECT_ROOT / "outputs"

POSTER_W = 1080
POSTER_H = 1350
PPT_POSTER_W = 1920
PPT_POSTER_H = 1080

PosterTemplate = Literal["classic_white", "liturgical_color"]


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> float:
    if hasattr(draw, "textlength"):
        return float(draw.textlength(text, font=font))
    bbox = draw.textbbox((0, 0), text, font=font)
    return float(bbox[2] - bbox[0])


def _wrap_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        words = paragraph.split()
        current: list[str] = []
        for w in words:
            trial = " ".join(current + [w])
            if _text_width(draw, trial, font) <= max_width:
                current.append(w)
            else:
                if current:
                    lines.append(" ".join(current))
                current = [w]
        if current:
            lines.append(" ".join(current))
    return lines or [""]


def _try_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _tint_rgb(rgb: tuple[int, int, int], *, toward_white: float = 0.86) -> tuple[int, int, int]:
    r, g, b = rgb
    t = toward_white
    return (
        int(r * (1 - t) + 255 * t),
        int(g * (1 - t) + 255 * t),
        int(b * (1 - t) + 255 * t),
    )


def _darken_for_text(bg: tuple[int, int, int]) -> tuple[int, int, int]:
    """Aim for readable body on tinted background."""
    lum = (0.2126 * bg[0] + 0.7152 * bg[1] + 0.0722 * bg[2]) / 255.0
    if lum > 0.72:
        return (32, 30, 28)
    return (245, 242, 237)


def _muted_text(title_rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(int(c * 0.55 + 128 * 0.45) for c in title_rgb)  # type: ignore[return-value]


def _paste_logo(img: Image.Image, logo_path: Path, *, margin_x: int) -> None:
    logo = Image.open(logo_path).convert("RGBA")
    pw, ph = img.size
    max_w = min(220, int(pw * 0.22))
    w, h = logo.size
    if w > max_w:
        nh = max(1, int(h * (max_w / w)))
        logo = logo.resize((max_w, nh), Image.Resampling.LANCZOS)
    lw, lh = logo.size
    x = pw - margin_x - lw
    y = ph - margin_x - lh
    img.paste(logo, (x, y), logo)


def _layout_fonts(pw: int, ph: int) -> tuple[float, int, int, int, int]:
    """Scale factor and font sizes + margin for portrait vs landscape."""
    portrait = ph >= pw * 1.02
    if portrait:
        s = min(pw / 1080.0, ph / 1350.0)
        margin = max(48, int(72 * s))
        return s, max(26, int(42 * s)), max(20, int(30 * s)), max(17, int(24 * s)), margin
    s = min(pw / 1920.0, ph / 1080.0)
    margin = max(36, int(56 * s))
    return s, max(22, int(36 * s)), max(18, int(26 * s)), max(15, int(20 * s)), margin


def _compose_mass_poster_image(
    pw: int,
    ph: int,
    *,
    title: str,
    gospel_reference: str,
    celebrant: str,
    date: str,
    template: PosterTemplate,
    liturgical_color: Optional[Mapping[str, Any]],
    logo_path: Optional[Path],
    community_name: str,
    gospel_quote: str,
    entrance_title: str,
    communion_titles: str,
) -> Image.Image:
    if template == "classic_white":
        bg = (255, 255, 255)
        title_c = (28, 28, 28)
        date_c = (45, 45, 45)
        line_c = (40, 40, 40)
    else:
        if liturgical_color and "rgb" in liturgical_color:
            raw = liturgical_color["rgb"]
            rgb = (int(raw[0]), int(raw[1]), int(raw[2]))
        else:
            rgb = (200, 200, 205)
        bg = _tint_rgb(rgb, toward_white=0.9)
        title_c = _darken_for_text(bg)
        date_c = _muted_text(title_c)
        line_c = _muted_text(title_c)

    _s, fs_title, fs_date, fs_line, margin_x = _layout_fonts(pw, ph)
    max_text_w = pw - 2 * margin_x

    img = Image.new("RGB", (pw, ph), bg)
    draw = ImageDraw.Draw(img)

    font_title = _try_font(fs_title)
    font_date = _try_font(fs_date)
    font_line = _try_font(fs_line)

    gq = (gospel_quote or "").strip()
    if len(gq) > 320:
        gq = gq[:317].rstrip() + "…"

    comm = (community_name or "").strip() or get_community_name()
    ent = (entrance_title or "").strip()
    comm_line = (communion_titles or "").strip()

    title_lines = _wrap_lines(draw, title or "Mass", font_title, max_text_w)
    date_lines = _wrap_lines(draw, date or "—", font_date, max_text_w)
    comm_lines = _wrap_lines(draw, comm, font_line, max_text_w) if comm else []
    celeb_lines = _wrap_lines(draw, f"Celebrant: {celebrant or '—'}", font_line, max_text_w)
    gosp_lines = _wrap_lines(draw, f"Gospel: {gospel_reference or '—'}", font_line, max_text_w)
    quote_lines = _wrap_lines(draw, f"“{gq}”", font_line, max_text_w) if gq else []
    music_blocks: list[str] = []
    if ent:
        music_blocks.append(f"Entrance: {ent}")
    if comm_line:
        music_blocks.append(f"Communion: {comm_line}")
    music_lines: list[str] = []
    for blk in music_blocks:
        music_lines.extend(_wrap_lines(draw, blk, font_line, max_text_w))

    segments: list[tuple[list[str], ImageFont.ImageFont, tuple[int, int, int], int]] = [
        (title_lines, font_title, title_c, 14),
        (date_lines, font_date, date_c, 18),
        (comm_lines, font_line, line_c, 10),
        (celeb_lines, font_line, line_c, 12),
        (gosp_lines, font_line, line_c, 12),
    ]
    if quote_lines:
        segments.append((quote_lines, font_line, line_c, 10))
    if music_lines:
        segments.append((music_lines, font_line, line_c, 10))

    line_blocks: list[tuple[str, ImageFont.ImageFont, tuple[int, int, int], int]] = []
    for lines, font, color, gap in segments:
        for ln in lines:
            line_blocks.append((ln, font, color, gap))

    heights: list[int] = []
    for ln, font, _c, gap in line_blocks:
        bbox = draw.textbbox((0, 0), ln or " ", font=font)
        heights.append(bbox[3] - bbox[1] + gap)

    total_h = sum(heights)
    y = max(margin_x, (ph - total_h) // 2)

    for (ln, font, color, _gap), h in zip(line_blocks, heights):
        tw = _text_width(draw, ln, font)
        x = int((pw - tw) / 2.0)
        draw.text((x, int(y)), ln, fill=color, font=font)
        y += h

    if logo_path and logo_path.is_file():
        _paste_logo(img, logo_path, margin_x=margin_x)

    return img


def generate_mass_poster(
    title: str,
    gospel_reference: str,
    celebrant: str,
    date: str,
    *,
    template: PosterTemplate = "liturgical_color",
    liturgical_color: Optional[Mapping[str, Any]] = None,
    logo_path: Optional[Path] = None,
    community_name: Optional[str] = None,
    gospel_quote: str = "",
    entrance_song_title: str = "",
    communion_song_titles: str = "",
) -> Tuple[Path, Path]:
    """
    Writes ``outputs/mass_poster.png`` (1080×1350, social / feed) and
    ``outputs/mass_poster_16x9.png`` (1920×1080, presentation-friendly).

    Returns ``(social_path, ppt_aspect_path)``.
    """
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    social_path = _OUTPUT_DIR / "mass_poster.png"
    ppt_path = _OUTPUT_DIR / "mass_poster_16x9.png"

    comm = (community_name or "").strip() or get_community_name()

    img_social = _compose_mass_poster_image(
        POSTER_W,
        POSTER_H,
        title=title,
        gospel_reference=gospel_reference,
        celebrant=celebrant,
        date=date,
        template=template,
        liturgical_color=liturgical_color,
        logo_path=logo_path,
        community_name=comm,
        gospel_quote=gospel_quote,
        entrance_title=entrance_song_title,
        communion_titles=communion_song_titles,
    )
    img_social.save(social_path, format="PNG", optimize=True)

    img_ppt = _compose_mass_poster_image(
        PPT_POSTER_W,
        PPT_POSTER_H,
        title=title,
        gospel_reference=gospel_reference,
        celebrant=celebrant,
        date=date,
        template=template,
        liturgical_color=liturgical_color,
        logo_path=logo_path,
        community_name=comm,
        gospel_quote=gospel_quote,
        entrance_title=entrance_song_title,
        communion_titles=communion_song_titles,
    )
    img_ppt.save(ppt_path, format="PNG", optimize=True)

    return social_path, ppt_path


def _letterbox(image: Image.Image, size: tuple[int, int], bg: tuple[int, int, int]) -> Image.Image:
    tw, th = size
    iw, ih = image.size
    scale = min(tw / iw, th / ih)
    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    resized = image.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (tw, th), bg)
    ox = (tw - nw) // 2
    oy = (th - nh) // 2
    canvas.paste(resized, (ox, oy))
    return canvas


def export_social_variants(
    poster_path: Path,
    output_dir: Optional[Path] = None,
    *,
    prefix: str = "mass_poster",
) -> dict[str, Path]:
    """
    Instagram 1:1, Stories 9:16, Open Graph 1.91:1 — written next to ``poster_path``.
    """
    output_dir = output_dir or poster_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    src = Image.open(poster_path).convert("RGB")
    w, h = src.size
    out: dict[str, Path] = {}

    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    square_src = src.crop((left, top, left + side, top + side))
    p_sq = output_dir / f"{prefix}_instagram_square.png"
    square_src.resize((1080, 1080), Image.Resampling.LANCZOS).save(p_sq, format="PNG", optimize=True)
    out["instagram_square"] = p_sq

    letterbox_bg = (22, 22, 26)
    p_story = output_dir / f"{prefix}_instagram_story.png"
    _letterbox(src, (1080, 1920), letterbox_bg).save(p_story, format="PNG", optimize=True)
    out["instagram_story"] = p_story

    p_og = output_dir / f"{prefix}_open_graph.png"
    _letterbox(src, (1200, 630), letterbox_bg).save(p_og, format="PNG", optimize=True)
    out["open_graph"] = p_og

    return out
