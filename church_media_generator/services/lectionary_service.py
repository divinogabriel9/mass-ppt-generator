import datetime as _dt

import requests

from core.liturgical_calendar import sunday_lectionary_cycle
from services.gospel_fallback import fetch_world_english_gospel, gospel_reference_looks_like_citation_only
from services.gospel_quote_extractor import extract_gospel_slide_quote
from services.usccb_scraper import fetch_gospel_text


def get_liturgical_data(date: str):
    """
    Fetch liturgical data from Catholic Readings API.
    date format: YYYY-MM-DD
    """

    try:
        on_date = _dt.datetime.strptime(date.strip(), "%Y-%m-%d").date()
    except ValueError:
        print("❌ Invalid date. Use YYYY-MM-DD.")
        return None

    lectionary_cycle = sunday_lectionary_cycle(on_date)

    year = date.split("-")[0]
    month_day = date[5:]

    url = f"https://cpbjr.github.io/catholic-readings-api/readings/{year}/{month_day}.json"

    print("Fetching:", url)

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:

            data = response.json()
            readings = data.get("readings", {})
            source_url = data.get("usccbLink", "")
            gospel_reference = readings.get("gospel", "") or ""
            gospel_text = ""
            quote_attribution = None

            if source_url:
                gospel_text = (fetch_gospel_text(source_url) or "").strip()

            if gospel_reference_looks_like_citation_only(gospel_reference, gospel_text):
                alt_text = fetch_world_english_gospel(gospel_reference)
                if alt_text:
                    gospel_text = alt_text
                    quote_attribution = (
                        "Below: World English Bible (WEB) fallback — verify NABRE on bible.usccb.org."
                    )
                else:
                    gospel_text = gospel_reference.strip()

            gospel_slide_quote = (
                extract_gospel_slide_quote(gospel_text, max_chars=300) if gospel_text else ""
            )

            return {
                "title": f"{data.get('season', 'Sunday Mass')} Celebration",
                "season": data.get("season", "Ordinary Time"),
                "lectionary_cycle": lectionary_cycle,
                "first_reading": readings.get("firstReading", ""),
                "psalm": readings.get("psalm", ""),
                "second_reading": readings.get("secondReading", ""),
                "gospel_reference": gospel_reference,
                "gospel_text": gospel_text,
                "gospel_slide_quote": gospel_slide_quote,
                "source": source_url,
                "quote_attribution": quote_attribution,
            }

        else:
            print(f"API Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"Connection Error: {e}")
        return None