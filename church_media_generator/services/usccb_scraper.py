import re

import requests
from bs4 import BeautifulSoup

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_gospel_text(usccb_url: str):
    """Extract Gospel body text from a USCCB daily readings HTML page."""

    try:
        response = requests.get(usccb_url, timeout=15, headers=_DEFAULT_HEADERS)

        if response.status_code != 200:
            print("❌ Failed to open USCCB page")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        gospel_header = None
        for h in soup.find_all(["h2", "h3", "h4"]):
            if "Gospel" in h.get_text():
                gospel_header = h
                break

        if not gospel_header:
            print("❌ Gospel section not found")
            return None

        # USCCB puts the verse under <p> tags that are NOT direct siblings of the heading.
        parts = []
        for p in gospel_header.find_all_next("p", limit=50):
            t = p.get_text(" ", strip=True)
            if not t:
                continue
            if "Copyright" in t or "Confraternity of Christian Doctrine" in t:
                break
            if re.match(r"^Get the Daily Readings", t, re.I):
                break
            if "USCCB" in t and len(t) < 160:
                break
            parts.append(t)

        if len(parts) == 0:
            addr = gospel_header.find_next("div", class_="address")
            if addr and addr.a and addr.a.get("href"):
                return _fetch_gospel_from_pericope(addr.a["href"])

            print("❌ Gospel paragraphs not found")
            return None

        return " ".join(parts)

    except Exception as e:
        print("Scrape error:", e)
        return None


def _fetch_gospel_from_pericope(href: str):
    """Fallback: follow the pericope link (e.g. .../bible/john/16?29)."""
    try:
        response = requests.get(href, timeout=15, headers=_DEFAULT_HEADERS)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        parts = []
        for p in soup.find_all("p", limit=45):
            t = p.get_text(" ", strip=True)
            if len(t) < 30:
                continue
            if "Copyright" in t or "USCCB" in t and len(t) < 200:
                break
            parts.append(t)
        return " ".join(parts) if parts else None
    except Exception:
        return None
