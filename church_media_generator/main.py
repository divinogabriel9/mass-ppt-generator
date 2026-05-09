import sys

from generators.poster_generator import generate_mass_poster
from generators.powerpoint import generate_mass_ppt
from services.gospel_quote_extractor import (
    first_sentence_slide_quote,
    pick_sentence_interactive,
    split_slide_sentences,
)
from services.liturgical_calendar import get_liturgical_color
from services.lectionary_service import get_liturgical_data

_PICK_SENTENCE_FLAGS = frozenset(("-p", "--pick-sentence"))
pick_sentence_mode = bool(_PICK_SENTENCE_FLAGS & set(sys.argv[1:]))

print("================================")
print("     CHURCH MEDIA GENERATOR     ")
print("================================")

# 1 Date
date = input("Enter Mass Date (YYYY-MM-DD): ")
# 2 Celebrant
celebrant = input("Enter Celebrant Name: ")

# 3 Liturgical data (includes readings + gospel text from API / USCCB)
data = get_liturgical_data(date)

if not data:
    print("❌ Unable to fetch liturgical data.")
    raise SystemExit(1)

title = data.get("title") or "Sunday Mass Celebration"
gospel_ref = data.get("gospel_reference") or "N/A"
gospel_text = data.get("gospel_text") or ""
gospel_slide_quote = (data.get("gospel_slide_quote") or "").strip()
season = data.get("season") or ""
cycle = data.get("lectionary_cycle") or ""
quote_attr = data.get("quote_attribution")

# 4 Gospel text (confirmed / preview)
print("\nGospel Reference:", gospel_ref)
if gospel_text:
    print("Gospel text loaded:", len(gospel_text), "characters.")
else:
    print("⚠️ Gospel full text not available; slides will show a fallback note.")

# 5 Liturgical color
liturgical_color = get_liturgical_color(date)
print(
    "Liturgical color:",
    liturgical_color["color_name"],
    f"({liturgical_color['season']})",
    liturgical_color["hex"],
)

# Short quote for title slide / poster context
base_quote = gospel_slide_quote or gospel_text or ""
sentences = split_slide_sentences(base_quote)
if pick_sentence_mode and len(sentences) > 1:
    slide_line = pick_sentence_interactive(sentences)
else:
    slide_line = first_sentence_slide_quote(base_quote)

if slide_line:
    print("Title / deck excerpt:", slide_line[:120] + ("…" if len(slide_line) > 120 else ""))

# 6 PowerPoint
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
)
print("✅ PowerPoint generated.")

# 7 Poster
poster_path = generate_mass_poster(
    title=title,
    gospel_reference=gospel_ref,
    celebrant=celebrant,
    date=date,
)
print(f"✅ Poster generated: {poster_path}")
