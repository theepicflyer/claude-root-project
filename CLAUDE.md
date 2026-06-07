# root-law-scraper

## Project layout

```
uploaded-files/          # Files to upload as Claude.ai Project knowledge
  root_law.jsonl         # 979 rule nodes (JSONL)
  root_law_schema.md     # Schema reference for root_law.jsonl
  root_cards.json        # 361 cards (JSON envelope: {game, source, total_cards, cards})
  root_cards_schema.md   # Schema reference for root_cards.json
scrape_law.py            # Scraper — outputs to uploaded-files/root_law.jsonl
pyproject.toml
```

## Running

```bash
uv run python scrape_law.py
```

Writes to `uploaded-files/root_law.jsonl`. Polite scraper (0.4 s delay per chapter). Spot-checks a handful of canonical IDs on exit.

## Data notes

**root_law.jsonl** — scraped from therootdatabase.com. Each line is one rule node. Key field: `id` (dotted section ID, e.g. `9.2.9.III.a`). Rootbotics entries are prefixed `B.`. `refs` is best-effort (~57/979 nodes populated).

**root_cards.json** — sourced from LederCards/cards GitHub repo, updated manually. Top-level is an envelope; cards live under `data["cards"]`. `set` field usually mirrors `expansion` but has 2 known exceptions (ROOT-167, ROOT-170) — prefer `expansion`.

See the `*_schema.md` files for full field references and query examples.

## Dependencies

Managed with uv. Add packages with `uv add <package>`, not pip.
