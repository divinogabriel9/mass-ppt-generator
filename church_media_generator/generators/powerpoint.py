"""GFCC-style full Mass flow + readings: 1920x1080 landscape, multi-slide."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Inches, Pt

from pptx.enum.text import PP_ALIGN

from . import gfcc_flow_content as GFCC

SLIDE_WIDTH = Inches(20)
SLIDE_HEIGHT = Inches(11.25)

MARGIN_SIDE = Inches(0.75)
MARGIN_TOP = Inches(0.5)

_BG = RGBColor(18, 18, 22)
_TITLE = RGBColor(220, 170, 90)
_BODY = RGBColor(245, 245, 245)
_MUTED = RGBColor(155, 155, 165)

_TITLE_PT = 38
_SECTION_PT = 30
_BODY_PT = 19
_META_PT = 14
_GREET_PT = 21
_FOOTER_PT = 13

_MAX_CHARS_PER_SLIDE_BODY = 900
_MAX_MARKED_BODY = 2800

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_OUTPUT_DIR = _PROJECT_ROOT / "outputs"

_COMMUNITY = "GWANGJU FILIPINO CATHOLIC COMMUNITY"


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
    tf.margin_top = Inches(0.08)
    tf.margin_bottom = Inches(0.08)


def _style_para(p, *, size_pt, color, bold=False, italic=False, font_name="Calibri"):
    p.font.name = font_name
    p.font.size = Pt(size_pt)
    p.font.bold = bold
    p.font.italic = italic
    p.font.color.rgb = color


def _add_community_footer(slide, footer_section: str):
    lx = MARGIN_SIDE
    w = SLIDE_WIDTH - 2 * MARGIN_SIDE
    y = SLIDE_HEIGHT - Inches(0.95)
    foot = slide.shapes.add_textbox(lx, y, w, Inches(0.85))
    tf = foot.text_frame
    _prep_tf(tf)
    tf.clear()
    p0 = tf.paragraphs[0]
    p0.text = _COMMUNITY
    _style_para(p0, size_pt=_FOOTER_PT, color=_MUTED, bold=True)
    p1 = tf.add_paragraph()
    p1.text = footer_section
    _style_para(p1, size_pt=_FOOTER_PT - 1, color=_TITLE, bold=False)
    p1.space_before = Pt(2)


def _parse_marked_lines(marked: str) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for raw in (marked or "").split("\n"):
        raw = raw.strip()
        if not raw:
            continue
        role = "plain"
        if raw.startswith("<<P>>"):
            role, raw = "priest", raw[5:].strip()
        elif raw.startswith("<<A>>"):
            role, raw = "all", raw[5:].strip()
        elif raw.startswith("<<D>>"):
            role, raw = "direction", raw[5:].strip()
        elif raw.startswith("<<H>>"):
            role, raw = "hymn", raw[5:].strip()
        out.append((role, raw))
    return out


def _add_marked_slide(prs: Presentation, footer_section: str, marked_text: str) -> None:
    slide = prs.slides.add_slide(_layout_blank(prs))
    _set_slide_bg(slide, _BG)
    lx, top, w = MARGIN_SIDE, MARGIN_TOP, SLIDE_WIDTH - 2 * MARGIN_SIDE
    body_h = SLIDE_HEIGHT - top - Inches(1.15)

    box = slide.shapes.add_textbox(lx, top, w, body_h)
    tf = box.text_frame
    _prep_tf(tf)
    tf.clear()
    first = True
    for role, line in _parse_marked_lines(marked_text):
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.text = line
        if role == "priest":
            _style_para(p, size_pt=_BODY_PT + 1, color=_TITLE, bold=True)
        elif role == "all":
            _style_para(p, size_pt=_BODY_PT + 1, color=_BODY, bold=True)
        elif role == "direction":
            _style_para(p, size_pt=_META_PT + 1, color=_TITLE, bold=False, italic=True)
        elif role == "hymn":
            _style_para(p, size_pt=_BODY_PT, color=_BODY, bold=True)
        else:
            _style_para(p, size_pt=_BODY_PT, color=_BODY, bold=False)
        p.space_after = Pt(5)

    _add_community_footer(slide, footer_section)


def _chunk_marked_body(marked: str, limit: int = _MAX_MARKED_BODY) -> List[str]:
    if len(marked) <= limit:
        return [marked]
    parts = []
    buf = []
    n = 0
    for line in marked.split("\n"):
        line_len = len(line) + 1
        if n + line_len > limit and buf:
            parts.append("\n".join(buf))
            buf = [line]
            n = line_len
        else:
            buf.append(line)
            n += line_len
    if buf:
        parts.append("\n".join(buf))
    return parts if parts else [marked[:limit]]


def _add_marked_slide_chunked(prs: Presentation, footer_section: str, marked_text: str) -> None:
    chunks = _chunk_marked_body(marked_text)
    total = len(chunks)
    for i, ch in enumerate(chunks):
        foot = footer_section if total == 1 else f"{footer_section} ({i + 1}/{total})"
        _add_marked_slide(prs, foot, ch)


def _add_divider_cover(
    prs: Presentation,
    *,
    title: str,
    celebrant: str,
    date: str,
    season: str,
    lectionary_cycle: str,
    gospel_reference: str,
    gospel_quote: str,
    quote_max_chars: int,
) -> None:
    slide = prs.slides.add_slide(_layout_blank(prs))
    _set_slide_bg(slide, _BG)
    lx = MARGIN_SIDE
    lw = SLIDE_WIDTH - 2 * MARGIN_SIDE
    ty = MARGIN_TOP + Inches(0.55)

    tb = slide.shapes.add_textbox(lx, ty, lw, Inches(1.15))
    _prep_tf(tb.text_frame)
    tb.text_frame.clear()
    p = tb.text_frame.paragraphs[0]
    p.text = title or "Mass"
    _style_para(p, size_pt=_TITLE_PT, color=_TITLE, bold=True)

    g_line = (gospel_quote or "").strip()
    if quote_max_chars and len(g_line) > quote_max_chars:
        g_line = g_line[: quote_max_chars - 1].rstrip() + "\u2026"
    gref = (gospel_reference or "").strip() or "—"

    blk = slide.shapes.add_textbox(lx, ty + Inches(1.25), lw, Inches(2.2))
    _prep_tf(blk.text_frame)
    blk.text_frame.clear()
    lines = [
        f"MASS CELEBRANT: {celebrant}",
        "",
        _COMMUNITY.replace(" ", "\n"),
        "",
        f"Gospel ({gref})",
    ]
    if g_line:
        lines.append(f"\u201c{g_line}\u201d")
    lines.append("")
    lines.append(f"YEAR {(lectionary_cycle or '—').strip().upper()}")
    lines.append(f"{date} · {(season or '').strip()}")

    first = True
    for line in lines:
        p = blk.text_frame.paragraphs[0] if first else blk.text_frame.add_paragraph()
        first = False
        p.text = line
        _style_para(p, size_pt=_GREET_PT, color=_BODY, bold=bool(line and "CELEBRANT" in line))
        p.space_after = Pt(2)

    _add_community_footer(slide, "Mass poster / divider")


def _add_section_card(prs: Presentation, big_lines: str, footer_section: str) -> None:
    slide = prs.slides.add_slide(_layout_blank(prs))
    _set_slide_bg(slide, _BG)
    lx, top, w = MARGIN_SIDE, MARGIN_TOP + Inches(1.2), SLIDE_WIDTH - 2 * MARGIN_SIDE
    box = slide.shapes.add_textbox(lx, top, w, Inches(4))
    tf = box.text_frame
    _prep_tf(tf)
    tf.clear()
    p = tf.paragraphs[0]
    p.text = big_lines
    _style_para(p, size_pt=44, color=_TITLE, bold=True)
    p.alignment = PP_ALIGN.CENTER

    _add_community_footer(slide, footer_section)


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
                for i in range(0, len(w), limit):
                    piece = w[i : i + limit].strip()
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
    lotw_banner: bool = False,
    footer_tag: str | None = None,
) -> None:
    ref = (reference or "").strip() or "—"
    body = (body or "").strip()
    foot = footer_tag or section

    def one_slide(head: str, sub: str, main: str):
        slide = prs.slides.add_slide(_layout_blank(prs))
        _set_slide_bg(slide, _BG)
        lx, top, w = MARGIN_SIDE, MARGIN_TOP, SLIDE_WIDTH - 2 * MARGIN_SIDE

        title_h = Inches(1.15) if lotw_banner else Inches(0.95)
        title_box = slide.shapes.add_textbox(lx, top, w, title_h)
        tf_t = title_box.text_frame
        _prep_tf(tf_t)
        tf_t.clear()
        if lotw_banner:
            p0 = tf_t.paragraphs[0]
            p0.text = "Liturgy of the Word"
            _style_para(p0, size_pt=_SECTION_PT - 2, color=_TITLE, bold=True)
            p1 = tf_t.add_paragraph()
            p1.text = head if "continued" in head.lower() else f"{section} ({ref})"
            _style_para(p1, size_pt=_META_PT + 2, color=_MUTED, bold=False)
        else:
            _paragraphs(tf_t, size_pt=_SECTION_PT, color=_TITLE, bold=True)
            tf_t.paragraphs[0].text = head

        sub_top = top + title_h + Inches(0.06)
        sub_h = Inches(0.48)
        sub_box = slide.shapes.add_textbox(lx, sub_top, w, sub_h)
        _prep_tf(sub_box.text_frame)
        _paragraphs(sub_box.text_frame, size_pt=_META_PT, color=_MUTED)
        sub_box.text_frame.paragraphs[0].text = sub

        body_top = sub_top + sub_h + Inches(0.12)
        body_h = SLIDE_HEIGHT - body_top - Inches(1.0)
        bsh = slide.shapes.add_textbox(lx, body_top, w, body_h)
        _prep_tf(bsh.text_frame)
        _paragraphs(bsh.text_frame, size_pt=_BODY_PT, color=_BODY)
        _fill_multipara(bsh.text_frame, main, size_pt=_BODY_PT, color=_BODY)
        _add_community_footer(slide, foot)

    if not body:
        one_slide(section, ref if lotw_banner else ref, unavailable_note)
        return

    chunks = chunk_plain_text(body)
    total = len(chunks)
    for i, chunk in enumerate(chunks):
        head = section if i == 0 else f"{section} (continued)"
        if lotw_banner:
            sub = "" if total <= 1 else f"Slide {i + 1} of {total}"
        else:
            sub = ref if total <= 1 else f"{ref}  ·  slide {i + 1} of {total}"
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

    ctx = dict(
        title=title,
        celebrant=celebrant,
        date=date,
        season=season,
        lectionary_cycle=lectionary_cycle,
        gospel_reference=gospel_reference,
        gospel_quote=gospel_quote,
        quote_max_chars=quote_max_chars,
    )

    # ----- Pre-Mass -----
    _add_marked_slide(prs, "Pre-Mass", GFCC.SILENT_REMINDER)
    _add_divider_cover(prs, **ctx)
    _add_marked_slide_chunked(prs, "Entrance", GFCC.ENTRANCE_HYMN_1 + "\n" + GFCC.ENTRANCE_HYMN_2)
    _add_divider_cover(prs, **ctx)

    # ----- Introductory rites -----
    _add_marked_slide(prs, "Introductory Rites", GFCC.SIGN_CROSS)
    _add_marked_slide(prs, "Penitential Act", GFCC.GREETING_EXTENDED)
    _add_marked_slide(prs, "Penitential Act", GFCC.CONFITEOR_OPEN)
    _add_marked_slide(prs, "Penitential Act", GFCC.ABSOLUTION_PENITENTIAL)
    _add_marked_slide(prs, "Kyrie Eleison", GFCC.KYRIE)
    _add_marked_slide_chunked(prs, "Gloria", GFCC.GLORIA_1 + "\n" + GFCC.GLORIA_2 + "\n" + GFCC.GLORIA_3)
    _add_marked_slide(prs, "Liturgy of the Word", GFCC.OPENING_PRAYER)

    # ----- Liturgy of the Word (readings) -----
    _add_section_card(prs, "LITURGY OF\nTHE WORD", "Liturgy of the Word")

    _add_reading_block(
        prs,
        section="First Reading",
        reference=first_reading_ref or "—",
        body=first_reading_text or "",
        unavailable_note=unavail,
        lotw_banner=True,
        footer_tag="Liturgy of the Word",
    )
    _add_reading_block(
        prs,
        section="Responsorial Psalm",
        reference=psalm_ref or "—",
        body=psalm_text or "",
        unavailable_note=unavail,
        lotw_banner=True,
        footer_tag="Liturgy of the Word",
    )
    if (second_reading_ref or "").strip():
        _add_reading_block(
            prs,
            section="Second Reading",
            reference=second_reading_ref.strip(),
            body=(second_reading_text or "").strip(),
            unavailable_note=unavail,
            lotw_banner=True,
            footer_tag="Liturgy of the Word",
        )

    _add_marked_slide(prs, "Gospel Acclamation", GFCC.ALLELUIA_SING)
    _add_marked_slide(prs, "Gospel Acclamation", GFCC.ALLELUIA_COMMENTATOR)
    _add_marked_slide(prs, "Gospel Acclamation", GFCC.GOSPEL_INTRO)

    gospel_body = ((gospel_full_text or "").strip() or (gospel_quote or "").strip())
    _add_reading_block(
        prs,
        section="Gospel",
        reference=gospel_reference or "—",
        body=gospel_body,
        unavailable_note=unavail,
        lotw_banner=False,
        footer_tag="Gospel",
    )

    _add_marked_slide(prs, "Gospel Acclamation", GFCC.GOSPEL_END)
    _add_divider_cover(prs, **ctx)

    # ----- Creed -----
    _add_marked_slide_chunked(prs, "Nicene Creed", GFCC.CREED_1 + "\n" + GFCC.CREED_2 + "\n" + GFCC.CREED_3)
    _add_divider_cover(prs, **ctx)

    # ----- Prayer of the Faithful -----
    _add_marked_slide(prs, "Prayer of the Faithful", GFCC.PRAYER_FAITHFUL_1)
    _add_marked_slide(prs, "Prayer of the Faithful", GFCC.PRAYER_FAITHFUL_2)
    _add_divider_cover(prs, **ctx)

    # ----- Liturgy of the Eucharist -----
    _add_marked_slide_chunked(prs, "Liturgy of the Eucharist", GFCC.OFFERTORY_HYMN)
    _add_section_card(prs, "LITURGY OF\nTHE EUCHARIST", "Liturgy of the Eucharist")
    _add_marked_slide(prs, "Liturgy of the Eucharist", GFCC.PRAY_BRETHREN)
    _add_section_card(prs, "LITURGY OF\nTHE EUCHARIST", "Liturgy of the Eucharist")
    _add_marked_slide(prs, "Liturgy of the Eucharist", GFCC.PREFACE_DIALOGUE)
    _add_marked_slide(prs, "Liturgy of the Eucharist", GFCC.PREFACE_ACCLAIM)
    _add_marked_slide_chunked(prs, "Sanctus", GFCC.SANCTUS)
    _add_section_card(prs, "LITURGY OF\nTHE EUCHARIST", "Liturgy of the Eucharist")
    _add_marked_slide(prs, "The Eucharistic Prayer", GFCC.MYSTERY_FAITH)
    _add_section_card(prs, "LITURGY OF\nTHE EUCHARIST", "Liturgy of the Eucharist")
    _add_marked_slide(prs, "Great Amen", GFCC.GREAT_AMEN)
    _add_marked_slide(prs, "Our Father", GFCC.OUR_FATHER_KO_1)
    _add_marked_slide(prs, "Our Father", GFCC.OUR_FATHER_KO_2)
    _add_divider_cover(prs, **ctx)
    _add_marked_slide(prs, "The Communion Rite", GFCC.COMMUNION_RITE_DELIVER)
    _add_marked_slide(prs, "Sign of Peace", GFCC.SIGN_PEACE)
    _add_marked_slide(prs, "Lamb of God", GFCC.LAMB_OF_GOD)
    _add_marked_slide(prs, "The Communion Rite", GFCC.COMMUNION_DIALOGUE)
    _add_divider_cover(prs, **ctx)
    _add_marked_slide_chunked(prs, "Communion", GFCC.COMMUNION_HYMN)
    _add_marked_slide(prs, "The Communion Rite", GFCC.POST_COMMUNION)
    _add_divider_cover(prs, **ctx)

    # ----- Announcements -----
    _add_marked_slide(prs, "Announcements", GFCC.ANNOUNCEMENTS_TITLE)
    _add_marked_slide(prs, "Announcements", GFCC.WELCOME_NEWCOMERS)
    _add_marked_slide(prs, "Announcements", GFCC.CONFESSION_SLIDE)
    _add_marked_slide(prs, "Announcements", GFCC.COLLECTION_PLACEHOLDER)
    _add_marked_slide(prs, "Announcements", GFCC.SPONSORSHIP)
    _add_marked_slide(prs, "Announcements", GFCC.FB_UPDATES)

    # ----- Dismissal -----
    _add_marked_slide(prs, "Final Blessing", GFCC.FINAL_BLESSING)
    _add_marked_slide_chunked(prs, "Recessional", GFCC.RECESSIONAL_1 + "\n" + GFCC.RECESSIONAL_2)
    _add_divider_cover(prs, **ctx)

    if quote_attribution and (gospel_quote or "").strip():
        _add_marked_slide(prs, "Scripture note", f"<<D>>{quote_attribution}")

    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = _OUTPUT_DIR / "mass_presentation.pptx"
    prs.save(out_file)

    print(f"✅ PowerPoint created: {out_file}")
