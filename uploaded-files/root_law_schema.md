# root_law.jsonl — Schema Reference

One JSON object per line. Every line is a self-contained rule node.

## Fields

| Field | Type | Description |
|---|---|---|
| `id` | string | Fully-qualified dotted section ID. Roman-numeral and letter levels are dot-separated: `9.2.9.III.a`. Rootbotics entries are prefixed `B.` (e.g., `B.11.1`). **Primary grep anchor.** |
| `title` | string | Section label (bold lead-in), e.g. `"Infamy"`. Never includes the ID itself. |
| `faction` | string \| null | Owning faction chapter (`"Vagabond"`, `"Marquise de Cat"`, …) or `null` for general rules. |
| `parent` | string \| null | `id` of the enclosing section — enables tree traversal. `null` for top-level nodes. |
| `level` | int | Nesting depth = number of dot-separated segments in `id`. |
| `refs` | string[] | Section IDs cited in `text`, normalized to dotted form (e.g. `["3.2.1", "9.2.9.III"]`). Best-effort — only ~57 of 979 nodes have it populated; grep `text` too if you need every cross-reference. |
| `glyphs` | string[] | Single uppercase letter glyphs found in `text` (`M`, `F`, `S`, `H`, etc.). |
| `text` | string | Cleaned rule text, excluding the title. |
| `law` | string | `"official"` (Law of Root) or `"rootbotics"` (Law of Rootbotics). |

## ID conventions

- Dotted numerics: `1.1.1`, `9.2.9`
- Roman-numeral sub-level: `9.2.9.III`
- Letter sub-level under roman: `9.2.9.III.a`

Numeric chapters `1`–`18` are the Law of Root's main chapters (`1` Golden Rules,
`2` Key Concepts, `3` Victory, `4` Key Actions, `5` Setup, `6`–`18` the factions).
Letter chapters are the appendices, named as on therootdatabase.com:

- `A.*` — Advanced Setup
- `C.*` — Components
- `G.*` — Glossary (e.g., `G.1`, `G.20`)
- `H.*` — Hirelings (e.g., `H.1`, `H.2.2`)
- `K.*` — Knave Captains
- `L.*` — Landmarks (only 2 nodes: `L.1.1`, `L.1.2` — the source chapter is that short)
- `M.*` — Maps
- `V.*` — Vagabonds
- `B.*` — Rootbotics, not an appendix: a synthetic prefix for the Law of Rootbotics
  (e.g., `B.11.1` Cogwheel Corvids section 11.1)

## Grep examples

```bash
# Exact section lookup
grep '"id": "9.2.9.III.a"' root_law.jsonl

# All Vagabond rules
grep '"faction": "Vagabond"' root_law.jsonl

# Sections that reference 3.2.1
grep '"3.2.1"' root_law.jsonl

# All Rootbotics entries
grep '"law": "rootbotics"' root_law.jsonl

# Keyword search with context
grep -i 'hostile' root_law.jsonl | jq .id
```

## Source

Scraped from `https://www.therootdatabase.com/law-of-root/?q=&type=official`
using `scrape_law.py` (repeatable; re-run to refresh).

Last scraped: 2026-06-07
