"""Portrait mass poster (1080x1350) for social / print preview."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_OUTPUT_DIR = _PROJECT_ROOT / "outputs"

POSTER_W = 1080
POSTER_H = 1350
MARGIN_X = 72
MAX_TEXT_W = POSTER_W - 2 * MARGIN_X


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


def generate_mass_poster(
    title: str,
    gospel_reference: str,
    celebrant: str,
    date: str,
) -> Path:
    """
    Create a 1080x1350 white poster with centered title, date, celebrant, and Gospel reference.

    Saves to outputs/mass_poster.png under the project root.
    """
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _OUTPUT_DIR / "mass_poster.png"

    img = Image.new("RGB", (POSTER_W, POSTER_H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    font_title = _try_font(42)
    font_date = _try_font(30)
    font_line = _try_font(24)

    title_lines = _wrap_lines(draw, title or "Mass", font_title, MAX_TEXT_W)
    date_lines = _wrap_lines(draw, date or "—", font_date, MAX_TEXT_W)
    celeb_lines = _wrap_lines(draw, f"Celebrant: {celebrant or '—'}", font_line, MAX_TEXT_W)
    gosp_lines = _wrap_lines(draw, f"Gospel: {gospel_reference or '—'}", font_line, MAX_TEXT_W)

    segments: list[tuple[list[str], ImageFont.ImageFont, tuple[int, int, int], int]] = [
        (title_lines, font_title, (28, 28, 28), 14),
        (date_lines, font_date, (45, 45, 45), 18),
        (celeb_lines, font_line, (40, 40, 40), 12),
        (gosp_lines, font_line, (40, 40, 40), 12),
    ]

    line_blocks: list[tuple[str, ImageFont.ImageFont, tuple[int, int, int], int]] = []
    for lines, font, color, gap in segments:
        for ln in lines:
            line_blocks.append((ln, font, color, gap))

    heights: list[int] = []
    for ln, font, _c, gap in line_blocks:
        bbox = draw.textbbox((0, 0), ln or " ", font=font)
        heights.append(bbox[3] - bbox[1] + gap)

    total_h = sum(heights)
    y = max(MARGIN_X, (POSTER_H - total_h) // 2)

    for (ln, font, color, _gap), h in zip(line_blocks, heights):
        tw = _text_width(draw, ln, font)
        x = int((POSTER_W - tw) / 2.0)
        draw.text((x, int(y)), ln, fill=color, font=font)
        y += h

    img.save(out_path, format="PNG", optimize=True)
    return out_path
