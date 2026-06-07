# Claude Projects setup for playing Root by Leder Games

This repo contains scripts and files to help you setup a Project on claude.ai for learning and playing Root. It focuses on giving Claude access to the Law of Root, citing it in responses.


## Datasets

Two datasets:

- **`root_law.jsonl`** — 979 rule nodes scraped from [therootdatabase.com/law-of-root](https://www.therootdatabase.com/law-of-root/?q=&type=official), covering the Law of Root (all factions) and the Law of Rootbotics.
- **`root_cards.json`** — 361 cards extracted from the [LederCards/cards](https://github.com/LederCards/cards) GitHub repository, covering all expansions.

Schema references for both files live in `uploaded-files/` alongside the data.

## Claude.ai Project setup

### Upload files

Upload all files in `uploaded-files/` as Project knowledge:

| File | Contents |
|---|---|
| `root_law.jsonl` | Rule nodes (JSONL) |
| `root_law_schema.md` | Field reference + grep examples for the law data |
| `root_cards.json` | Card database (JSON) |
| `root_cards_schema.md` | Field reference + query examples for the card data |

### Set project instructions

Then paste the following as the **Project Instructions** on Claude.ai:

---

Always refer to the Law of Root to answer rules questions and check procedures. Be careful with wording: the specific terms used determine which rule applies where. Verify the terms you use are appropriate, and search the Law for the exact term.

Where to look (do NOT default to project_knowledge_search for rules):
- Rules / procedures → read or grep root_law.jsonl directly; cite the section id (e.g. 9.2.9.III.a) so every claim is checkable.
- Card text / properties → query root_cards.json directly.
- Fuzzy recall ("where did we discuss X", "what was that strategy") → project_knowledge_search.

root_law.jsonl mixes the Law of Root ("law": "official") and the Law of Rootbotics ("law": "rootbotics", bot logic). For human-play rules, filter to official. Bot faction names (Vagabot, Electric Eyrie, Mechanical Marquise 2.0, etc.) are automated opponents — distinct from the player factions of similar name.

See root_law_schema.md and root_cards_schema.md for field definitions and grep patterns.

---

## Refreshing the law data

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv run python scrape_law.py
```

Output is written to `uploaded-files/root_law.jsonl`. Re-upload to the Project after refreshing.

The card data (`root_cards.json`) is sourced from the [LederCards/cards](https://github.com/LederCards/cards) repo and updated manually.

## Dependencies

- `requests` — HTTP
- `lxml` — HTML parsing

## License

Data scraped from therootdatabase.com is owned by Leder Games. This repository contains only tooling and schema documentation — the data files are for personal/research use. Root is a trademark of Leder Games.
