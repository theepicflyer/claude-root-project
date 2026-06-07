# root-law-scraper

## Project layout

```
uploaded-files/          # Files to upload as Claude.ai Project knowledge
  root_law.jsonl         # 979 rule nodes (JSONL)
  root_law_schema.md     # Schema reference for root_law.jsonl
  root_cards.json        # 361 cards (JSON envelope: {game, source, total_cards, cards})
  root_cards_schema.md   # Schema reference for root_cards.json
scrape_law.py            # Scraper — outputs to uploaded-files/root_law.jsonl
build_cards.py           # Card builder — outputs to uploaded-files/root_cards.json
vendor/cards/            # Pinned LederCards/cards submodule (card source data)
pyproject.toml
```

## Running

```bash
uv run python scrape_law.py    # rebuild root_law.jsonl  (scrapes therootdatabase.com)
uv run python build_cards.py   # rebuild root_cards.json (reads vendor/cards submodule)
```

`scrape_law.py` is a polite scraper (0.4 s delay per chapter) and spot-checks canonical IDs on exit. `build_cards.py` reads the pinned `vendor/cards` submodule and spot-checks card count / unmapped categories on exit — run `git submodule update --init vendor/cards` first if the submodule is empty. To advance the source: `git submodule update --remote vendor/cards`, rebuild, then commit both the submodule pointer and the regenerated JSON.

## Data notes

**root_law.jsonl** — scraped from therootdatabase.com. Each line is one rule node. Key field: `id` (dotted section ID, e.g. `9.2.9.III.a`). Rootbotics entries are prefixed `B.`. `refs` is best-effort (~57/979 nodes populated).

**root_cards.json** — built by `build_cards.py` from the pinned `vendor/cards` submodule. Top-level is an envelope; cards live under `data["cards"]`. `expansion` is the LederCards source-file grouping (derived from `source_file`), **not** the physical product box. Usually it's the faction's origin expansion, but cross-cutting cards are inconsistent in the source: ROOT-167/170 (Lizard Cult / Riverfolk Company Advanced Setup) are filed by faction → `Riverfolk Expansion`, while ROOT-165 (Eyrie Advanced Setup) is filed by box → `Marauders Expansion`, though both ship in the Marauder box. Box data isn't modeled; raw hints survive in `tags`.

See the `*_schema.md` files for full field references and query examples.

## Dependencies

Managed with uv. Add packages with `uv add <package>`, not pip.
