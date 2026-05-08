"""Multi-slide Liturgy deck: 1920x1080 landscape (20\" x 11.25\" @ 96 dpi), chunked readings."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Inches, Pt

SLIDE_WIDTH = Inches(20)
SLIDE_HEIGHT = Inches(11.25)

MARGIN_SIDE = Inches(0.75)
MARGIN_TOP = Inches(0.5)

_BG = RGBColor(18, 18, 22)
_TITLE = RGBColor(220, 170, 90)
_BODY = RGBColor(245, 245, 245)
_MUTED = RGBColor(155, 155, 165)

_TITLE_PT = 38
_SECTION_PT = 32
_BODY_PT = 20
_META_PT = 15
_GREET_PT = 21

_MAX_CHARS_PER_SLIDE_BODY = 920

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_OUTPUT_DIR = _PROJECT_ROOT / "outputs"


def _layout_blank(prs: Presentation):
    for layout in prs.slide_layouts:
        nm = (layout.name or "").lower()
        if "blank" in nm:
            return layout
    return prs.slide_layouts[-1]


def _set_slide_bg(slide, rgb):
    fi = slide.background.fill
    fi.solid()
    fi.fore_color.rgb = rgb


def _prep_tf(tf):
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = Inches(0.12)
    tf.margin_right = Inches(0.12)
    tf.margin_top = Inches(0.1)
    tf.margin_bottom = Inches(0.1)


def _style_para(p, *, size_pt, color, bold=False, font_name="Calibri"):
    p.font.name = font_name
    p.font.size = Pt(size_pt)
    p.font.bold = bold
    p.font.color.rgb = color


def chunk_plain_text(text: str, limit: int = _MAX_CHARS_PER_SLIDE_BODY) -> List[str]:
    if not (text or "").strip():
        return []
    norm = " ".join(text.split())
    if len(norm) <= limit:
        return [norm]

    sentences = re.split(r"(?<=[.!?])\s+", norm)
    out: List[str] = []
    buf = ""

    def flush_buf():
        nonlocal buf
        if buf:
            out.append(buf.strip())
            buf = ""

    for s in sentences:
        w = s.strip()
        if not w:
            continue
        spacer = " " if buf else ""
        if len(buf) + len(spacer) + len(w) <= limit:
            buf += spacer + w
        else:
            flush_buf()
            if len(w) <= limit:
                buf = w
            else:
                step = limit
                for i in range(0, len(w), step):
                    piece = w[i : i + step].strip()
                    if piece:
                        out.append(piece)
                buf = ""
    flush_buf()
    return out if out else [norm[:limit]]


def _paragraphs(tf, *, size_pt, color, bold=False):
    tf.clear()
    p = tf.paragraphs[0]
    _style_para(p, size_pt=size_pt, color=color, bold=bold)
    return tf


def _fill_multipara(tf, text: str, *, size_pt=_BODY_PT, color=_BODY):
    tf.clear()
    raw = (text or "").strip()
    parts = [b.strip() for b in raw.split("\n\n") if b.strip()]
    if not parts:
        parts = [raw] if raw else [""]
    first = True
    for block in parts:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.text = block
        _style_para(p, size_pt=size_pt, color=color)
        p.space_after = Pt(4)


def _add_reading_block(
    prs: Presentation,
    *,
    section: str,
    reference: str,
    body: str,
    unavailable_note: str,
) -> None:
    ref = (reference or "").strip() or "—"
    body = (body or "").strip()

    def one_slide(head: str, sub: str, main: str):
        slide = prs.slides.add_slide(_layout_blank(prs))
        _set_slide_bg(slide, _BG)
        lx, top, w = MARGIN_SIDE, MARGIN_TOP, SLIDE_WIDTH - 2 * MARGIN_SIDE

        title_box = slide.shapes.add_textbox(lx, top, w, Inches(0.9))
        tf_t = title_box.text_frame
        _prep_tf(tf_t)
        _paragraphs(tf_t, size_pt=_SECTION_PT, color=_TITLE, bold=True)
        tf_t.paragraphs[0].text = head

        sub_box = slide.shapes.add_textbox(lx, top + Inches(0.92), w, Inches(0.52))
        _prep_tf(sub_box.text_frame)
        _paragraphs(sub_box.text_frame, size_pt=_META_PT, color=_MUTED)
        sub_box.text_frame.paragraphs[0].text = sub

        body_top = top + Inches(1.55)
        body_h = SLIDE_HEIGHT - body_top - MARGIN_SIDE
        bsh = slide.shapes.add_textbox(lx, body_top, w, body_h)
        _prep_tf(bsh.text_frame)
        _paragraphs(bsh.text_frame, size_pt=_BODY_PT, color=_BODY)
        _fill_multipara(bsh.text_frame, main, size_pt=_BODY_PT, color=_BODY)

    if not body:
        one_slide(section, ref, unavailable_note)
        return

    chunks = chunk_plain_text(body)
    total = len(chunks)
    for i, chunk in enumerate(chunks):
        head = section if i == 0 else f"{section} (continued)"
        sub = ref if total <= 1 else f"{ref}   ·   slide {i + 1} of {total}"
        one_slide(head, sub, chunk)


def generate_mass_ppt(
    title: str,
    gospel_reference: str,
    gospel_quote: str,
    season: str,
    lectionary_cycle: str,
    celebrant: str,
    date: str,
    *,
    gospel_full_text: str = "",
    first_reading_ref: str = "",
    first_reading_text: str = "",
    psalm_ref: str = "",
    psalm_text: str = "",
    second_reading_ref: str = "",
    second_reading_text: str = "",
    quote_attribution=None,
    quote_max_chars: int = 400,
):
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT

    unavail = (
        "Full text was not loaded from bible.usccb.org. "
        "Open today’s readings and paste text here if needed."
    )

    # Cover
    cov = prs.slides.add_slide(_layout_blank(prs))
    _set_slide_bg(cov, _BG)
    lx = MARGIN_SIDE
    lw = SLIDE_WIDTH - 2 * MARGIN_SIDE
    ty = MARGIN_TOP + Inches(0.65)

    tb = cov.shapes.add_textbox(lx, ty, lw, Inches(1.3))
    _prep_tb = tb.text_frame
    _prep_tf(_prep_tb)
    _paragraphs(_prep_tb, size_pt=_TITLE_PT, color=_TITLE, bold=True)
    _prep_tb.paragraphs[0].text = title or "Mass"

    g_line = (gospel_quote or "").strip()
    if quote_max_chars and len(g_line) > quote_max_chars:
        g_line = g_line[: quote_max_chars - 1].rstrip() + "\u2026"

    blk = cov.shapes.add_textbox(lx, ty + Inches(1.45), lw, Inches(1.85))
    _prep_tf(blk.text_frame)
    _paragraphs(blk.text_frame, size_pt=_GREET_PT, color=_BODY)
    gref = (gospel_reference or "").strip() or "—"
    lit = (
        f"Celebrant: {celebrant}\nDate: {date}\n\n"
        f"Season: {(season or '—').strip()}\n"
        f"Sunday Lectionary: Year {(lectionary_cycle or '—').strip().upper()}\n\n"
    )
    if g_line:
        lit += f"Gospel ({gref}) — excerpt\n\u201c{g_line}\u201d"
    else:
        lit += f"Gospel ({gref})\n(See Gospel slides for full passage.)"

    _fill_multipara(blk.text_frame, lit, size_pt=_GREET_PT, color=_BODY)

    if quote_attribution and g_line:
        note = cov.shapes.add_textbox(lx, SLIDE_HEIGHT - Inches(1.25), lw, Inches(0.85))
        _prep_tf(note.text_frame)
        _paragraphs(note.text_frame, size_pt=_META_PT, color=_MUTED)
        _fill_multipara(note.text_frame, str(quote_attribution).strip(), size_pt=_META_PT, color=_MUTED)

    gospel_body = ((gospel_full_text or "").strip() or (gospel_quote or "").strip())

    _add_reading_block(
        prs,
        section="First Reading",
        reference=first_reading_ref or "—",
        body=first_reading_text or "",
        unavailable_note=unavail,
    )
    _add_reading_block(
        prs,
        section="Responsorial Psalm",
        reference=psalm_ref or "—",
        body=psalm_text or "",
        unavailable_note=unavail,
    )
    if (second_reading_ref or "").strip():
        _add_reading_block(
            prs,
            section="Second Reading",
            reference=second_reading_ref.strip(),
            body=(second_reading_text or "").strip(),
            unavailable_note=unavail,
        )
    _add_reading_block(
        prs,
        section="Gospel",
        reference=gospel_reference or "—",
        body=gospel_body,
        unavailable_note=unavail,
    )

    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = _OUTPUT_DIR / "mass_presentation.pptx"
    prs.save(out_file)

    print(f"✅ PowerPoint created: {out_file}")
