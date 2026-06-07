"""
Scrape therootdatabase.com/law-of-root and emit root_law.jsonl.

Each line is a JSON object matching the schema in root_law_schema.md.
Run with: uv run python scrape_law.py

Rootbotics chapters reuse the same section numbers as base-law chapters
(e.g., both Riverfolk Company and Cogwheel Corvids are "section 11").
To keep IDs grep-unique, Rootbotics IDs are prefixed with "B."
(e.g., "B.11.1" for Cogwheel Corvids 11.1).
"""

import json
import re
import sys
import time

import requests
from lxml import html as lxml_html

BASE = "https://www.therootdatabase.com"

# Maps URL slug → faction name (None = general/shared rules)
SLUG_TO_FACTION: dict[str, str | None] = {
    # Base Law of Root
    "golden-rules": None,
    "key-concepts": None,
    "victory": None,
    "key-actions": None,
    "setup": None,
    "vagabonds": None,
    "hirelings": None,
    "landmarks": None,
    "maps": None,
    "advanced-setup": None,
    "components": None,
    "glossary": None,
    "marquise-de-cat": "Marquise de Cat",
    "eyrie-dynasties": "Eyrie Dynasties",
    "woodland-alliance": "Woodland Alliance",
    "vagabond": "Vagabond",
    "riverfolk-company": "Riverfolk Company",
    "the-lizard-cult": "Lizard Cult",
    "underground-duchy": "Underground Duchy",
    "corvid-conspiracy": "Corvid Conspiracy",
    "lord-of-the-hundreds": "Lord of the Hundreds",
    "keepers-in-iron": "Keepers in Iron",
    "lilypad-diaspora": "Lilypad Diaspora",
    "twilight-council": "Twilight Council",
    "knaves-of-the-deepwood": "Knaves of the Deepwood",
    "knave-captains": "Knave Captains",
    # Law of Rootbotics (general)
    "changes-to-the-law": None,
    "new-rules": None,
    "setup-with-bots": None,
    "map-interactions": None,
    # Law of Rootbotics (factions)
    "mechanical-marquise-20": "Mechanical Marquise 2.0",
    "electric-eyrie": "Electric Eyrie",
    "automated-alliance": "Automated Alliance",
    "vagabot": "Vagabot",
    "logical-lizards": "Logical Lizards",
    "drillbit-duchy": "Drillbit Duchy",
    "cogwheel-corvids": "Cogwheel Corvids",
    "riverfolk-robots": "Riverfolk Robots",
}

# Roman numeral + optional letter: e.g. "IIIa" → normalize to "III.a"
_ROMAN_LETTER = re.compile(r"^(.+)\.([IVXLCDM]+)([a-z]+)$")


def normalize_id(raw: str, prefix: str = "") -> str:
    """Insert dot between roman numeral and trailing letter(s), apply prefix.

    normalize_id("9.2.9.IIIa") → "9.2.9.III.a"
    normalize_id("11.1", "B.") → "B.11.1"
    """
    m = _ROMAN_LETTER.match(raw)
    if m:
        base = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
    else:
        base = raw
    return prefix + base


def compute_parent(nid: str) -> str | None:
    parts = nid.split(".")
    return ".".join(parts[:-1]) if len(parts) > 1 else None


# Section references like (3.1), (9.2.9.IIIa), (H.2.2)
_REF_PAT = re.compile(r"\(([0-9A-Z][0-9.]*(?:[IVXLCDM]+[a-z]*)?)\)")
# Single uppercase letter glyphs (M F S H R X B T C etc.)
_GLYPH_PAT = re.compile(r"\b([MFSRHXBTC])\b")


def extract_refs(text: str) -> list[str]:
    seen: dict[str, None] = {}
    for m in _REF_PAT.finditer(text):
        nid = normalize_id(m.group(1))
        seen[nid] = None
    return list(seen)


def extract_glyphs(text: str) -> list[str]:
    seen: dict[str, None] = {}
    for m in _GLYPH_PAT.finditer(text):
        seen[m.group(1)] = None
    return list(seen)


def header_title(el) -> str:
    """Extract normalized title from a header element.

    "9.4 BIRDSONG"  → "Birdsong"
    "Crafting."     → "Crafting"
    """
    raw = "".join(el.itertext()).strip()
    # Strip leading section-number prefix (e.g. "9.4 ", "G.1 ", "1. ")
    raw = re.sub(r"^[0-9A-Z][0-9A-Z.]*\s+", "", raw)
    # Strip trailing period
    raw = raw.rstrip(".")
    # Normalize ALL CAPS to Title Case
    return raw.title() if raw.isupper() else raw


def parse_entry(text_link: str, header_row, id_prefix: str) -> dict | None:
    """Parse a text data-link + its section header row into a rule record.

    header_row: the immediate div containing both the section heading and the
                copy icons — scoped to THIS section only, not nested children.
    id_prefix:  "" for base law, "B." for Rootbotics.
    """
    m = re.match(r"^> (\S+) - (.+)$", text_link, re.DOTALL)
    if not m:
        return None

    raw_id = m.group(1)
    rest = m.group(2).strip()

    # Derive the title from the HTML header in this section's header row.
    # Searching within header_row avoids picking up headers from nested sections.
    title = ""
    if header_row is not None:
        for tag in ("h2", "h3", "h4", "h5", "h6", "strong"):
            candidates = header_row.xpath(f".//{tag}")
            if candidates:
                candidate = header_title(candidates[0])
                if candidate:
                    title = candidate
                    break

    if title:
        # Strip the title prefix from the data-link text to get the body.
        # Handles both "Title. Body" and "Title Body" (no period separator).
        after = rest[len(title):]
        text = after.lstrip(". ").strip()
        if not text:
            text = rest  # title == body (no separate body sentence)
    else:
        # Fallback: split on first '. ' (period-space).
        if ". " in rest:
            title, text = rest.split(". ", 1)
            title = title.rstrip(".")
        else:
            text = rest

    norm_id = normalize_id(raw_id, id_prefix)
    return {
        "id": norm_id,
        "title": title,
        "faction": None,  # filled in by caller
        "parent": compute_parent(norm_id),
        "level": len(norm_id.split(".")),
        "refs": extract_refs(text),
        "glyphs": extract_glyphs(text),
        "text": text,
    }


SESSION = requests.Session()
SESSION.headers["User-Agent"] = "root-law-scraper/1.0 (personal research)"


def fetch(url: str) -> str:
    resp = SESSION.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def get_slug_lists() -> tuple[list[str], list[str]]:
    """Return (base_law_slugs, rootbotics_slugs) in page order."""
    html = fetch(f"{BASE}/law-of-root/?q=&type=official")
    bots_pos = html.find("Law of Rootbotics")
    base_html = html[:bots_pos]
    bots_html = html[bots_pos:]
    slug_pat = re.compile(r'href="/law/([^/]+)/en/\?highlight_law=\d+"')
    base_slugs = list(dict.fromkeys(slug_pat.findall(base_html)))
    bots_slugs = list(dict.fromkeys(slug_pat.findall(bots_html)))
    return base_slugs, bots_slugs


def scrape_chapter(
    slug: str, faction: str | None, law: str, id_prefix: str
) -> list[dict]:
    url = f"{BASE}/law/{slug}/en/"
    print(f"  fetching {url}", file=sys.stderr)
    html_text = fetch(url)
    tree = lxml_html.fromstring(html_text)

    entries = []
    copy_icons = tree.xpath('//i[contains(@class,"bi-copy") and @data-link]')

    for icon in copy_icons:
        text_link = icon.get("data-link", "")
        if not text_link.startswith(">"):
            continue

        # Walk up to find:
        #   header_row — the innermost div holding both the section heading
        #                 and the copy icons (scoped to THIS section only)
        #   law_div    — the enclosing div[id^='law-']
        header_row = None
        law_div = None
        el = icon.getparent()
        while el is not None:
            el_id = el.get("id", "")
            if el_id.startswith("law-"):
                law_div = el
                break
            if el.tag == "div" and "justify-content-between" in el.get("class", ""):
                header_row = el
            el = el.getparent()

        if law_div is None:
            continue

        entry = parse_entry(text_link, header_row, id_prefix)
        if entry is None:
            continue

        entry["faction"] = faction
        entry["law"] = law
        entries.append(entry)

    return entries


def main() -> None:
    base_slugs, bots_slugs = get_slug_lists()
    print(
        f"Found {len(base_slugs)} base-law chapters, "
        f"{len(bots_slugs)} Rootbotics chapters",
        file=sys.stderr,
    )

    all_entries: list[dict] = []
    seen_ids: set[str] = set()

    chapters = (
        [(s, "official", "") for s in base_slugs]
        + [(s, "rootbotics", "B.") for s in bots_slugs]
    )

    for slug, law, id_prefix in chapters:
        if slug not in SLUG_TO_FACTION:
            print(f"  SKIP unknown slug '{slug}'", file=sys.stderr)
            continue
        faction = SLUG_TO_FACTION[slug]
        print(
            f"Scraping '{slug}' (law={law}, faction={faction!r})...",
            file=sys.stderr,
        )
        entries = scrape_chapter(slug, faction, law, id_prefix)
        added = 0
        for entry in entries:
            if entry["id"] not in seen_ids:
                all_entries.append(entry)
                seen_ids.add(entry["id"])
                added += 1
        print(f"  → {len(entries)} scraped, {added} new", file=sys.stderr)
        time.sleep(0.4)

    out_path = "uploaded-files/root_law.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for entry in all_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(all_entries)} entries to {out_path}", file=sys.stderr)

    # Spot-check canonical IDs — each should appear exactly once
    with open(out_path) as f:
        lines = f.readlines()
    for check_id in ("9.2.9.III.a", "3.2.1", "1.1.1", "G.1", "B.11.1"):
        hits = [l for l in lines if f'"id": "{check_id}"' in l]
        status = "OK" if len(hits) == 1 else f"WARN ({len(hits)} hits)"
        print(f"  spot-check {check_id!r}: {status}", file=sys.stderr)


if __name__ == "__main__":
    main()
