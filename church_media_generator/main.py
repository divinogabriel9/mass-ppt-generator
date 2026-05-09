import sys

from pipeline import generate_mass_media

_PICK_SENTENCE_FLAGS = frozenset(("-p", "--pick-sentence"))


def _argv_positional() -> list[str]:
    return [a for a in sys.argv[1:] if a not in _PICK_SENTENCE_FLAGS and not a.startswith("-")]


def _prompt_line(msg: str) -> str:
    print(msg, end="", flush=True)
    return input()


pick_sentence_mode = bool(_PICK_SENTENCE_FLAGS & set(sys.argv[1:]))

print("================================", flush=True)
print("     CHURCH MEDIA GENERATOR     ", flush=True)
print("================================", flush=True)

positional = _argv_positional()
if len(positional) >= 2:
    date, celebrant = positional[0], positional[1]
    print(f"Date: {date}\nCelebrant: {celebrant}\n", flush=True)
else:
    print(
        "Tip: run non-interactively — python3 main.py YYYY-MM-DD \"Celebrant Name\"\n",
        flush=True,
    )
    if len(positional) == 1:
        date = positional[0]
        celebrant = _prompt_line("Enter Celebrant Name: ")
    else:
        date = _prompt_line("Enter Mass Date (YYYY-MM-DD): ")
        celebrant = _prompt_line("Enter Celebrant Name: ")

print("Working: fetching readings and building PowerPoint + poster…", flush=True)

result = generate_mass_media(
    date,
    celebrant,
    interactive_pick=pick_sentence_mode,
)

if not result.ok:
    print("❌", result.error or "Generation failed.")
    raise SystemExit(1)

print("\nGospel Reference:", result.gospel_reference)
if result.gospel_text_length:
    print("Gospel text loaded:", result.gospel_text_length, "characters.")
else:
    print("⚠️ Gospel full text not available; slides will show a fallback note.")
if result.liturgical_color_name:
    print(
        "Liturgical color:",
        result.liturgical_color_name,
        f"({result.liturgical_season_label})" if result.liturgical_season_label else "",
        result.liturgical_color_hex,
    )
if result.slide_line_preview:
    print("Title / deck excerpt:", result.slide_line_preview)

print("✅ PowerPoint generated.")
print("✅ Poster generated:", result.poster_path)
