import sys

from generators.powerpoint import generate_mass_ppt
from services.gospel_quote_extractor import (
    first_sentence_slide_quote,
    pick_sentence_interactive,
    split_slide_sentences,
)
from services.lectionary_service import get_liturgical_data

_PICK_SENTENCE_FLAGS = frozenset(("-p", "--pick-sentence"))
pick_sentence_mode = bool(_PICK_SENTENCE_FLAGS & set(sys.argv[1:]))

print("================================")
print("     CHURCH MEDIA GENERATOR     ")
print("================================")

# USER INPUT
date = input("Enter Mass Date (YYYY-MM-DD): ")
celebrant = input("Enter Celebrant Name: ")
# STEP 1 — GET LITURGICAL DATA
data = get_liturgical_data(date)

if data:

    title = data.get("title") or "Sunday Mass Celebration"
    gospel_ref = data.get("gospel_reference") or "N/A"
    gospel_text = data.get("gospel_text") or ""
    gospel_slide_quote = (data.get("gospel_slide_quote") or "").strip()
    season = data.get("season") or ""
    cycle = data.get("lectionary_cycle") or ""
    quote_attr = data.get("quote_attribution")

    print("\nGospel Reference:", gospel_ref)
    if cycle:
        print("Sunday Lectionary: Year", cycle)
    if season:
        print("Season:", season)

    base_quote = gospel_slide_quote or gospel_text or ""
    sentences = split_slide_sentences(base_quote)
    if pick_sentence_mode and len(sentences) > 1:
        slide_line = pick_sentence_interactive(sentences)
    else:
        slide_line = first_sentence_slide_quote(base_quote)

    if slide_line:
        print("\nSlide line:", slide_line)
    elif gospel_text:
        print("\nPreview (full excerpt):", gospel_text[:150], "...")
    else:
        print("\n⚠️ Gospel text not available.")

    # STEP 2 — GENERATE POWERPOINT
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
    )

    print("✅ PowerPoint Generated!")

else:
    print("❌ Unable to fetch liturgical data.")
