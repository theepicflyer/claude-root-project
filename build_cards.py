"""
Build uploaded-files/root_cards.json from the pinned LederCards/cards submodule.

Reads the Root card YAML under vendor/cards/content/card-data/root/en-US/,
normalizes each card to the schema in root_cards_schema.md, and writes a single
JSON envelope.

Run with: uv run python build_cards.py

To refresh the source data:
    git submodule update --remote vendor/cards   # advance to upstream HEAD
    uv run python build_cards.py                  # rebuild root_cards.json
    git add vendor/cards uploaded-files/root_cards.json && git commit

`expansion` is the LederCards source-file grouping (derived purely from the
source filename), NOT the physical product box. It is usually the faction's
origin expansion, but the source is internally inconsistent for cross-cutting
cards: ROOT-167/170 (Lizard Cult / Riverfolk Company Advanced Setup) are filed
by faction (riverfolk-hirelings -> Riverfolk), while ROOT-165 (Eyrie Advanced
Setup) is filed by box (marauders-hirelings -> Marauders), even though all of
them ship in the Marauder box. We take the file grouping verbatim and ignore
the partial `Marauders` tags on 167/170 (the source applied them to only some
of the cards that ship in that box). Raw tags are preserved in `tags`.
"""

import json
import sys
from pathlib import Path

import yaml

REPO_URL = "https://github.com/LederCards/cards"
CARD_DIR = Path(__file__).parent / "vendor/cards/content/card-data/root/en-US"
OUT_PATH = "uploaded-files/root_cards.json"

SUITS = {"Bird", "Fox", "Mouse", "Frog"}
BUNNY_SUITS = {"Bunny", "Rabbit"}
DECK_TAGS = {"Standard Deck", "Exiles & Partisans Deck", "Squires & Disciples Deck"}

# Source filename → its LederCards expansion grouping (usually faction origin).
EXPANSION_BY_FILE = {
    "rootbasegame": "Base Game",
    "exiles-partisans": "Exiles & Partisans Deck",
    "riverfolk": "Riverfolk Expansion",
    "riverfolk-hirelings": "Riverfolk Expansion",
    "underworld": "Underworld Expansion",
    "underworld-hirelings": "Underworld Expansion",
    "marauders": "Marauders Expansion",
    "marauders-hirelings": "Marauders Expansion",
    "homeland": "Homeland Expansion",
    "homeland-hirelings": "Homeland Expansion",
    "vagabonds": "Vagabond Pack",
    "clockwork1": "Clockwork Expansion",
    "clockwork2": "Clockwork Expansion",
    "landmarks": "Landmarks",
    "squires-disciples": "Squires & Disciples Deck",
}


def derive_category(card: dict, tags: set[str]) -> str:
    name = card.get("name", "")
    if "Hirelings" in tags:
        return "hireling"
    if "Clockwork" in tags:
        if "Vagabot" in name or any(
            x in name
            for x in (
                "Ranger (Vagabot)", "Tinker (Vagabot)", "Theif (Vagabot)",
                "Arbiter (Vagabot)", "Vagrant (Vagabot)", "Scoundrel (Vagabot)",
            )
        ):
            return "clockwork_bot"
        if any(
            x in name
            for x in ("Basic Services", "Advanced Services", "Introduction", "Interactions")
        ):
            return "clockwork_reference"
        return "clockwork_trait"
    if "ADSET" in tags or "Advanced Setup" in tags:
        return "advanced_setup"
    if "Learn to Play" in tags:
        return "learn_to_play"
    if "Clarification" in tags:
        return "clarification"
    if "Landmark" in tags or "Landmarks" in tags:
        return "landmark"
    if "Quest" in tags:
        return "quest"
    if "Mechanical Marquise 1.0" in tags:
        return "mechanical_marquise"
    if "Eyrie" in tags:
        return "eyrie_leader"
    if "Moles" in tags:
        return "duchy_minister"
    if "Rats" in tags:
        return "mood"
    if "Captain" in tags:
        return "homeland_captain"
    if "Frog" in tags and "Craftable" not in tags:
        return "homeland_frog"
    if name in ("Ambush!", "Ambush"):
        return "ambush"
    if name == "Dominance":
        return "dominance"
    if "Craftable" in tags:
        return "craft_card"
    if "Vagabond" in tags:
        return "vagabond_role"
    if "Marauder" in tags or "Marauders" in tags:
        return "faction_card"
    return "other"


def build_card(raw: dict, src: str) -> dict:
    tags = raw.get("tags", [])
    tags_set = set(tags)

    suit = None
    for t in tags:
        if t in BUNNY_SUITS:
            suit = "Rabbit"
            break
        if t in SUITS:
            suit = t
            break

    return {
        "id": raw["id"],
        "numeric_id": int(raw["id"].replace("ROOT-", "")),
        "name": raw.get("name", ""),
        "text": raw.get("text") or None,
        "image": raw.get("image", ""),
        "suit": suit,
        "deck": next((t for t in tags if t in DECK_TAGS), None),
        "craftable": "Craftable" in tags_set,
        "category": derive_category(raw, tags_set),
        "expansion": EXPANSION_BY_FILE.get(src),
        "source_file": src,
        "tags": tags,
    }


def main() -> None:
    if not CARD_DIR.is_dir():
        sys.exit(
            f"Card source not found at {CARD_DIR}.\n"
            "Initialize the submodule first: git submodule update --init vendor/cards"
        )

    all_cards: list[dict] = []
    for filepath in sorted(CARD_DIR.glob("*.yml")):
        src = filepath.stem
        cards = yaml.safe_load(filepath.read_text()) or []
        for raw in cards:
            all_cards.append(build_card(raw, src))
        print(f"  {src}: {len(cards)} cards", file=sys.stderr)

    all_cards.sort(key=lambda c: c["numeric_id"])
    output = {
        "game": "Root",
        "source": REPO_URL,
        "total_cards": len(all_cards),
        "cards": all_cards,
    }
    Path(OUT_PATH).write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"\nWrote {len(all_cards)} cards to {OUT_PATH}", file=sys.stderr)

    # Spot-checks
    others = [c["id"] for c in all_cards if c["category"] == "other"]
    print(f"  category 'other': {len(others)} {others}", file=sys.stderr)
    unmapped = [c["id"] for c in all_cards if c["expansion"] is None]
    print(f"  expansion unmapped: {len(unmapped)} {unmapped}", file=sys.stderr)
    for cid in ("ROOT-167", "ROOT-170"):
        c = next(c for c in all_cards if c["id"] == cid)
        print(f"  {cid}: expansion={c['expansion']!r}", file=sys.stderr)


if __name__ == "__main__":
    main()
