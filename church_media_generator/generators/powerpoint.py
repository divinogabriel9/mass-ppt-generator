from pathlib import Path

from pptx import Presentation

# Always write beside the repo root (`church_media_generator/`), regardless of cwd.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_OUTPUT_DIR = _PROJECT_ROOT / "outputs"


def generate_mass_ppt(
    title,
    gospel_reference,
    gospel_quote,
    season,
    lectionary_cycle,
    celebrant,
    date,
    quote_attribution=None,
    quote_max_chars=480,
):
    prs = Presentation()

    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)

    slide.shapes.title.text = title or "Mass"

    ref = (gospel_reference or "").strip() or "—"
    body_lines = [f"Gospel: {ref}", ""]

    quote = (gospel_quote or "").strip()
    if quote:
        q = quote if len(quote) <= quote_max_chars else quote[: quote_max_chars - 1].rstrip() + "…"
        body_lines.append(q)
    else:
        body_lines.append(
            "Gospel text was not available from the automatic fetch. "
            "Open today’s readings on bible.usccb.org and paste the Gospel into the deck if needed."
        )

    if quote_attribution and quote.strip():
        body_lines.extend(["", str(quote_attribution).strip()])

    season_line = (season or "").strip() or "—"
    cycle_letter = (lectionary_cycle or "").strip().upper() or "—"
    body_lines.extend(
        [
            "",
            f"Sunday Lectionary: Year {cycle_letter}",
            f"Liturgical season: {season_line}",
            "",
            f"Celebrant: {celebrant}",
            f"Date: {date}",
        ]
    )

    slide.placeholders[1].text = "\n".join(body_lines)

    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = _OUTPUT_DIR / "mass_presentation.pptx"
    prs.save(out_file)

    print(f"✅ PowerPoint created: {out_file}")
